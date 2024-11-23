# -*- coding: UTF-8 -*-

import CConfigs as configs
import CTushare
import CTushare as cts
import CTools as tools

from CTools import CTools

import datesum as datesum

if __name__ == '__main__':
    configs = configs.CConfigs()
    cts = CTushare.CTushare()
    # print(cts.getStockBaseInfo())
    # cts.initData()
    cts.currentDataDayAppend()
    '''
    日支出
    '''
    # ds = datesum.datesum()
    # ds.readfile()
