import os.path

import CMarket
import requests
import pandas as pd
import datetime
import time
import CStrategy as strate
import CTools as ctools
import CTushare as cts
from CDayWork import CDayWork
from CCommon import log, warning, error
from CMacdBbiCase import CMacdBbiCase
from CRealData import CRealData
from ClsMThreadPool import ClsMTPool


class CStockMarket(CMarket.CMarket):
    def __init__(self, fntrigger=None):
        super().__init__()
        self.cts = cts.CTushare()
        self.strate = strate.CStrategy()
        self.tools = ctools.CTools()
        self.mttool = ClsMTPool.Create()
        self.realdata = CRealData.create(fntrigger)

        self.amprepare = self.configs.getModeulConfig('stockmarket', 'amprepare')
        self.pmprepare = self.configs.getModeulConfig('stockmarket', 'pmprepare')
        self.ambegin = self.configs.getModeulConfig('stockmarket', 'ambegin')
        self.amend = self.configs.getModeulConfig('stockmarket', 'amend')
        self.pmbegin = self.configs.getModeulConfig('stockmarket', 'pmbegin')
        self.pmend = self.configs.getModeulConfig('stockmarket', 'pmend')
        self.dayworkbegintime = self.configs.getModeulConfig('daywork', 'begin')
        self.dayworkendtime = self.configs.getModeulConfig('daywork', 'end')
        self.dayworkflag = False
        self.exitflag = False
        self.isReplay = False
        self.minutepath = self.configs.getDataConfig('local', 'minutepath')

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

    def isDayworkTime(self):
        if self.dayworkflag:
            return False
        else:
            t1 = self.timeCmp(time.localtime(time.time()), time.strptime(self.dayworkbegintime, "%H:%M:%S"))
            t2 = self.timeCmp(time.strptime(self.dayworkendtime, "%H:%M:%S"), time.localtime(time.time()))
            if t1 > 0 and t2 > 0:
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
        self.mttool.add(self.monitor, ())

    def endtriiger(self, flag):
        self.exitflag = flag

    # 打印空闲时间信息
    def printEmptyTime(self):
        countdatetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{countdatetime}')

    # 实时板块统计
    # def runStockIndexStat(self, date, index='N'):
    #     # 概念成分
    #     dfIndex = self.cts.getIndexTHS(index)
    #     # 当前实时数据
    #     # alldf = self.realdata.pull()
    #     alldf = pd.read_csv(f'data/minute/{date}/14_57.csv', dtype={'code': str})
    #     alldf['code'] = alldf.apply(lambda x: self.tools.getBackCode(x.code), axis=1)
    #     db_all = alldf[['code', 'level']]
    #     dfIndex['level'] = dfIndex.apply(self.calLevel, db_all=db_all, axis=1)
    #     db = dfIndex.query('level != 0')[['ts_code', 'level', 'count', 'name']]
    #     db.sort_values(by='level', ascending=False, inplace=True)
    #     # print(db)
    #     return db

    # def calLevel(self, row, db_all):
    #     fname = f'{self.cts.ths_member}{row.ts_code}.csv'
    #     perlevel = 0
    #     if os.path.exists(fname):
    #         dk = pd.read_csv(fname)
    #         dk = pd.merge(dk, db_all, how='inner', left_on='con_code', right_on='code')
    #         if dk.shape[0] > 0:
    #             perlevel = round(dk['level'].mean(), 4)
    #         else:
    #             perlevel = 0
    #     return perlevel

    def getStocksRealPrices(self, df):
        tl = int(df.shape[0] / 300) + 1
        total = None
        for m in range(0, tl):
            codes = self.getRequestCodes(df, m)
            result = self.getRealPrice3(codes)
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

    # 保留原始的原始的数据
    def getRealPrice3(self, codes):
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
        cols = ['code', 'open', 'close', 'price', 'high', 'low', 'buy1', 'sell1', 'done_num', 'done_money',
                'buy1_num', 'buy1_price', 'buy2_num', 'buy2_price', 'buy3_num', 'buy3_price', 'buy4_num', 'buy4_price',
                'buy5_num', 'buy5_price',
                'sell1_num', 'sell1_price', 'sell2_num', 'sell2_price', 'sell3_num', 'sell3_price', 'sell4_num',
                'sell4_price', 'sell5_num', 'sell5_price',
                'date', 'time']
        ret = pd.DataFrame(columns=cols, index=[])
        for retstr in r.text.split(';'):
            if len(retstr) < 50:
                continue
            p1 = retstr.index("\"") + 1
            p2 = retstr.rindex("\"") - 1

            if p2 > p1:
                db = retstr[p1:p2].split(',')
                if p1 == 21:
                    code = str(retstr[13:19])
                else:
                    code = str(retstr[14:20])

            ret.loc[len(ret)] = [code, db[1], db[2], db[3], db[4], db[5], db[6], db[7], db[8], db[9],
                                 db[10], db[11], db[12], db[13], db[14], db[15], db[16], db[17], db[18], db[19],
                                 db[20], db[21], db[22], db[23], db[24], db[25], db[26], db[27], db[28], db[29],
                                 db[30], db[31]]
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

    def setReplay(self, flag=False):
        self.isReplay = flag

    def replayModel(self, date=''):
        try:
            if self.isReplay:
                rData = self.cts.getLastTradeDate() if date == '' else date
                fpath = f'{self.path}/{self.minutepath}/{rData}/'
                if not os.path.exists(fpath):
                    print(f'路径不存在 {fpath}')
                allfiles = os.listdir(fpath)
                files = sorted(allfiles,key=lambda file: os.path.getctime(os.path.join(fpath, file)))
                alldb = None
                for fl in files:
                    fname = os.path.join(fpath, fl)
                    db = pd.read_csv(fname,dtype={'code': str})
                    self.realdata.push(db,False)
                    time.sleep(0.1)
                    # alldb = db if alldb is None else pd.concat([alldb, db], ignore_index=True, axis=0)
                # alldb.sort_values(by='time', inplace=True)
                # self.realdata.push(alldb, False)
        except Exception as er:
            print(er)

    def realModel(self):
        # now = datetime.datetime.now().strftime('%Y%m%d')
        # if not self.cts.isTradeDate(now):
        #     print('不是交易日！')
        #     return
        df = self.cts.filterStocks()
        while True:
            print('======================================')
            if self.isTradeTime():
                log(f'数据监控中')
                dk = self.getStocksRealPrices(df)
                # dk = pd.read_csv('data/minute/20250127/14_25.csv')
                self.realdata.push(dk)
            else:
                self.printEmptyTime()

            if self.isPrepareTime():
                time.sleep(1)
            else:
                time.sleep(8)

            if self.isDayworkTime():
                daywork = CDayWork(self.endtriiger)
                # daywork.endtrigger = self.endtriiger
                daywork.run()
                self.dayworkflag = True

            if self.exitflag:
                break

    # 监控实时数据并缓存
    def monitor(self):
        try:
            if self.isReplay:
                self.replayModel()
            else:
                self.realModel()
        except Exception as ex:
            error(ex)
