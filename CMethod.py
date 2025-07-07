import datetime
import importlib
import json
import sys
import threading
import time
import pandas as pd
import os
import numpy as np

import CConfigs
import CMacdBbiCase
from CCommon import log, warning, error
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
        self.market = CStockMarket.create(self.realDataTrigger)
        self.websocket = CWebSocket(self.websocketTrigger)
        sys.path.append('/')
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
        return
        try:
            print('实时数据获取时触发')
            # case = CMacdBbiCase()
            # case.run()
        except Exception as er:
            print(er)

    def websocketTrigger(self, data):
        try:
            jobj = json.loads(data)
            # print(f'{jobj["name"]} {jobj["command"]} {jobj["data"]}')
            vdata = jobj["data"]
            if jobj["command"] == 'load_module':
                self.loadModule(jobj["name"])
            elif jobj["command"] == 'run':
                module = self.loadModule(jobj["name"])
            elif jobj["command"] == 'run_repeat':
                module = self.loadModule(jobj["name"],True)

            cls = getattr(module, jobj["name"])
            obj = cls.create()
            return obj.run(vdata)
        except Exception as er:
            print(er)

    def loadModule(self, name,repeat=False):
        if name in sys.modules:
            if repeat:
                module = sys.modules[name]
            else:
                module = importlib.reload(sys.modules[name])
        else:
            module = importlib.import_module(name)
        return module

    def checkExit(self):
        flag = self.configs.getAppConfig('main', 'exit')
        if str.lower(flag) == 'true':
            return True
        else:
            return False
