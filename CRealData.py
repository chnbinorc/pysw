import threading

import pandas as pd
import datetime
import CConfigs as configs
import os
import threading
from CCommon import log, warning, error

class CRealData:
    realdata = None

    @staticmethod
    def create(fncallback=None):
        if CRealData.realdata is None:
            CRealData.realdata = CRealData(fncallback)
        return CRealData.realdata

    def __init__(self, fncallback):
        self.newData = None
        self.lock = threading.Lock()
        self.fnTrigger = fncallback
        self.configs = configs.CConfigs()
        mPath = self.configs.getLocalDataPath()
        if not os.path.exists(mPath):
            os.mkdir(mPath)
        self.minutePath = mPath + '/' + self.configs.getDataConfig('local', 'minutepath') + '/'

        if not os.path.exists(self.minutePath):
            os.mkdir(self.minutePath)
        self.minute = -1

    def push(self, df,write=True):
        try:
            if not write:
                self.newData = df
            else:
                self.lock.acquire()
                minute = datetime.datetime.now().minute
                if self.minute != minute:
                    self.saveData()
                    self.minute = minute
                    self.newData = df
                else:
                    self.newData = pd.concat([self.newData, df], ignore_index=True, axis=0)
                self.lock.release()
        except Exception as er:
            if self.lock.locked():
                self.lock.release()
            error(er)

        if self.fnTrigger is not None:
            self.fnTrigger()

    def pull(self):
        # self.lock.acquire()
        # bak = self.newData.copy()
        # self.lock.release()
        return self.newData

    def saveData(self):
        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d')
        filepath = '{0}/{1}'.format(self.minutePath, date)
        if not os.path.exists(filepath):
            os.mkdir(filepath)
        filename = '{0}/{1}_{2}.csv'.format(filepath, now.hour, now.minute)
        if not self.newData is None:
            self.newData.to_csv(filename, index=False, encoding="utf_8_sig")
