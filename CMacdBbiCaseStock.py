import math

import CCaseBase
import os
import CTushare as cts
import datetime
import pandas as pd
import Constants
from CTools import CTools
import numpy as np
from CCommon import log, error, warning
from CIndicatorAI import CIndicatorAI

PERIOD_BOTTOM = '波谷'
PERIOD_TOP = '波峰'
PERIOD_SMOOTH = '平滑'
PERIOD_0_1 = '平滑上升'
PERIOD_0_2 = '平滑下降'
PERIOD_1_1 = '上升平滑'
PERIOD_1_2 = '下降平滑'
PERIOD_OTHER = '其他'


class CMacdBbiCaseStock(CCaseBase.CCaseBase):
    def __init__(self, code):
        super().__init__()
        self.cts = cts.CTushare()
        scode = CTools.getOnlyCode(code)
        self.code = scode + '.SH' if scode.startswith('6') else scode + '.SZ'
        cols = ['ts_code', 'trade_date', 'close', 'direct']
        self.record = pd.DataFrame(columns=cols)
        self.cia = CIndicatorAI()

    def test(self):
        return

    def buy(self, code, date, close):
        self.record.loc[len(self.record)] = [code, date, close, 1]

    def sell(self, code, date, close):
        self.record.loc[len(self.record)] = [code, date, close, 0]

    def calX(self, xflag, arg1, arg2):
        ret = bool(xflag) ^ (arg1 > arg2)
        flag = xflag
        if ret:
            flag = ~xflag
        return ret, flag

    def getTestData(self,days=Constants.ONE_YEARE_DAYS):
        filename = '{0}{1}.csv'.format(self.stockIndiPath, self.code)
        now = self.cts.getLastTradeDate()
        # now = datetime.datetime.now().strftime('%Y%m%d')
        start = CTools.getDateDelta(now, round(- days))
        df = pd.read_csv(filename).query('trade_date > ' + start)
        return df

    # 采样: 双金叉，判断bbi走势，价格位置，成交量，,BBI周期，空间（上涨或下跌空间暂时不考虑）
    def simpleIndicatorModel(self):
        df = self.getTestData()
        df.reset_index()
        xflag = False
        idx = 0
        cols = ['s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 'quaprice', 'quavol', 'days',
                'income',
                'ts_code', 'trade_date']
        # 生成采样数据 近一年BBI macd双金叉
        data = pd.DataFrame(columns=cols)
        for i, row in df.iterrows():
            if idx < 12:
                idx += 1
                continue
            ret, xflag = self.calX(xflag, row['close'], row['BBI'])
            if ret and xflag:
                quaPrice = self.calQuaPoint(df, 'close', row['close'])
                quaVol = self.calQuaPoint(df, 'vol', row['vol'])
                sbbi = self.analyCode(df, idx - 11, idx + 1, quaPrice, quaVol)
                data.loc[len(data)] = sbbi.values
            idx += 1
        return data

    # 获取在最近3个交易日的产生双金叉信号的数据
    def getRecentSignData(self):
        db = self.getTestData()
        quaPrice = 0
        quaVol = 0
        df = self.getTestData(Constants.ONE_WEAK_DAYS)
        df.reset_index()
        xflag = False
        idx = 0
        now = self.cts.getLastTradeDate()
        target = CTools.getDateDelta(now,-3)
        cols = ['ts_code', 'trade_date','label', 'quaprice', 'quavol']
        data = pd.DataFrame(columns=cols)
        for i, row in df.iterrows():
            ret, xflag = self.calX(xflag, row['close'], row['BBI'])
            if ret and xflag and int(row['trade_date']) > target:
                quaPrice = self.calQuaPoint(db, 'close', row['close'])
                quaVol = self.calQuaPoint(db, 'vol', row['vol'])
                arr = np.array(df[idx-11:idx+1]).reshape(-1, 12, 1)
                sz = self.cia.fit_kshape(arr)
                data.loc[0] = [row['ts_code'],row['trade_date'],sz[0],quaPrice,quaVol]
        return data

    def calQuaPoint(self, df, col, val):
        quaLev = df[col].quantile([0.2, 0.4, 0.6, 0.8])
        idx = 0
        for it in quaLev:
            if val < it:
                return idx
            idx += 1
        return idx

    def analyCode(self, df, start, end, quaPrice, quaVol):
        # 计算前12日的BBI差值
        temp = df[start:end]
        baseClose = temp.iloc[0]['PRE_BBI']
        diff = temp.apply(lambda x: round((x['BBI'] - baseClose) / baseClose, 3), axis=1)
        # 计算收益情况，历经天数，成交量
        base = temp.iloc[11]['close']
        income = 0
        maxIncome = 0
        idx = end
        while True:
            if idx >= len(df):
                break
            midIncome = round((df.iloc[idx]['close'] - base) / base, 3)
            income = midIncome
            if income < 0.03 and (idx - end + 1) >= 3:
                break
            if income < -0.05:
                break
            maxIncome = income if income >= maxIncome else maxIncome
            if maxIncome - income > 0.05:
                break
            idx += 1

        diff.loc[len(diff)] = quaPrice
        diff.loc[len(diff)] = quaVol
        diff.loc[len(diff)] = int(idx - end + 1)
        diff.loc[len(diff)] = round(income, 3)
        diff.loc[len(diff)] = temp.iloc[11]['ts_code']
        diff.loc[len(diff)] = temp.iloc[11]['trade_date']

        return diff

    # 不成熟的
    def fight_1(self):
        filename = '{0}{1}.csv'.format(self.stockIndiPath, self.code)
        now = datetime.datetime.now().strftime('%Y%m%d')
        start = CTools.getDateDelta(now, round(- Constants.ONE_YEARE_DAYS * 0.7))
        df = pd.read_csv(filename).query('trade_date > ' + start)

        ''' 金叉True 死叉False'''
        xflag = False
        preRet = None
        buyPre = False
        bbi_val = 0
        checkMacd = False

        for i, row in df.iterrows():
            if buyPre:
                if row['close'] - row['BBI'] > bbi_val:
                    if row['close'] < row['PRICE60']:
                        self.buy(row['ts_code'], row['trade_date'], row['close'])
                    else:
                        if (row['close'] - row['BBI']) / row['BBI'] > 0.02:
                            self.buy(row['ts_code'], row['trade_date'], row['close'])
                    bbi_val = 0
                    buyPre = False
                else:
                    bbi_val = row['close'] - row['BBI']
                    if bbi_val < 0:
                        buyPre = False
                        bbi_val = 0
            if checkMacd:
                if row['macd_diff'] > row['macd_dea']:
                    self.buy(row['ts_code'], row['trade_date'], row['close'])
                bbi_val = 0
                buyPre = False
                checkMacd = False
            '''ret 产生信号'''
            ret, xflag = self.calX(xflag, row['close'], row['BBI'])

            if ret:
                if xflag:
                    # if (row['close'] - row['BBI']) / row['BBI'] < 0.02:
                    #     continue
                    if (row['macd_diff'] > row['macd_dea']):
                        # and ((row['PRICE10'] - row['PRICE60']) / row['PRICE60']) < 0.1 \
                        # and row['PRICE5'] > row['PRICE10']:
                        # and row['vol'] > row['VOL5'] * 1.2:
                        # self.buy(row['ts_code'],row['trade_date'], row['close'])
                        buyPre = True
                        bbi_val = row['close'] - row['BBI']
                    else:
                        checkMacd = True

        # if self.record.shape[0] > 0:
        #     # rcd = self.record.tail(1).iloc[0]
        #     # date =rcd.trade_date
        #     # if CTools.dateDiff(now,date) < 4:
        #     #     print(self.record.tail(1))
        #     print(self.record)
        return self.record
