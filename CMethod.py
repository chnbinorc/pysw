import datetime
import threading
import time
import pandas as pd
import os
import numpy as np

import CConfigs
from CCommon import log, warning, error

from ClsMThreadPool import ClsMTPool

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 10000)
pd.set_option('display.width', 10000)


class CMethod:
    def __init__(self):
        self.configs = CConfigs.CConfigs()
        self.mttool = ClsMTPool.Create()
        return

    def run(self):
        return

    def checkExit(self):
        flag = self.configs.getAppConfig('main','exit')
        if str.lower(flag) == 'true':
            return True
        else:
            return False
