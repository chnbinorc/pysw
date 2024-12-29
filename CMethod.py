import datetime
import threading
import time
import pandas as pd
import os
import numpy as np

import CTools
from CCommon import log, warning, error
import CStrategy as strate
import CTools as ctools
import CTushare as cts
import Constants
import ClsRealTime as crt
import CRealData as realdata
from CMacdBbiCaseStock import CMacdBbiCaseStock
from CMacdBbiCase import CMacdBbiCase
from CIndicatorAI import CIndicatorAI

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 10000)
pd.set_option('display.width', 10000)


class CMethod:
    def __init__(self):
        self.cts = cts.CTushare()
        self.strate = strate.CStrategy()
        self.tools = ctools.CTools()
        self.crt = crt.ClsRealTime()
        self.realdata = realdata.CRealData(self.trigger)
        self.bbicase = CMacdBbiCase()

    # region  ============日终任务============

    # 日终任务
    def dayWork(self):
        log('============开始日终处理============')
        log('更新备用数据')
        self.doBakData()
        log('更新日线行情数据')
        self.doDayData()
        log('更新指标数据分析')
        self.doIndicators(False)
        # log('============日终处理结束============')

    # 日线指标生成完成事件
    # 完成事件后，可进行预处理，分析等操作
    def evtIndicatorsCompletDay(self, start, end):
        self.strate.completTitles += 1
        if self.strate.completTitles == self.strate.titles:
            log('============生成最近交易日预处理数据============')
            self.genPreData()
            log('============生成目标预测数据============')
            self.genTargetPredictStockDay()
            log('============日终处理结束============')
        else:
            log(f'日终指标数据生成情况：总数{self.strate.titles},完成{self.strate.completTitles}')

    # 更新备用数据
    def doBakData(self):
        now = datetime.datetime.now().strftime('%Y%m%d')
        # start = self.tools.getDateDelta(now, -Constants.ONE_YEARE_DAYS)
        try:
            self.cts.BakDaily(now, now)
        except Exception as er:
            error(er)

    # 更新指定日期段的备用行情
    def doBakDataBat(self, start, end):
        try:
            self.cts.BakDaily(start, end)
        except Exception as er:
            error(er)

    # 更新日线行情
    def doDayData(self):
        now = datetime.datetime.now().strftime('%Y%m%d')
        start = self.tools.getDateDelta(now, -Constants.ONE_YEARE_DAYS - Constants.ONE_MONTH_DAYS * 6)
        df = self.cts.queryStockbaseBoardCust(Constants.MAIN_CONDITION_STR)
        for i, row in df.iterrows():
            try:
                filepath = self.cts.stockPriceDayPath + row.ts_code + '.csv'
                if os.path.exists(filepath):
                    self.doDayDataCode(row.ts_code)
                else:
                    ds = self.cts.getCodeDay(row.ts_code, start, now)
                    self.cts.updateDailyCode(row.ts_code, ds)
            except Exception as er:
                error(er)

    # 生成预处理数据
    def genPreData(self):
        db = self.bbicase.genPredictData()

    def analyDay(self):
        return self.bbicase.analy()

    def doDayDataCode(self, code):
        now = datetime.datetime.now().strftime('%Y%m%d')
        filepath = self.cts.stockPriceDayPath + code + '.csv'
        if os.path.exists(filepath):
            rows = pd.read_csv(filepath)
            date = rows['trade_date'].max()
            n = self.tools.dateDiff(now, date)
            if n > 0:
                start = self.tools.getDateDelta(now, -n + 1)
                df = self.cts.getCodeDay(code, start, now)
                # df = self.cts.getCodeDaily(code,start,now)
                if df is not None and df.shape[0] > 0:
                    rows = rows.append(df, ignore_index=True)
                self.cts.updateDailyCode(code, rows)

    # 生成指标数据
    def doIndicators(self, flag=False):
        self.strate.evtIndicatorsCompletDay = self.evtIndicatorsCompletDay
        self.strate.genIndicators('', flag)
        # total = self.filterStocks().shape[0]
        # count = 0
        # print(f'总共处理 {total}')
        # for i, row in self.filterStocks().iterrows():
        #     print(count)
        #     if count % 10 == 0:
        #         print(f'已经处理{count}')
        #     df = self.strate.genIndicatorsDayCode(row.ts_code)
        #     if flag:
        #         self.strate.draw(row.ts_code, df, row.ts_code)
        #     count += 1
        # return

    # 获取实时行情
    def getRealPrice(self):
        # start = datetime.datetime.now()
        # print(start.strftime('%H_%M_%S'))
        # print(start.second)
        df = self.cts.filterStocks()
        tl = int(df.shape[0] / 300) + 1
        total = None
        for m in range(0, tl):
            codes = self.getRequestCodes(df, m)
            result = self.crt.GetRealPrices2(codes)
            if total is None:
                total = result
            else:
                total = pd.concat([total, result], ignore_index=True, axis=0)
        # end = datetime.datetime.now()

        # delta = end - start
        # print(delta.seconds)

        # if not total is None:
        #     total.to_csv('d:/temp/tmp.csv', index=False, encoding="utf_8")
        return total

    def getRequestCodes(self, data, index=0):
        ret = ''
        star = index * 100 + 0
        end = star + 100
        for idx, row in data[star:end].iterrows():
            ret = ret + row['ts_code'] + ','
        return ret

    # endregion

    def doWork(self):
        now = datetime.datetime.now()
        for i in range(0, 10):
            data = self.getRealPrice()
            self.realdata.push(data)
            time.sleep(20)

    def trigger(self, df):
        if not df is None:
            print(df.shape[0])

    def genMacdBbiModel(self):
        case = CMacdBbiCase()
        case.genMacdBBIModel()
        cia = CIndicatorAI()
        cia.test_kshape(True)
        cia.test_make_kshape_day_10()

    # 生成目标预测数据
    def genTargetPredictStockDay(self):
        case = CMacdBbiCase()
        case.getpredictStockDay()

    # region 测试代码

    def test_draw_std(self):
        cia = CIndicatorAI()
        cia.test_draw_std()

        # 检查个股某个点的label情况

    def test_stat5(self):
        fname = f'{self.strate.stockIndicatorsPath}002192.SZ.csv'
        pp = pd.read_csv(fname).query('trade_date < 20240725').tail(11)

        diff = pd.Series(pp['BBI'])
        diff.loc[len(diff)] = pp.iloc[10]['BBI']
        print(diff)
        arr = np.array(diff.values).reshape(-1, 12, 1)
        cia = CIndicatorAI()
        labels = cia.fit_kshape(arr)
        print(labels)

    def test_stat2(self):
        filename = 'd:/temp/bbidata.csv'
        # db = pd.read_csv(filename).query('quaprice == 0 and (quavol == 3 or quavol == 4) and label == 3')
        db = pd.read_csv(filename).query('quaprice == 0 and (quavol == 2 or quavol == 3 or quavol == 4) and label == 6')
        dk = pd.read_csv('d:/temp/bbidata_kshape_day_10_std.csv')
        dd = pd.merge(db, dk, on=['quaprice', 'quavol', 'label'], how='inner')

        retdb = pd.DataFrame(columns=dd.columns)
        for i, row in dd.iterrows():
            fname = f'{self.strate.stockIndicatorsPath}{row.ts_code}.csv'
            dbase = pd.read_csv(fname)
            stock = CMacdBbiCaseStock(row.ts_code)
            rflag, mflag = stock.filterPriceBBIRange_50_6(dbase, row.trade_date)
            if rflag:
                retdb.loc[len(retdb)] = row

        # dm = pd.read_csv(f''self.strate.stockIndicatorsPath)
        dd = retdb

        diffmacd = dd.apply(lambda row: row['macd_diff'] - row['macd_dea'] > 0, axis=1)
        dd['diffmacd'] = diffmacd
        # print(dd.sort_values(by=['succeed','quaprice','quavol','label'],ascending=False))

        dd.sort_values(by=['income'], ascending=False, inplace=True)
        print(dd.shape[0])
        d1 = dd.query('income > 0')
        print(d1.shape[0])
        d2 = dd.query('income < 0')
        print(d2.shape[0])
        d3 = dd.query('income == 0')
        print(d3.shape[0])

        d1.sort_values(by=['ts_code', 'trade_date'], inplace=True)
        print(d1)
        print('===================================')
        d2.sort_values(by=['ts_code', 'trade_date'], inplace=True)
        print(d2)
        # print(db.shape[0])
        # dk = db.apply(lambda row: self.calCloseBBI(row),axis=1)
        # db['flag'] = dk.values
        # print(db.groupby('flag')['flag'].count())

    def test_stat4(self):
        filename = 'd:/temp/bbidata.csv'
        db = pd.read_csv(filename).query('trade_date < 20241210 and income < 0')
        print(db.shape[0])
        dk = pd.read_csv('d:/temp/bbidata_kshape_day_10_std.csv').query('quavol > 2 and succeed > 0.7 and simples > 30')
        print(dk)
        dd = pd.merge(db, dk, on=['quaprice', 'quavol', 'label'], how='inner')
        print(dd.shape[0])

        for i, row in dd.iterrows():
            tscode = row.ts_code
            date = row.trade_date
            print(row)
            fname = f'{self.strate.stockIndicatorsPath}{tscode}.csv'
            if os.path.exists(fname):
                subdb = pd.read_csv(fname).query(f'trade_date < {date}').tail(12)
                print(subdb)
                values = subdb.apply(lambda x: [x.BBI, round((x.close - x.BBI) / x.BBI, 3)], axis=1)
                print(values)
            break

        # filename = 'd:/temp/bbidata_kshape_day_10_std.csv'
        # db = pd.read_csv(filename).query('succeed > 0.55 and simples > 30')
        # db.sort_values(by=['succeed','quaprice','quavol','label'],ascending=False,inplace=True)
        # print(dd.shape[0])

    def test_stat3(self):
        path = self.strate.stockIndicatorsPath
        db = self.cts.filterStocks('float_mv > 50')
        cols = ['ts_code', 'quaprice', 'vol2', 'vol3', 'vol4', 'label', 'BBI']
        dk = pd.DataFrame(columns=cols)
        date = self.cts.getLastTradeDate()
        for i, row in db.iterrows():
            filename = f'{path}{row.ts_code}'
            if os.path.exists(filename):
                dbbase = pd.read_csv(filename)
                data = dbbase.query(f'trade_date == {date}')
                if data.shape[0] == 0 and data.iloc[0]['close'] < data.iloc[0]['BBI']:
                    case = CMacdBbiCaseStock()
                    case.calQuaPoint(dbbase, 'price', data.iloc[0]['BBI'])

    def calCloseBBI(self, row):
        path = self.strate.stockIndicatorsPath
        nextdate = self.cts.getNextTradeDate(row.trade_date)
        filename = f'{path}{row.ts_code}.csv'
        db = pd.read_csv(filename).query(f'ts_code == "{row.ts_code}" and trade_date == {nextdate}')
        if db is None or db.shape[0] == 0:
            print(f'filename:{filename},ts_code:{row.ts_code},date:{row.trade_date}')
            return -1
        else:
            if (db.iloc[0]['close'] - db.iloc[0]['pre_close']) / db.iloc[0]['pre_close'] > 0.00:
                return 1
            else:
                return 0

    def test_stats(self):
        filename = 'd:/temp/bbidata.csv'
        db = pd.read_csv(filename).query('income > 0')
        print(db.shape[0])
        db2 = pd.read_csv('d:/temp/bbidata_kshape_day_10_std.csv').query('succeed > 0.6')
        print(db2.shape[0])
        db2.drop(columns=['succeed', 'fail', 'simples'], inplace=True)
        dk = pd.merge(db, db2, how='inner', on=['quaprice', 'quavol', 'label'])
        print(dk.shape[0])
        # # dz = db.apply(lambda x: datetime.datetime.strptime(str(x['trade_date']),'%Y%m%d').isoweekday(),axis=1)
        # # db['ndate'] = dz.values
        # # print(db.groupby('ndate')['ndate'].count())
        dz = dk.apply(lambda x: self.calPrice(x), axis=1)
        dk['rate'] = dz.values
        print(dk.groupby('rate')['rate'].count())

    def calPrice(self, row):
        # rate = round((row.s11 - row.s10)/ row.s10,3)
        sz = pd.Series(row).drop(labels=['quaprice', 'quavol', 'days', 'income', 'ts_code', 'trade_date', 'label'])
        rate = round((sz.max() - sz.min()) / sz.min(), 3)
        if rate < 0:
            return 0
        elif rate < 0.01:
            return 1
        elif rate < 0.02:
            return 2
        elif rate < 0.03:
            return 3
        elif rate < 0.04:
            return 4
        elif rate < 0.05:
            return 5
        elif rate < 0.06:
            return 6
        elif rate < 0.07:
            return 7
        elif rate < 0.08:
            return 8
        elif rate < 0.09:
            return 9
        else:
            return 10

    # endregion
