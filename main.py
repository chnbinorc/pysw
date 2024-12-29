# -*- coding: UTF-8 -*-
import datetime
import math

import CConfigs as configs
import CStrategy
import CTushare
import CTushare as cts
import CTools as tools

from CTools import CTools

import datesum as datesum
import CStrategy as strate
import pandas as pd
import CMethod as method
import CMacdBbiCase as macd
from CMacdBbiCaseStock import CMacdBbiCaseStock
from queue import Queue
import numpy as np

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

    # cts.qryPoints()
    # md.doWork()

    # md.doBakDataBat(20241125,20241227)

    # 日终任务
    # md.dayWork()


    # 生成BBImacd指标模型
    # md.genMacdBbiModel()

    # 生成预处理数据
    # md.genPreData()
    # md.analyDay()
    # md.test_stat2()
    # md.test_draw_std()
    md.genTargetPredictStockDay()


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
