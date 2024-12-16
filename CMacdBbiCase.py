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
from CIndicatorAI import  CIndicatorAI

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
        filename = f'd:/temp/predictdata_{now}.csv'
        df = self.cts.filterStocks()
        db = self.getDoubleGoldBBI(df)
        if db is not None and db.shape[0] > 0:
            dk = db.copy()
            dk = dk.drop(columns=['quaprice', 'quavol', 'ts_code', 'trade_date'])
            arr = np.array(dk).reshape(-1, 12, 1)
            labels = self.cia.fit_kshape(arr)
            db['label'] = labels
            # db.to_csv('d:/temp/predictdata.csv',index=False)
            db.to_csv(filename, index=False)

    def analy(self):
        now = self.cts.getLastTradeDate()
        filename = f'd:/temp/predictdata_{now}.csv'
        if not os.path.exists(filename):
            now = self.cts.getPreTradeDate()
            filename = f'd:/temp/predictdata_{now}.csv'
            if not os.path.exists(filename):
                print(f'文件不存在，请生成预处理文件:{filename}')
                return
        db = pd.read_csv(filename)
        # db = pd.read_csv('d:/temp/predictdata.csv')
        dk = pd.read_csv('d:/temp/bbidata_kshape_day_10_std.csv')
        dd = pd.merge(db, dk, on=['quaprice', 'quavol', 'label'], how='left')
        dz = dd[['quaprice', 'quavol', 'label', 'ts_code', 'trade_date', 'succeed', 'simples']].copy()
        # dz.sort_values(by='succeed', ascending=False, inplace=True)

        income = pd.Series()
        range = pd.Series()
        for i,row in dz.iterrows():
            fname = f'{self.stockIndiPath}{row.ts_code}.csv'
            if not os.path.exists(fname):
                income.loc[len(income)] = math.nan
                range.loc[len(range)] = math.nan
            else:
                cond = f'trade_date >= {row.trade_date}'
                subdb = pd.read_csv(fname).query(cond)
                subdb.sort_values(by='trade_date',inplace=True)
                range.loc[len(range)] = round( (subdb.iloc[0]['close'] - subdb.iloc[0]['BBI']) / subdb.iloc[0]['BBI'],3)
                if len(subdb) == 1:
                    income.loc[len(income)] = 0
                else:
                    income.loc[len(income)] = round((subdb.iloc[len(subdb)-1]['close'] - subdb.iloc[0]['close']) / subdb.iloc[0]['close'],3)
        dz['income'] = income.values
        dz['range'] = range.values
        dz.sort_values(by=['trade_date','income'], ascending=False,inplace=True)
        print(dz)

    # 查询个股最近一个月双金叉情况，如果双金叉在3个交易日内发生，则返回最近此双金叉前12个交易日的BBI变化数组，包含此双金叉发生的交易日
    def getDoubleGoldBBI(self, db):
        cols = ['s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 'quaprice', 'quavol',
                'ts_code', 'trade_date']
        data = pd.DataFrame(columns=cols)
        for i, row in db.iterrows():
            stock = CMacdBbiCaseStock(row.ts_code)
            sbbi = stock.getRecentSignData()
            if sbbi is not None:
                data.loc[len(data)] = sbbi.values
        return data

    def checkBBIGold(self, df):
        return

    def checkMacdGold(self, df):
        return

    def buyCondition(self, df):
        return

    # 过滤股票
    def filterStocks(self):
        """ 查询主板和中小板 """
        df = self.cts.queryStockbaseBoardCust(Constants.MAIN_CONDITION_STR)
        da = self.cts.queryBakBasic("industry != '银行'")
        dk = pd.merge(df, da, left_on='ts_code', right_on='ts_code', how='inner')
        columns = ['ts_code', 'float_mv', 'total_mv', 'name_x',
                   'industry_x']
        dtmp = dk[columns].copy()
        dtmp = dtmp.query('float_mv > 50').sort_values(by='industry_x')
        Bool = dtmp.name_x.str.contains("ST")  # 去除ST
        dtmp = dtmp[~Bool]
        return dtmp

    # 生成macdbbi指标模型
    def genMacdBBIModel(self):
        db = None
        idx = 0
        print(len(self.cts.filterStocks()))
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
            db.to_csv('d:/temp/bbidata.csv', index=False, encoding="utf_8_sig")

    # 样本检测
    def testSimple(self):
        df = pd.read_csv('d:/temp/bbidata.csv')
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
