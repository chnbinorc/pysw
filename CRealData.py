import threading

import pandas as pd
import datetime
import CConfigs as configs
import os
import threading


class CRealData:
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

    def push(self, df):
        self.lock.acquire()
        self.newData = df
        minute = datetime.datetime.now().minute
        if self.minute != minute:
            self.saveData()
            self.minute = minute
        self.lock.release()
        if not self.fnTrigger is None:
            self.fnTrigger()

    def pull(self):
        self.lock.acquire()
        bak = self.newData.copy()
        self.lock.release()
        return bak

    def saveData(self):
        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d')
        filepath = '{0}/{1}'.format(self.minutePath, date)
        if not os.path.exists(filepath):
            os.mkdir(filepath)
        filename = '{0}/{1}_{2}.csv'.format(filepath, now.hour, now.minute)
        if not self.newData is None:
            self.newData.to_csv(filename, index=False, encoding="utf_8_sig")
