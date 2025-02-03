import datetime
import threading
import time
import pandas as pd
import os
import numpy as np

import CConfigs
from CCommon import log, warning, error
from CMacdBbiCase import CMacdBbiCase
from CStockMarket import CStockMarket
from CWebSocket import CWebSocket

from ClsMThreadPool import ClsMTPool

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 10000)
pd.set_option('display.width', 10000)


class CMethod:
    def __init__(self):
        self.configs = CConfigs.CConfigs()
        self.mttool = ClsMTPool.Create()
        self.market = CStockMarket(self.realDataTrigger)
        self.websocket = CWebSocket(self.websocketTrigger)
        return

    def run(self):
        return

    def runMarket(self):
        # self.market.setReplay(True)
        self.market.run()

    def runWebsocket(self):
        self.websocket.start()

    # 触发器，实时数据获取时触发
    def realDataTrigger(self):
        print('实时数据获取时触发')
        try:
            case = CMacdBbiCase()
            case.run()
        except Exception as er:
            print(er)

    def websocketTrigger(self,data):
        print(data)

    def checkExit(self):
        flag = self.configs.getAppConfig('main','exit')
        if str.lower(flag) == 'true':
            return True
        else:
            return False
