# -*- coding: UTF-8 -*-

import CConfigs as configs
import CTushare
import CTushare as cts

import datesum as datesum

if __name__ == '__main__':
    # configs = configs.CConfigs()
    # cts = CTushare.CTushare()
    # # print(cts.getStockBaseInfo())
    # print(cts.getLastTradeDate())
    ds = datesum.datesum()
    ds.readfile()