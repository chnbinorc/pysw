import CConfigs

class CCaseBase:

    def __init__(self):
        configs = CConfigs.CConfigs()
        path = configs.getLocalDataPath()
        self.allStockFile = '%s/allstock.csv' % path  # 股票信息
        self.stockBaseFile = '%s/stockbase.csv' % path  # 股票基本信息
        self.stockCompanyFile = '%s/stockcompany.csv' % path

        daypath = configs.getDataConfig('local', 'daypath')
        bakpath = configs.getDataConfig('local', 'bakpath')
        indicatorspath = configs.getDataConfig('local', 'indicatorspath')
        minutepath = configs.getDataConfig('local', 'minutepath')

        self.stockPriceDayPath = '{0}/{1}/'.format(path, daypath)  # 日线行情数据
        self.stockBakDayPath = '{0}/{1}/'.format(path, bakpath)  # 备用行情数据路径
        self.stockIndiPath = '{0}/{1}/'.format(path, indicatorspath)  # 日线指标分析数据路径
        self.stockPriceMinPath = '{0}/{1}/'.format(path, minutepath)  # 日线分钟行情数据路径
        return

    # 准备数据
    def readyData(self, data):
        return

    # 测试
    def test(self):
        return

    # 评估结果
    def result(self):
        return

    # 运作
    def run(self, data):
        return
