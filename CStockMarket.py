import math
import os.path

import CMarket
import requests
import pandas as pd
import datetime
import time
import CStrategy as strate
import CTools as ctools
import CTushare as cts
import Constants
from CMacdBbiCase import CMacdBbiCase
from CCommon import log, warning, error


class CStockMarket(CMarket.CMarket):
    def __init__(self):
        super().__init__()
        self.cts = cts.CTushare()
        self.strate = strate.CStrategy()
        self.tools = ctools.CTools()

        self.amprepare = self.configs.getModeulConfig('stockmarket', 'amprepare')
        self.pmprepare = self.configs.getModeulConfig('stockmarket', 'pmprepare')
        self.ambegin = self.configs.getModeulConfig('stockmarket', 'ambegin')
        self.amend = self.configs.getModeulConfig('stockmarket', 'amend')
        self.pmbegin = self.configs.getModeulConfig('stockmarket', 'pmbegin')
        self.pmend = self.configs.getModeulConfig('stockmarket', 'pmend')
        self.dayworkbegintime = self.configs.getModeulConfig('daywork', 'begin')
        self.dayworkendtime = self.configs.getModeulConfig('daywork', 'end')

        self.url = 'http://hq.sinajs.cn/list='
        self.headers = {'Accept': '/',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                        # 'Connection': 'keep-alive',
                        'Connection': 'close',
                        'Content-Length': '129',
                        'Content-Type': 'text/plain; charset=UTF-8',
                        'Cookie': 'ASP.NET_SessionId=vdl5ooxkjkazwszgvj5woewh',
                        'Referer': 'https://finance.sina.com.cn',
                        }

    def timeCmp(self, tm1, tm2):
        return int(time.strftime("%H%M%S", tm1)) - int(time.strftime("%H%M%S", tm2))

    def isTradeTime(self):
        t1 = self.timeCmp(time.localtime(time.time()), time.strptime(self.ambegin, "%H:%M:%S"))
        t2 = self.timeCmp(time.strptime(self.amend, "%H:%M:%S"), time.localtime(time.time()))
        t3 = self.timeCmp(time.localtime(time.time()), time.strptime(self.pmbegin, "%H:%M:%S"))
        t4 = self.timeCmp(time.strptime(self.pmend, "%H:%M:%S"), time.localtime(time.time()))
        # if (t1 > 0 and t4 > 0):
        #     return True
        if t1 >= 0 and t2 >= 0:
            return True
        elif t3 >= 0 and t4 >= 0:
            return True
        return False

    def isDayWork(self):
        t1 = self.timeCmp(time.localtime(time.time()), time.strptime(self.dayworkbegintime, "%H:%M:%S"))
        t2 = self.timeCmp(time.strptime(self.dayworkendtime, "%H:%M:%S"), time.localtime(time.time()))
        if t1 > 0 and t2 > 0:
            return True

    def isPrepareTime(self):
        t1 = self.timeCmp(time.localtime(time.time()), time.strptime(self.amprepare, "%H:%M:%S"))
        t2 = self.timeCmp(time.strptime(self.ambegin, "%H:%M:%S"), time.localtime(time.time()))
        t3 = self.timeCmp(time.localtime(time.time()), time.strptime(self.pmprepare, "%H:%M:%S"))
        t4 = self.timeCmp(time.strptime(self.pmbegin, "%H:%M:%S"), time.localtime(time.time()))
        if (t1 >= 0 and t2 >= 0) or (t3 >= 0 and t4 >= 0):
            return True
        return False

    def run(self):
        # 获取需要监控的个股
        date = self.cts.getPreTradeDate()
        case = CMacdBbiCase()
        df = case.getPredictData(date)
        # df = case.getPredictData(20241227)

        while True:
            print('======================================')
            if self.isTradeTime():
                log(f'数据监控中')
                self.fight_macdbbi(df, date)
            else:
                countdate = datetime.datetime.now().strftime('%Y-%m-%d')
                counttime = datetime.datetime.now().strftime('%H:%M:%S')
                print(f'{countdate} {counttime}')

            if self.isPrepareTime():
                time.sleep(1)
            else:
                time.sleep(8)

    def fight_macdbbi(self, df, date):
        if not df is None and df.shape[0] > 0:
            dk = self.getStocksRealPrices(df)
            if not dk is None and dk.shape[0] > 0:
                dk['code'] = dk['code'].apply(lambda x: x + '.SH' if x.startswith('6') else x + '.SZ')
                dbnew = pd.merge(df, dk[['code', 'price', 'done_num', 'name']], how='left', left_on=['ts_code'],
                                 right_on=['code'])

                fname = f'{self.stockTempPath}fake_buy_{self.cts.getLastTradeDate()}.csv'
                if os.path.exists(fname):
                    dbold = pd.read_csv(fname)
                    dbnew['close'] = dbold['close']
                dbnew['vol'] = dbnew.apply(lambda x: self.calVolRate(x), axis=1)
                dbnew['close'] = dbnew.apply(lambda x: self.calClose(x), axis=1)
                dbnew['succeed'] = dbnew.apply(lambda x: self.calRate(x), axis=1)
                dbnew.to_csv(fname, index=False)
                dbnewshow = dbnew.drop(
                    columns=['vol0', 'rate0', 'vol1', 'rate1', 'vol2', 'rate2', 'vol3', 'rate3', 'vol4', 'rate4',
                             'code'])
                income = dbnewshow.apply(
                    lambda x: round((float(x.price) - float(x.close)) / float(x.close), 4) if float(x.close) > 0 else 0,
                    axis=1)
                dbnewshow.insert(loc=7, column='income', value=income)
                print(dbnewshow.query('succeed > 0').sort_values(by='succeed', ascending=False))

    def calClose(self, row):
        if float(row.close >= float(row.preclose)) and float(row.vol) >= 3.0:
            return row.close
        else:
            return row.price

    def calVolRate(self, row):
        if float(row.close) < float(row.preclose):
            return 0
        if row.done_num >= row.vol4:
            return 4
        elif row.done_num >= row.vol3:
            return 3
        elif row.done_num >= row.vol2:
            return 2
        elif row.done_num >= row.vol1:
            return 1
        else:
            return 0

    def calRate(self, row):
        if float(row.close) < float(row.preclose):
            return 0
        if row.done_num >= row.vol4:
            return row.rate4
        elif row.done_num >= row.vol3:
            return row.rate3
        elif row.done_num >= row.vol2:
            return row.rate2
        elif row.done_num >= row.vol1:
            return row.rate1
        else:
            return row.rate0

    def getStocksRealPrices(self, df):
        tl = int(df.shape[0] / 300) + 1
        total = None
        for m in range(0, tl):
            codes = self.getRequestCodes(df, m)
            result = self.GetRealPrices2(codes)
            if total is None:
                total = result
            else:
                total = pd.concat([total, result], ignore_index=True, axis=0)
        return total

    def getRequestCodes(self, data, index=0):
        ret = ''
        star = index * 300 + 0
        end = star + 300
        for idx, row in data[star:end].iterrows():
            ret = ret + row['ts_code'] + ','
        return ret

    def GetRealPrices2(self, codes):
        src = codes.split(',')
        sp = self.url
        t = ''
        for stritem in src:
            if len(stritem) == 0:
                continue
            s1 = stritem.lower().split('.')
            if len(s1) < 2:
                t = s1[0]
                break
            t = t + s1[1] + s1[0] + ','
        sp = sp + t
        r = requests.get(sp, headers=self.headers)
        r.encoding = 'gbk'
        cols = ['levelW', 'level', 'code', 'name', 'open', 'close', 'price', 'high', 'low', 'buy', 'sell',
                'done_num', 'done_money', 'date', 'time']
        ret = pd.DataFrame(columns=cols, index=[])
        for retstr in r.text.split(';'):
            if (len(retstr) < 5):
                continue
            p1 = retstr.index("\"") + 1
            p2 = retstr.rindex("\"") - 1

            if p2 > p1:
                db = retstr[p1:p2].split(',')
                if (p1 == 21):
                    code = str(retstr[13:19])
                else:
                    code = str(retstr[14:20])

                if (float(db[1]) == 0):
                    level = 1
                    levelW = 1
                else:
                    level = round((float(db[3]) - float(db[2])) / float(db[2]), 4)
                    levelW = round((float(db[3]) - float(db[1])) / float(db[1]), 4)

                ret.loc[len(ret)] = [levelW, level, code, db[0], db[1], db[2], db[3], db[4], db[5], db[6],
                                     db[7],
                                     int(int(db[8]) / 100), round(float(db[9]) / 100000000, 2), db[30], db[31]]

        return ret

    # 更新个股资金流向
    def updateStockMoneyFlow(self, date=None):
        self.cts.updateStockMoneyFlow2(date)

    # 官方不披露北向资金，已经没用了
    def updateMoneyFlowHSGT(self):
        now = datetime.datetime.now().strftime('%Y%m%d')
        start = self.tools.getDateDelta(now, -Constants.ONE_YEARE_DAYS)
        self.cts.updateMoneyFlowHSGT(start, now)
