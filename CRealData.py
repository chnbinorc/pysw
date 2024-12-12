import pandas as pd
import datetime
import CConfigs as configs
import os


class CRealData:
    def __init__(self, fncallback):
        self.datas = [None, None, None]
        self.newData = None
        self.fnTrigger = fncallback
        self.configs = configs.CConfigs()
        mPath = self.configs.getLocalDataPath()
        if not os.path.exists(mPath):
            os.mkdir(mPath)
        self.minutePath = mPath + '/' + self.configs.getDataConfig('local', 'minutepath') + '/'
        if not os.path.exists(self.minutePath):
            os.mkdir(self.minutePath)

    def push(self, df):
        self.newData = df
        self.updateDatas()
        if not self.fnTrigger is None:
            self.fnTrigger(self.newData)

    def updateDatas(self):
        sec = datetime.datetime.now().second
        if sec < 20:
            self.datas[0] = self.newData
            self.saveData()
        elif sec >= 20 < 40:
            self.datas[1] = self.newData
        else:
            self.datas[2] = self.newData

    def saveData(self):
        now = datetime.datetime.now()
        date = now.strftime('%Y%m%d')
        filepath = '{0}/{1}'.format(self.minutePath, date)
        if not os.path.exists(filepath):
            os.mkdir(filepath)
        filename = '{0}/{1}_{2}.csv'.format(filepath, now.hour, now.minute)
        if not self.datas[0] is None:
            self.datas[0].to_csv(filename, index=False, encoding="utf_8_sig")
