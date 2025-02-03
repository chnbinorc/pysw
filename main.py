# -*- coding: UTF-8 -*-
import datetime
import math
import time

import CConfigs as configs
import CStrategy
import CTushare
import CTushare as cts
import CTools as tools
import easyocr

import Constants
from CDayWork import CDayWork
from CStockMarket import CStockMarket
from CTools import CTools

import datesum as datesum
import CStrategy as strate
import pandas as pd
import CMethod as method
import CMacdBbiCase as macd
from CMacdBbiCaseStock import CMacdBbiCaseStock
from queue import Queue
import numpy as np

from testMethod import CTestMethod

# def strinstr(cond):
#     for i,row in dbyz.iterrows():
#         if cond in row.orgs:
#             return True
#     return False

if __name__ == '__main__':
    configs = configs.CConfigs()
    md = method.CMethod()
    cts = CTushare.CTushare()
    strate = strate.CStrategy()
    tmd = CTestMethod()

    md.runMarket()
    md.runWebsocket()

    # tmd.test_checkData()
    # tmd.test_boardwin()

    # tmd.doWork()
    # tmd.doBakDataBat(20241125,20241227)

    # 生成BBImacd指标模型
    # tmd.genMacdBbiModel()

    # 生成预处理数据
    # tmd.genPreData()
    # tmd.genTargetPredictStockDay()

    # tmd.test_webcoket()

    # 日终任务
    # tmd.dayWork()

    # print(tmd.analyDay())
    # print(tmd.analy_all_bbi())

    # print(cts.getYZOrgin())
    # cts.updateTHSIndex()
    # tmd.updateStockMoneyFlow()
    # tmd.test_realdata()

    # dbyz = cts.getYZOrgin()
    # db = cts.filterStocks()
    # nowtime = datetime.datetime.now().strftime('%H%M%S')
    # print(nowtime)
    # for i,row in db.iterrows():
    #     # cts.updateBlockTrade(row.ts_code)
    #     now = datetime.datetime.now().strftime('%Y%m%d')
    #     start = CTools.getDateDelta(now, -Constants.ONE_WEAK_DAYS * 2)
    #     cond = f'trade_date > {start} '
    #     dk = cts.getBlockTrade(row.ts_code,cond)
    #     for j,it in dk.iterrows():
    #         if it.buyer == '机构专用':
    #             break
    #         if strinstr(it.buyer) and int(it.trade_date) == 20250121:
    #             print(f'{it.ts_code}  {it.trade_date}  {it.amount} {it.buyer}')
    #     # if dk.shape[0] > 0:
    #     #     if dk['amount'].sum() > 1000:
    #     #         print(dk)
    #     # time.sleep(0.1)
    # nowtime = datetime.datetime.now().strftime('%H%M%S')
    # print(nowtime)

    # print(cts.getBlockTrade('600186.sh'))

    # daywork = CDayWork(None)
    # daywork.genTargetPredictStockDay()
    # daywork.updateIndexMoneyFlow_THS()
    # daywork.genPreData()



    # tmd.test_stat2()
    # tmd.test_draw_std()
    # tmd.test_getRealPrice()
    # tmd.test_class_abc()


    '''  
    日支出
    '''
    # ds = datesum.datesum()
    # ds.readfile()
