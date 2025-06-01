import math
import datetime

import numpy as np
import pandas as pd

import CCaseBase
import os
import CRealData
import CTools
from CConfigs import CConfigs
import json

from CDataPrepare import CDataPrepare
from CTushare import CTushare


# 抓潜在龙头

class CCatchDragonCase(CCaseBase.CCaseBase):
    _obj = None

    @staticmethod
    def create():
        if CCatchDragonCase._obj is None:
            CCatchDragonCase._obj = CCatchDragonCase()
        return CCatchDragonCase._obj

    def __init__(self):
        super().__init__()
        self.cts = CTushare()
        self.qdate = datetime.datetime.now().strftime('%Y%m%d')

    # 交易日数据统计
    def getData(self,tradedate=''):
        if tradedate == '':
            tradedate = self.cts.getPreTradeDate(self.qdate)
        pre = CDataPrepare.create()
        predb = pre.getData()
        file = f'{self.stockBakDayPath}{tradedate}.csv'
        print(file)
        if not os.path.exists(file):
            print(f'{file} 文件不存在!!')
            return pd.DataFrame()
        basedb = self.cts.filterStocks()
        basedb['ts_code'] = basedb.apply(lambda x: CTools.CTools.getOnlyCode(x.ts_code), axis=1)
        db = pd.merge(basedb[['ts_code']], predb, left_on='ts_code', right_on='code', how='inner')
        da = pd.read_csv(file)
        da['ts_code'] = da.apply(lambda x: CTools.CTools.getOnlyCode(x.ts_code), axis=1)
        da = pd.merge(db, da[
            ['ts_code', 'trade_date', 'pct_change', 'close', 'change', 'open', 'high', 'low', 'pre_close']],
                      left_on='ts_code', right_on='ts_code', how='inner')
        da['rate'] = da.apply(lambda x: round((float(x.close) - float(x.pre_close)) / float(x.pre_close), 2),
                              axis=1)
        return da

    def run(self, data):
        xdata = {
            'name': 'CDataPrepare',
            'command': 'CDataPrepare_ret',
            'data': ''
        }
        if self.isValidDate(data, '%Y%m%d'):
            self.qdate = data
        retdb = self.getData()
        xdata['data'] = retdb.to_json(orient='table', index=False)
        return json.dumps(xdata)
