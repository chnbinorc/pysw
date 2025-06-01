import os.path
import datetime

import CConfigs
from CTools import CTools
from ICase import ICaseRun


class CCaseBase(ICaseRun):

    def __init__(self):
        configs = CConfigs.CConfigs()
        path = configs.getLocalDataPath()
        self.tools = CTools()
        self.allStockFile = '%s/allstock.csv' % path  # 股票信息
        self.stockBaseFile = '%s/stockbase.csv' % path  # 股票基本信息
        self.stockCompanyFile = '%s/stockcompany.csv' % path

        daypath = configs.getDataConfig('local', 'daypath')
        bakpath = configs.getDataConfig('local', 'bakpath')
        indicatorspath = configs.getDataConfig('local', 'indicatorspath')
        minutepath = configs.getDataConfig('local', 'minutepath')
        predictpath = configs.getDataConfig('local','predict')
        temppath = configs.getDataConfig('local','temp')

        self.stockPriceDayPath = '{0}/{1}/'.format(path, daypath)  # 日线行情数据
        self.stockBakDayPath = '{0}/{1}/'.format(path, bakpath)  # 备用行情数据路径
        self.stockIndiPath = '{0}/{1}/'.format(path, indicatorspath)  # 日线指标分析数据路径
        self.stockPriceMinPath = '{0}/{1}/'.format(path, minutepath)  # 日线分钟行情数据路径
        self.stockPredictPath = f'{path}/{predictpath}/'  # 预测数据路径
        self.stockTempPath = f'{path}/{temppath}/'  # 临时目录
        if not os.path.exists(self.stockPredictPath):
            os.mkdir(self.stockPredictPath)
        if not os.path.exists(self.stockTempPath):
            os.mkdir(self.stockTempPath)

    def isValidDate(self, date_str, date_format):
        try:
            datetime.datetime.strptime(date_str, date_format)
            return True
        except ValueError:
            return False

    # 准备数据
    def readyData(self):
        return

    # 测试
    def test(self):
        return

    # 评估结果
    def result(self):
        return

    # 运作
    def run(self,data):
        print('CCaseBase')
        return
