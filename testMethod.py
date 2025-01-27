
import pandas as pd
import os
import numpy as np

import CTools
from CCommon import log, warning, error
import CStrategy as strate
import CTools as ctools
import CTushare as cts
from CDayWork import CDayWork
from CMacdBbiCaseStock import CMacdBbiCaseStock
from CMacdBbiCase import CMacdBbiCase
from CIndicatorAI import CIndicatorAI
from CStockMarket import CStockMarket

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 10000)
pd.set_option('display.width', 10000)

class CTestMethod:
    def __init__(self):
        self.cts = cts.CTushare()
        self.strate = strate.CStrategy()
        self.tools = ctools.CTools()
        self.bbicase = CMacdBbiCase()
        return

    # region  ============日终任务============

    # 日终任务
    def dayWork(self):
        daywork = CDayWork()
        daywork.run()

    # 近3个交易日产生的双金叉个股
    def analyDay(self):
        # self.cts.updateTHSIndex()

        db = self.bbicase.analy()
        # print(db)
        index = 'N'
        market = CStockMarket()
        dbind = market.runStockIndexStat(self.cts.getPreTradeDate(), index)
        # dbths = self.cts.getIndexThsMembers('885918.TI')
        db[['ind_code', 'ind_range', 'ind_name']] = db.apply(
            lambda x: self.mergIndex2Stock(x.ts_code, dbind, index), axis=1, result_type="expand")
        db.sort_values(by='ind_range', ascending=False, inplace=True)
        print(db)

    def analy_all_bbi(self):
        fname = 'd:/temp/analy_all_bbi.csv'
        if not os.path.exists(fname):
            db = self.bbicase.analy_all_bbi()
            db.to_csv(fname, index=False)
        else:
            db = pd.read_csv(fname)
        dk = db.query('label in (0,1,2,4,7,9) and range > 0.1')
        return dk

    def mergIndex2Stock(self, tscode, dbind, index='N'):
        db = self.cts.getStockIndex(tscode, index)
        # print(db)
        level = -10
        retstr = None
        for i, row in db.iterrows():
            dk = dbind.query(f'ts_code == "{row.ind_code}"')
            if dk.shape[0] == 0:
                # print(row)
                continue
            if dk.iloc[0].level > level:
                level = dk.iloc[0].level
                retstr = [dk.iloc[0].ts_code, dk.iloc[0].level, dk.iloc[0]["name"]]
        return retstr

    # endregion

    # 生成macdbbi双金叉模型数据，除非需重新计算，运行一次就好
    def genMacdBbiModel(self):
        case = CMacdBbiCase()
        case.genMacdBBIModel()
        cia = CIndicatorAI()
        cia.test_kshape(True)
        cia.test_make_kshape_day_10()

    # region 测试代码
    def test_realdata(self):
        market = CStockMarket()
        market.realDataTrigger()
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

    def test_getRealPrice(self):
        market = CStockMarket()
        df = self.cts.filterStocks()
        dk = market.getStocksRealPrices(df)
        print(dk)

    def test_class_abc(self):
        case = CMacdBbiCase()
        case.run()
    # endregion