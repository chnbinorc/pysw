# -*- coding: UTF-8 -*-
import tushare as ts
import pandas as pd
import os
import datetime
import time

import CConfigs
import CConfigs as Configs

pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth',100)

'''
积分过期查询先用接口实现，后续再做网页版
https://tushare.pro/document/1?doc_id=307
'''

'''
tushare ，数据源
'''
class CTushare:
    tsToken = ''
    pro = None
    dataPath = ''

    def __init__(self):
        if not bool(CTushare.tsToken):
            Configs = CConfigs.CConfigs()
            ts.set_token(Configs.getTushareToken())
            CConfigs.pro = ts.pro_api()
            CConfigs.dataPath = Configs.getLocalDataPath()
            if os.path.exists(CConfigs.dataPath):
                os.mkdir(CConfigs.dataPath)
        self.allStockFile = '%s/allstock.csv' % CConfigs.dataPath
        self.stockBaseFile = '%s/stockbase.csv' % CConfigs.dataPath

    def getAllSockInfo(self,reload = False):
        if (reload) :
            df = CConfigs.pro.stock_basic(
            is_hs='',
            list_status='',
            exchange='',
            ts_code='',
            market='',
            #limit='',
            #offset='',
            name='',
            fields='ts_code,symbol,name,area,industry,fullname,enname,cnspell,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')

            df.to_csv(self.allStockFile,encoding="utf_8_sig")
        df = pd.read_csv(self.allStockFile)
        return df