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

    # df = pd.read_csv('D:/work/StockWinner/source/pysw/data/indicators/000981.SZ.csv')
    # print(dk)
    # strate.genIndicatorsDayCode('000977.SZ')
    # strate.draw('000981.SZ',df,'000981.SZ')
    # strate.drawMpf(df)

    # while True:
    #     cmd = input('请输入指令：')
    #     if cmd == 'exit':
    #         break
    #     else:
    #         print(cmd)
    #     time.sleep(10)

    # cts.qryPoints()
    # md.doWork()

    # md.doBakDataBat(20241125,20241227)

    # 生成BBImacd指标模型
    # md.genMacdBbiModel()

    # 生成预处理数据
    # md.genPreData()
    # md.genTargetPredictStockDay()

    # 日终任务
    # md.dayWork()
    md.marketrun()

    # print(md.analyDay())
    # print(md.analy_all_bbi())

    # print(cts.getYZOrgin())
    # cts.updateTHSIndex()
    # md.updateStockMoneyFlow()
    # md.test_realdata()

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

    # market = CStockMarket()
    # market.runStockIndexStat()





    # md.test_stat2()
    # md.test_draw_std()

    # retdb = md.getRealPrice()  # .query('level > 0').sort_values(by='level')
    # retdb.to_csv('d:/temp/fake_min_data_2.csv', index=False)
    # print(retdb.query('level > 0').sort_values(by='level'))

    # dk = pd.read_csv('d:/temp/bbidata_kshape_day_10_std.csv').query('succeed > 0.5 and succeed <= 0.6').sort_values(by=['label','quaprice','quavol'])
    # print(dk)

    # db = pd.read_csv('d:/temp/bbidata.csv').query('quaprice == 0 and quavol == 3 and label == 6')
    # # print(db)
    # # print(db.shape[0])
    # dz = db.copy()
    #
    # tmp = pd.Series()
    # dz.drop(columns=['quaprice','quavol','days','income','ts_code','trade_date','label'],inplace=True)
    # for i,row in dz.iterrows():
    #     arr = np.array(row)
    #     tmp.loc[len(tmp)] = round(max(arr) - min(arr),3)
    # # print(tmp)
    # db['bbi_range'] = tmp.values
    # print(db.sort_values(by='income'))

    # db = pd.read_csv('d:/temp/bbidata_kshape_day_10_std.csv')
    # db.sort_values(by='succeed',ascending=False,inplace=True)
    # print(db)

    # stock = CMacdBbiCaseStock('000002.SZ')
    # stock.test()
    # macd = macd.CMacdBbiCase()

    # df = pd.read_csv('d:/temp/macdbbi.csv').query('trade_date >= 20241128')
    #
    # print(df)

    '''  
    日支出
    '''
    # ds = datesum.datesum()
    # ds.readfile()
