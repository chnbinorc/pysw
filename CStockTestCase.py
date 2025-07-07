import datetime
import os.path

import pandas as pd
import CCaseBase
import CRealData
from CDataPrepare import CDataPrepare
from CTools import CTools
from CTushare import CTushare
import json

class CStockTestCase(CCaseBase.CCaseBase):
    _obj = None

    @staticmethod
    def create():
        if CStockTestCase._obj is None:
            CStockTestCase._obj = CStockTestCase()
        return CStockTestCase._obj

    def __init__(self):
        super().__init__()
        self.cts = CTushare()

    def run(self, vdata):
        try:
            self.test_rise_top_query()
        except Exception as err:
            print(err)
        return '123'

    # 同价连续多日上涨的情况
    def test_rise_top_query(self):
        sqlstr = 's6 > 0.05 and s7 > 0.05'
        sqlstr = 's6 > 0.05 and s7 > 0.05'

        td = 7
        tk = 8
        # sqlstr = f's{td} + s{tk} > 0.1'
        sqlstr = f's{td} > 0.05'
        for x in range(td+1,td+3):
            # if not (x == td or x == tk):
            #     sqlstr = f'{sqlstr} and s{x} < 0.03'
            if not x == td:
                sqlstr = f'{sqlstr} and s{x} < 0.03'
        print(sqlstr)
        self.test_rise_top(sqlstr)

    def test_rise_top(self, sqlstr='s0 > 0'):

        pre = CDataPrepare.create()
        dbpre = pre.getData()

        db = self.cts.filterStocks()
        columns = ['s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 'code']
        retdb = pd.DataFrame(columns=columns)
        for i, row in db.iterrows():
            diff = self.calRiseTop(row)
            retdb.loc[len(retdb)] = diff.values
        da = retdb.query(f'{sqlstr}')
        da = pd.merge(da, dbpre, left_on='code', right_on='code', how='inner')
        da.sort_values(by=['ind_code'], inplace=True)
        # dc = pd.DataFrame()
        # for indx,item in da.iterrows():
        #     for i in range(4,10):
        #         col = f's{i} > 0.05'
        #         ret = da.query(col)
        #         if ret.shape[0] > 0:
        #             if da.shape[0] > 0:
        #                 dc = pd.concat([dc, ret], ignore_index=True, axis=0)
        #             else:
        #                 dc = ret
        # da = dc
        print(da)

    def calRiseTop(self, row):
        file = f'data/indicators/{row.ts_code}.csv'
        if not os.path.exists(file):
            return [row.ts_code, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        dk = pd.read_csv(file)
        da = dk.tail(10)
        diff = da.apply(lambda x: round((x.high - x.pre_close) / x.pre_close, 2), axis=1)
        diff.loc[len(diff)] = CTools.getOnlyCode(row.ts_code)
        return diff

    # 统计突破信号出现，比如盘中上涨5个点，其后交易日缩量的情况