
import os.path
import CConfigs

class CMarket:
    def __init__(self):
        self.configs = CConfigs.CConfigs()
        self.path = self.configs.getLocalDataPath()

        temppath = self.configs.getDataConfig('local', 'temp')
        self.stockTempPath = f'{self.path}/{temppath}/'  # 临时目录
        if not os.path.exists(self.stockTempPath):
            os.mkdir(self.stockTempPath)

