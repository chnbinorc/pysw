# -*- coding: UTF-8 -*-

import CConfigs as configs
import CTushare
import CTushare as cts

if __name__ == '__main__':
    configs = configs.CConfigs()
    cts = CTushare.CTushare()
    cts.getAllSockInfo(True)
