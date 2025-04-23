import CCaseBase
import CRealData
from CTushare import CTushare


class CBoardCase(CCaseBase.CCaseBase):
    _obj = None

    @staticmethod
    def create():
        if CBoardCase._obj is None:
            CBoardCase._obj = CBoardCase()
        return CBoardCase._obj

    def __init__(self):
        self.cts = CTushare()

    def run(self,data):
        cdata = CRealData.CRealData.create()
        alldb = cdata.pull()
        if alldb is None:
            print('没有缓存数据')
            return 'CBoardCase.run_rep'
        alldf = alldb.copy().drop(
            columns=['buy1_num', 'buy1_price', 'buy2_num', 'buy2_price', 'buy3_num', 'buy3_price', 'buy4_num',
                     'buy4_price',
                     'buy5_num', 'buy5_price',
                     'sell1_num', 'sell1_price', 'sell2_num', 'sell2_price', 'sell3_num', 'sell3_price', 'sell4_num',
                     'sell4_price', 'sell5_num', 'sell5_price'])

        alldf[['levelW', 'level', 'done_num', 'done_money']] = alldb.apply(
            lambda x: self.calLevel(x.price, x.open, x.close, x.done_num, x.done_money), axis=1,
            result_type="expand")
        alldf.rename(columns={'buy1': 'buy', 'sell1': 'sell'}, inplace=True)
        print(alldf.query('level > 0.09'))
        return 'CBoardCase.run_rep'

    def calLevel(self, price, open, close, num, money):
        levelW = 0 if float(open) == 0 else round((float(price) - float(open)) / float(open), 4)
        level = 0 if float(close) == 0 else round((float(price) - float(close)) / float(close), 4)
        done_num = round(float(num) / 100, 4)
        done_money = round(float(money) / 10000, 4)
        return [levelW, level, done_num, done_money]