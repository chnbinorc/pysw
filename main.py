# -*- coding: UTF-8 -*-
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

if __name__ == '__main__':
    configs = configs.CConfigs()
    md = method.CMethod()
    cts = CTushare.CTushare()
    strate = strate.CStrategy()

    # df = pd.read_csv('D:/work/StockWinner/source/pysw/data/indicators/000977.SZ.csv')
    # print(dk)
    # strate.genIndicatorsDayCode('000977.SZ')
    # strate.draw('000977.SZ',df,'000977.SZ')
    # strate.drawMpf(df)

    # cts.qryPoints()
    # md.doWork()

    # 日终任务
    # md.dayWork()

    # 生成BBImacd指标模型
    md.genMacdBbiModel()

    # 生成预处理数据
    md.genPreData()
    md.analyDay()

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
