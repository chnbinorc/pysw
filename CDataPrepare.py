import datetime
import os

import pandas as pd
from pypinyin import pinyin, Style

import CCaseBase
import Constants
import CConfigs
from CTools import CTools
from CTushare import CTushare
import json


# 准备数据

class CDataPrepare(CCaseBase.CCaseBase):
    _obj = None

    @staticmethod
    def create():
        if CDataPrepare._obj is None:
            CDataPrepare._obj = CDataPrepare()
        return CDataPrepare._obj

    def __init__(self):
        super().__init__()
        self.db = pd.DataFrame()
        self.stockIndicatorsPath = '{0}/indicators/'.format(CConfigs.dataPath)
        self.cts = CTushare()
        self.qdate = datetime.datetime.now().strftime('%Y%m%d')
        self.allbakdb = pd.DataFrame()
        self.avgbak = pd.DataFrame()

    def getAllBakData(self):
        count = 0
        tradedate = self.cts.getPreTradeDate(self.qdate)
        while count < 10:
            file = f'{self.stockBakDayPath}{tradedate}.csv'
            if os.path.exists(file):
                sub = pd.read_csv(file)
                if self.allbakdb.shape[0] == 0:
                    self.allbakdb = sub
                else:
                    self.allbakdb = pd.concat([self.allbakdb, sub], ignore_index=True, axis=0)
            tradedate = self.cts.getPreTradeDate(tradedate)
            count += 1

        s = self.allbakdb.groupby('ts_code')['turn_over'].mean()
        self.avgbak = s.to_frame(name='turn_over_avg')
        self.avgbak.reset_index(inplace=True)
        self.avgbak['turn_over_avg'] = self.avgbak.apply(lambda x: round(float(x.turn_over_avg), 2), axis=1)
        # self.avgbak['ts_code'] = self.avgbak.apply(lambda x: CTools.getOnlyCode(x.ts_code), axis=1)
        # print(self.avgbak.head(3))

    def getData(self):
        if self.db.shape[0] == 0:
            self.run('')
        return self.db

    def getPinyin(self, text):
        try:
            # 获取每个字的拼音首字母（自动处理多音字取第一个读音）
            initials = [p[0][0].upper() for p in pinyin(text, style=Style.FIRST_LETTER)]
            return ''.join(initials)
        except:
            # 异常处理：遇到非汉字字符时保留原字符
            return ''.join([c.upper() if not '\u4e00' <= c <= '\u9fff' else '' for c in text])

    def forIndex(self):
        df = self.cts.queryStockbaseBoardCust(Constants.MAIN_CONDITION_STR)
        dk = df['ts_code']
        da = self.cts.queryBakBasic("industry != '银行'")
        Bool = da.name.str.contains("ST")  # 去除ST
        da = da[~Bool]
        da = pd.merge(da, dk, left_on='ts_code', right_on='ts_code', how='inner')
        alldb = None
        for i, row in self.cts.getThsIndex().iterrows():
            file = f'data/ths_member/{row.ts_code}.csv'
            if not os.path.exists(file):
                # print(f'文件不存在 {file} {row["name"]}')
                continue
            dbmembers = pd.read_csv(file)
            dbmembers['ind_code'] = dbmembers.apply(lambda x: row["ts_code"], axis=1)
            dbmembers['ind_name'] = dbmembers.apply(lambda x: row["name"], axis=1)

            if alldb is None:
                alldb = dbmembers
            else:
                alldb = pd.concat([alldb, dbmembers], ignore_index=True, axis=0)

        tmpdb = pd.merge(da, alldb, left_on='ts_code', right_on='con_code', how='inner')
        tmpdb = pd.merge(tmpdb, self.avgbak, left_on='ts_code_x', right_on='ts_code', how='inner')
        tmpdb.drop_duplicates(subset='ts_code_x', inplace=True)
        tmpdb.rename(columns={'ts_code_x': 'code'}, inplace=True)
        self.db = tmpdb[
            ['code', 'total_mv', 'float_mv', 'name', 'ind_code', 'ind_name', 'turn_over_avg', 'float_share']]
        self.db['code'] = self.db.apply(lambda x: CTools.getOnlyCode(x.code), axis=1)
        self.db['pinyin'] = self.db.apply(lambda x: self.getPinyin(x.ind_name), axis=1)
        self.db['risecount'] = self.db.apply(lambda x: self.calHighPriceCount(x.code), axis=1)
        self.db['pricelevel'] = self.db.apply(lambda x: self.calPriceLevel(x.code), axis=1)
        # print(self.db.head(3))

    # 计算个股价格的四分位
    def calPriceLevel(self, code):
        scode = CTools.getBackCode(code)
        file = f'{self.stockIndiPath}{scode}.csv'
        if not os.path.exists(file):
            print(file)
            return -1;
        db = pd.read_csv(file).tail(Constants.ONE_MONTH_DAYS * 3 + 15)
        # print(db.iloc[0]['trade_date'])
        tmpdb = db.tail(1)
        price = tmpdb.iloc[0]['close']
        qua = db['close'].quantile([0.25, 0.5, 0.75])
        ret = 0
        idx = 1
        for it in qua:
            ret = idx if price > it else ret
            idx += 1
        return ret

    # 计算个股最近10天涨幅超过4.5的次数
    def calHighPriceCount(self, code):
        scode = CTools.getBackCode(code)
        file = f'{self.stockIndiPath}{scode}.csv'
        count = -1
        if not os.path.exists(file):
            print(file)
            return count;
        else:
            db = pd.read_csv(file).tail(10)
            db['rise'] = db.apply(
                lambda x: round((float(x.close) - float(x.pre_close)) / float(x.pre_close) * 100, 3), axis=1)
            count = db['rise'][db['rise'] > 4.5].count()
        return count

    # def isValidDate(self, date_str, date_format):
    #     try:
    #         datetime.datetime.strptime(date_str, date_format)
    #         return True
    #     except ValueError:
    #         return False

    def run(self, data):
        if self.isValidDate(data, '%Y%m%d'):
            self.qdate = data
        self.getAllBakData()
        xdata = {
            'name': 'CDataPrepare',
            'command': 'CDataPrepare_ret',
            'data': 'ok'
        }
        self.forIndex()
        return json.dumps(xdata)
        # print(self.db.shape[0])
        # print(self.db.head(5))
        # 准备 行业，总股本，流通股本
        # df = self.cts.filterStocks()
