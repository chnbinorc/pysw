import datetime
import os.path

import pandas as pd
import CCaseBase
import CConfigs
from CDataPrepare import CDataPrepare
from CTools import CTools
from CTushare import CTushare
import json
from CRealData import CRealData


class CMockDataCase(CCaseBase.CCaseBase):
    _obj = None

    @staticmethod
    def create():
        if CMockDataCase._obj is None:
            CMockDataCase._obj = CMockDataCase()
        return CMockDataCase._obj

    def __init__(self):
        super().__init__()
        self.cts = CTushare()
        self.qdate = datetime.datetime.now().strftime('%Y%m%d')
        self.realdata = CRealData.create()
        self.index = -1
        self.files = None
        self.configs = CConfigs.CConfigs()
        self.path = self.configs.getLocalDataPath()
        self.minutepath = self.configs.getDataConfig('local', 'minutepath')

    def pushNewData(self):
        print('开始模拟复盘')
        print('数据准备')
        case = CDataPrepare.create()
        case.run(self.qdate)
        print('数据已完成准备...')
        # rData = self.cts.getLastTradeDate()
        self.fpath = f'{self.path}/{self.minutepath}/{self.qdate}/'
        if not os.path.exists(self.fpath):
            print(f'路径不存在 {self.fpath}')
            return
        self.index = 0
        allfiles = os.listdir(self.fpath)
        self.files = sorted(allfiles, key=lambda file: os.path.getctime(os.path.join(self.fpath, file)))
        self.pushData()
        return

    def pushData(self):
        if self.index < 0:
            return
        if self.index >= len(self.files):
            return
        fname = os.path.join(self.fpath, self.files[self.index])
        db = pd.read_csv(fname, dtype={'code': str})
        self.realdata.push(db, False)
        self.index += 1
        return

    def mock(self, date=''):
        if self.qdate != date:
            self.qdate = date
            self.pushNewData()
        else:
            self.pushData()

    def run(self, vdata=''):
        # mock
        self.mock(vdata)

        cpre = CDataPrepare.create()
        predb = cpre.getData()
        #
        xdata = {
            'name': 'CMockDataCase',
            'command': 'CMockDataCase_ret',
            'data': ''
        }

        alldb = self.realdata.pull()
        if alldb is None:
            print('没有缓存数据')
            return json.dumps(xdata)
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

        retdb = alldf.drop_duplicates(subset=['code'], keep='last')
        retdb = pd.merge(retdb, predb, left_on='code', right_on='code', how='inner')
        retdb['turn_over'] = retdb.apply(lambda x: round(float(x.done_num) / float(x.float_share), 2), axis=1)
        retdb.rename(columns={'ts_code_x': 'code'}, inplace=True)
        retdb.sort_values(by=['ind_code'], inplace=True)
        # print(retdb.head(3))
        xdata['data'] = retdb.to_json(orient='table', index=False)
        # print(retdb.head(3))
        return json.dumps(xdata)

    def calLevel(self, price, open, close, num, money):
        levelW = 0 if float(open) == 0 else round((float(price) - float(open)) / float(open) * 100, 2)
        level = 0 if float(close) == 0 else round((float(price) - float(close)) / float(close) * 100, 2)
        done_num = round(float(num) / (100 * 10000), 2)
        done_money = round(float(money) / (10000 * 10000), 2)
        return [levelW, level, done_num, done_money]
