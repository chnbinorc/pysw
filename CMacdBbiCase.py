import math

import numpy as np

import CCaseBase
import os
import CTushare as cts
import datetime
import pandas as pd
import Constants
import CTools
from CMacdBbiCaseStock import CMacdBbiCaseStock
from CIndicatorAI import CIndicatorAI
from CCommon import log, warning, error


# macd,bbi,obv 指标，批量处理

class CMacdBbiCase(CCaseBase.CCaseBase):

    def __init__(self):
        super().__init__()
        self.predictMacdBbiPath = '{0}/{1}/'.format(self.stockIndiPath, 'predict_macd_bbi')
        if not os.path.exists(self.predictMacdBbiPath):
            os.mkdir(self.predictMacdBbiPath)
        self.cts = cts.CTushare()
        self.cia = CIndicatorAI()
        return

    # 生成预测数据，便于实际运行计算
    def genPredictData(self):
        # 获取满足双金叉数据
        now = self.cts.getLastTradeDate()
        filename = f'{self.stockTempPath}predictdata_{now}.csv'
        df = self.cts.filterStocks()
        db = self.getDoubleGoldBBI(df)
        if db is not None and db.shape[0] > 0:
            dk = db.copy()
            dk = dk.drop(columns=['quaprice', 'quavol', 'ts_code', 'trade_date', 'macd_diff', 'macd_dea', 'macd'])
            arr = np.array(dk).reshape(-1, 12, 1)
            labels = self.cia.fit_kshape(arr)
            db['label'] = labels
            db.to_csv(filename, index=False)

    # 计算所有个股的形态，价格区间，成交量区间
    def analy_all_bbi(self):
        cols = ['ts_code', 'label', 'close', 'quaprice', 'quavol','range']
        result = pd.DataFrame(columns=cols)
        df = self.cts.filterStocks()
        for i, row in df.iterrows():
            fname = f'{self.stockIndiPath}{row.ts_code}.csv'
            if not os.path.exists(fname):
                continue
            dbstock = pd.read_csv(fname)
            dk = dbstock.tail(12)
            range = round((dk['BBI'].max() - dk['BBI'].min()) / dk['BBI'].min(),4)
            close = dk.tail(1).iloc[0]['close']
            dm = dbstock.tail(Constants.ONE_MONTH_DAYS * 5)
            arr = np.array(dk['BBI']).reshape(-1, 12, 1)
            label = self.cia.fit_kshape(arr)[0]
            dm_1 = dm.sort_values(by='close')
            quaprice = self.calQuaValues(dm_1,'close',close)
            dm_2 = dm.sort_values(by='vol')
            quavol = self.calQuaValues(dm_2, 'vol', dk.tail(1).iloc[0]['vol'])
            result.loc[len(result)] = [row.ts_code,label,close,quaprice,quavol,range]
        return result

    def analy(self):
        now = self.cts.getLastTradeDate()
        filename = f'{self.stockTempPath}predictdata_{now}.csv'
        if not os.path.exists(filename):
            now = self.cts.getPreTradeDate()
            filename = f'{self.stockTempPath}predictdata_{now}.csv'
            if not os.path.exists(filename):
                print(f'文件不存在，请生成预处理文件:{filename}')
                return
        db = pd.read_csv(filename)
        dk = pd.read_csv(f'{self.stockTempPath}bbidata_kshape_day_10_std.csv')
        dd = pd.merge(db, dk, on=['quaprice', 'quavol', 'label'], how='left')
        dz = dd[['quaprice', 'quavol', 'label', 'ts_code', 'trade_date', 'succeed', 'simples']].copy()

        income = pd.Series()
        range = pd.Series()
        for i, row in dz.iterrows():
            fname = f'{self.stockIndiPath}{row.ts_code}.csv'
            if not os.path.exists(fname):
                income.loc[len(income)] = math.nan
                range.loc[len(range)] = math.nan
            else:
                cond = f'trade_date >= {row.trade_date}'
                subdb = pd.read_csv(fname).query(cond)
                subdb.sort_values(by='trade_date', inplace=True)
                range.loc[len(range)] = round((subdb.iloc[0]['close'] - subdb.iloc[0]['BBI']) / subdb.iloc[0]['BBI'], 3)
                if len(subdb) == 1:
                    income.loc[len(income)] = 0
                else:
                    income.loc[len(income)] = round(
                        (subdb.iloc[len(subdb) - 1]['close'] - subdb.iloc[0]['close']) / subdb.iloc[0]['close'], 3)
        dz['income'] = income.values
        dz['range'] = range.values
        dz.sort_values(by=['trade_date', 'succeed'], ascending=False, inplace=True)
        dbret = dz.query('succeed > 0.55')
        # print(dbret)
        return dbret

    # 查询个股最近一个月双金叉情况，如果双金叉在3个交易日内发生，则返回最近此双金叉前12个交易日的BBI变化数组，包含此双金叉发生的交易日
    def getDoubleGoldBBI(self, db):
        cols = ['s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 'quaprice', 'quavol',
                'ts_code', 'trade_date', 'macd_diff', 'macd_dea', 'macd']
        data = pd.DataFrame(columns=cols)
        for i, row in db.iterrows():
            stock = CMacdBbiCaseStock(row.ts_code)
            sbbi = stock.getRecentSignData()
            if sbbi is not None:
                data.loc[len(data)] = sbbi.values
        return data

    def calPriceQua(self, df, close):
        dk = df.tail(Constants.ONE_YEARE_DAYS)
        max = dk['close'].max()
        min = dk['close'].min()
        per = (max - min) / 5
        lev = 0
        for i in range(1, 5):
            if close > min + per * i:
                lev = i
        return lev

    def calQuaValues(self,df,col,val):
        qua = df[col].quantile([0.2, 0.4, 0.6, 0.8])
        ret = 0
        idx = 1
        for it in qua:
            ret = idx if val > it else ret
            idx += 1
        return ret


    def getPredictCodes(self):
        db = self.cts.filterStocks()
        cols = ['ts_code', 'trade_date', 'quaprice']
        dk = pd.DataFrame(columns=cols)
        for i, row in db.iterrows():
            fname = f'{self.stockIndiPath}{row.ts_code}.csv'
            if os.path.exists(fname):
                dz = pd.read_csv(fname).sort_values('trade_date')
                it = dz.tail(1)
                if it.iloc[0].close < it.iloc[0].BBI:
                    quaPrice = self.calPriceQua(dz, it.iloc[0].close)
                    dk.loc[len(dk)] = [row.ts_code, it.iloc[0].trade_date, quaPrice]
        return dk

    def prepareStockDay(self, db):
        db = db.reindex(
            columns=db.columns.tolist() + ['close', 'vol', 'succeed', 'vol0', 'rate0', 'vol1', 'rate1', 'vol2', 'rate2',
                                           'vol3',
                                           'rate3', 'vol4', 'rate4'])
        stand = pd.read_csv(f'{self.stockTempPath}bbidata_kshape_day_10_std.csv')
        for i, row in db.iterrows():
            stockfile = f'{self.stockIndiPath}{row.ts_code}.csv'
            dm = pd.read_csv(stockfile)
            quaVols = (dm['vol'].max() - dm['vol'].min()) / 5
            cond = f' quaprice == {row.quaprice} and label == {row.label}'
            dk = stand.query(cond).sort_values(by='quavol')
            if dk.shape[0] == 0:
                continue
            db.loc[i, 'vol0'] = 0
            db.loc[i, 'rate0'] = dk.iloc[0].succeed
            db.loc[i, 'vol1'] = dm['vol'].min() + quaVols
            db.loc[i, 'rate1'] = dk.iloc[1].succeed
            db.loc[i, 'vol2'] = dm['vol'].min() + quaVols * 2
            db.loc[i, 'rate2'] = dk.iloc[2].succeed
            db.loc[i, 'vol3'] = dm['vol'].min() + quaVols * 3
            db.loc[i, 'rate3'] = dk.iloc[3].succeed
            db.loc[i, 'vol4'] = dm['vol'].min() + quaVols * 4
            db.loc[i, 'rate4'] = dk.iloc[4].succeed
            db.loc[i, 'close'] = 0
            db.loc[i, 'vol'] = 0
            db.loc[i, 'succeed'] = 0
            if dk.iloc[0].succeed < 0.5 and \
                    dk.iloc[1].succeed < 0.5 and \
                    dk.iloc[2].succeed < 0.5 and \
                    dk.iloc[3].succeed < 0.5 and \
                    dk.iloc[4].succeed < 0.5:
                db.loc[i, 'flag'] = False
        savefile = f'{self.stockPredictPath}{self.cts.getLastTradeDate()}.csv'
        db.to_csv(savefile, index=False)

    def getPredictData(self, date=datetime.datetime.now().strftime('%Y%m%d')):
        fname = f'{self.stockPredictPath}{date}.csv'
        if os.path.exists(fname):
            return pd.read_csv(fname)
        else:
            error(f'文件不存在:{fname}')
        return None

    # 一定要做日终，得到指标数据，才能做目标数据预测
    def getpredictStockDay(self):
        log('开始获取目标预测数据')
        dk = self.getPredictCodes()
        flags = pd.Series()
        precloses = pd.Series()
        labels = pd.Series()
        cia = CIndicatorAI()
        log(f'目标预测数据数量：{dk.shape[0]}')
        count = 0
        for i, row in dk.iterrows():
            # tradeDate = self.cts.getPreTradeDate(row.trade_date)
            tradeDate = row.trade_date
            stock = CMacdBbiCaseStock(row.ts_code)
            db, quaClose, preclose = stock.predictStockDay(tradeDate)
            dd = db.tail(12)
            diff = pd.Series(dd['BBI'])
            arr = np.array(diff.values).reshape(-1, 12, 1)
            retlabels = cia.fit_kshape(arr)
            if retlabels[0] == 5:
                ret = stock.filterBBIRange_6(tradeDate)
            elif retlabels[0] == 0 or 3 or 6 or 8:
                ret = stock.filterBBIRange_1(tradeDate)
            else:
                ret = stock.filterBBIRange_0(tradeDate)
            flags.loc[len(flags)] = ret
            labels.loc[len(labels)] = retlabels[0]
            precloses.loc[len(precloses)] = preclose
            count += 1
            if count % 10 == 0:
                log(f'处理目标预测数据，总数：{dk.shape[0]},已处理{count}')

        dk['label'] = labels.values
        dk['flag'] = flags.values
        dk['preclose'] = precloses.values
        dk = dk.query('flag == True')
        dk.sort_values(by='flag', inplace=True)
        log(f'开始准备目标预测数据')
        self.prepareStockDay(dk)

    def checkBBIGold(self, df):
        return

    def checkMacdGold(self, df):
        return

    def buyCondition(self, df):
        return

    # 生成macdbbi指标模型
    def genMacdBBIModel(self):
        db = None
        idx = 0
        for i, row in self.cts.filterStocks().iterrows():
            stock = CMacdBbiCaseStock(row.ts_code)
            dk = stock.simpleIndicatorModel()
            if dk is None or dk.shape[0] == 0:
                continue
            if db is None:
                db = dk
            else:
                db = pd.concat([db, dk], ignore_index=True, axis=0)
            idx += 1
            if idx % 100 == 0:
                print(idx)
        if db is not None:
            db.to_csv(f'{self.stockTempPath}bbidata.csv', index=False, encoding="utf_8_sig")

    # 样本检测
    def testSimple(self):
        df = pd.read_csv(f'{self.stockTempPath}bbidata.csv')
        # dk = df.query('quaprice < 6 and quavol > 8').copy()
        # # dk.drop(columns=['s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11'], inplace=True)
        # # print(dk)
        # d1 = dk.query('income > 0')
        # d2 = dk.query('income < 0')
        # print(f'{len(dk)} , { round(len(d1)/len(dk),3) }, { round(len(d2)/len(dk),3) }')
        print(f'样本总数：{df.shape[0]}')
        for i in range(5):
            for j in range(5):
                cond = f'quaprice == {i} and quavol == {j}'
                dk = df.query(cond).copy()
                d1 = dk.query('income > 0')
                d2 = dk.query('income < 0')
                print(
                    f'条件：价格区间：{i} 成交量区间:{j}  总数： {len(dk)} , 成功：{round(len(d1) / len(dk), 3)}, 失败：{round(len(d2) / len(dk), 3)}')
            print('==========================================================')
