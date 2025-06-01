import datetime
import time

import pandas as pd
import os
import numpy as np
from pypinyin import pinyin, Style

import CTools
import Constants
from CCatchDragonCase import CCatchDragonCase
from CCommon import log, warning, error
import CStrategy as strate
import CTools as ctools
import CTushare as cts
from CDataPrepare import CDataPrepare
from CDayWork import CDayWork
from CMacdBbiCaseStock import CMacdBbiCaseStock
from CMacdBbiCase import CMacdBbiCase
from CIndicatorAI import CIndicatorAI
from CStockMarket import CStockMarket
from CWebSocket import CWebSocket

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 10000)
pd.set_option('display.width', 10000)


class CTestMethod:
    def __init__(self):
        self.cts = cts.CTushare()
        self.strate = strate.CStrategy()
        self.tools = ctools.CTools()
        self.bbicase = CMacdBbiCase()
        return

    # region  ============日终任务============

    # 日终任务
    def dayWork(self):
        daywork = CDayWork(None)
        daywork.run()

    # 近3个交易日产生的双金叉个股
    def analyDay(self):
        # self.cts.updateTHSIndex()

        db = self.bbicase.analy()
        # print(db)
        index = 'N'
        market = CStockMarket()
        dbind = self.runStockIndexStat(self.cts.getPreTradeDate(), index)
        # dbths = self.cts.getIndexThsMembers('885918.TI')
        db[['ind_code', 'ind_range', 'ind_name']] = db.apply(
            lambda x: self.mergIndex2Stock(x.ts_code, dbind, index), axis=1, result_type="expand")
        db.sort_values(by='ind_range', ascending=False, inplace=True)
        print(db)

    def analy_all_bbi(self):
        fname = 'd:/temp/analy_all_bbi.csv'
        if not os.path.exists(fname):
            db = self.bbicase.analy_all_bbi()
            db.to_csv(fname, index=False)
        else:
            db = pd.read_csv(fname)
        dk = db.query('label in (0,1,2,4,7,9) and range > 0.1')
        return dk

    def mergIndex2Stock(self, tscode, dbind, index='N'):
        db = self.cts.getStockIndex(tscode, index)
        # print(db)
        level = -10
        retstr = None
        for i, row in db.iterrows():
            dk = dbind.query(f'ts_code == "{row.ind_code}"')
            if dk.shape[0] == 0:
                # print(row)
                continue
            if dk.iloc[0].level > level:
                level = dk.iloc[0].level
                retstr = [dk.iloc[0].ts_code, dk.iloc[0].level, dk.iloc[0]["name"]]
        return retstr

    # 实时板块统计
    def runStockIndexStat(self, date, index='N'):
        # 概念成分
        dfIndex = self.cts.getIndexTHS(index)
        # 当前实时数据
        # alldf = self.realdata.pull()
        alldb = pd.read_csv(f'data/minute/{date}/14_57.csv', dtype={'code': str})
        alldf = self.trans2LevelForm(alldb)
        alldf['code'] = alldf.apply(lambda x: self.tools.getBackCode(x.code), axis=1)
        db_all = alldf[['code', 'level']]
        dfIndex['level'] = dfIndex.apply(self.calLevel, db_all=db_all, axis=1)
        db = dfIndex.query('level != 0')[['ts_code', 'level', 'count', 'name']]
        db.sort_values(by='level', ascending=False, inplace=True)
        # print(db)
        return db

    def calLevel(self, row, db_all):
        fname = f'{self.cts.ths_member}{row.ts_code}.csv'
        perlevel = 0
        if os.path.exists(fname):
            dk = pd.read_csv(fname)
            dk = pd.merge(dk, db_all, how='inner', left_on='con_code', right_on='code')
            if dk.shape[0] > 0:
                perlevel = round(dk['level'].mean(), 4)
            else:
                perlevel = 0
        return perlevel

    def trans2LevelForm(self, data):
        alldf = data.copy().drop(
            columns=['buy1_num', 'buy1_price', 'buy2_num', 'buy2_price', 'buy3_num', 'buy3_price', 'buy4_num',
                     'buy4_price',
                     'buy5_num', 'buy5_price',
                     'sell1_num', 'sell1_price', 'sell2_num', 'sell2_price', 'sell3_num', 'sell3_price', 'sell4_num',
                     'sell4_price', 'sell5_num', 'sell5_price'])

        alldf[['levelW', 'level', 'done_num', 'done_money']] = data.apply(
            lambda x: self.calLevelsrc(x.price, x.open, x.close, x.done_num, x.done_money), axis=1,
            result_type="expand")
        alldf.rename(columns={'buy1': 'buy', 'sell1': 'sell'}, inplace=True)
        return alldf

    def calLevelsrc(self, price, open, close, num, money):
        levelW = 0 if float(open) == 0 else round((float(price) - float(open)) / float(open), 4)
        level = 0 if float(close) == 0 else round((float(price) - float(close)) / float(close), 4)
        done_num = round(float(num) / 100, 4)
        done_money = round(float(money) / 10000, 4)
        return [levelW, level, done_num, done_money]

    # endregion

    # 生成macdbbi双金叉模型数据，除非需重新计算，运行一次就好
    def genMacdBbiModel(self):
        case = CMacdBbiCase()
        case.genMacdBBIModel()
        cia = CIndicatorAI()
        cia.test_kshape(True)
        cia.test_make_kshape_day_10()

    # region 测试代码

    # 多头并列
    def test_longPosition(self):
        return

    # 打板战法
    def test_checkData(self):
        # fpath = 'data/minute/20250127/'
        # files = os.listdir(fpath)
        # alldb = None
        # for fl in files:
        #     fname = os.path.join(fpath,fl)
        #     db = pd.read_csv(fname).query('code == 600807')
        #     alldb = db if alldb is None else pd.concat([alldb, db], ignore_index=True, axis=0)
        # alldb.sort_values(by='time',inplace=True)
        # print(alldb)

        # fname = 'data/temp/fake_buy_20250127.csv'
        # db = pd.read_csv(fname).query('flag == True').sort_values(by='income')
        # print(db)

        # retdb = pd.DataFrame()
        # db = self.cts.filterStocks()
        # print(f'总数：{db.shape[0]}')
        # count = 1
        # for i, row in db.iterrows():
        #     fname = f'data/indicators/{row.ts_code}.csv'
        #     subdb = pd.read_csv(fname)
        #     subdb['topflag'] = subdb.apply(lambda x: 1 if round((x.close - x.pre_close) / x.pre_close, 4) > 0.09 else 0,
        #                                    axis=1)
        #     dk = subdb.query('topflag == 1')
        #     for j, it in dk.iterrows():
        #         d2 = self.cts.getPreTradeDate(it.trade_date)
        #         d1 = self.cts.getPreTradeDate(d2)
        #         db1 = dk.query(f'trade_date == {d1}')
        #         db2 = dk.query(f'trade_date == {d2}')
        #         if db1.shape[0] == 0 and db2.shape[0] == 1:
        #             retdb = retdb.append(it, ignore_index=True)
        #     count += 1
        #     if count % 50 == 0:
        #         print(count)
        # retdb[['trade_date']] = retdb[['trade_date']].astype(int)
        # print(retdb)
        # retdb.to_csv('data/temp/all_top_analy.csv',index=False)

        buydb = retdb = pd.DataFrame()
        retdb = pd.read_csv('data/temp/all_top_analy.csv')
        print(retdb.shape[0])
        count = 0
        for i, row in retdb.iterrows():
            fname = f'data/indicators/{row.ts_code}.csv'
            db = pd.read_csv(fname)
            next = self.cts.getNextTradeDate(row.trade_date)
            flag = True
            while flag:
                qdb = db.query(f'trade_date == {next}')
                if qdb.shape[0] > 0 and qdb.iloc[0].high != qdb.iloc[0].low:
                    buydb = buydb.append(row, ignore_index=True)
                    flag = False
                elif qdb.shape[0] == 0:
                    flag = False
                next = self.cts.getNextTradeDate(next)
            if count % 20 == 0:
                print(count)
            count += 1
        buydb.to_csv('data/temp/all_top_analy_buy.csv', index=False)

    def test_boardwin(self):
        # db = pd.read_csv('data/temp/all_top_analy_buy.csv',dtype={'trade_date': int})
        # db['winflag'] = db.apply(lambda x: self.test_checkwin(db,x),axis=1)
        # print(db)
        # all = db.shape[0]
        # print(all)
        # win = db.query('winflag == True').shape[0]
        # los = db.query('winflag == False').shape[0]
        # print(f'win:{win},los:{los} , rate: {win / all}')
        # db.to_csv('data/temp/all_top_analy_buy.csv',index=False)
        db = pd.read_csv('data/temp/all_top_analy_buy.csv', dtype={'trade_date': int})
        print(db.query('winflag == False').head(100))

    def test_checkwin(self, db, row):
        next = self.cts.getNextTradeDate(row.trade_date)
        fname = f'data/indicators/{row.ts_code}.csv'
        stockdb = pd.read_csv(fname).query(f'trade_date >= {next}')
        close = 0
        # 止盈5个点，止损3个点
        winrate = 0
        for i, it in stockdb.iterrows():
            if close == 0:
                if it.high == it.low:
                    continue
                else:
                    close = it.close
                    continue
            rate = round((it.close - close) / close, 4)
            if rate > winrate:
                winrate = rate
            else:
                if winrate - rate > 0.03:
                    winrate = rate
                    break
            if winrate > 0.08:
                break
        return winrate > 0

    def test_realdata(self):
        market = CStockMarket()
        market.realDataTrigger()

    def test_draw_std(self):
        cia = CIndicatorAI()
        cia.test_draw_std()

    # 检查个股某个点的label情况
    def test_stat5(self):
        fname = f'{self.strate.stockIndicatorsPath}002192.SZ.csv'
        pp = pd.read_csv(fname).query('trade_date < 20240725').tail(11)

        diff = pd.Series(pp['BBI'])
        diff.loc[len(diff)] = pp.iloc[10]['BBI']
        print(diff)
        arr = np.array(diff.values).reshape(-1, 12, 1)
        cia = CIndicatorAI()
        labels = cia.fit_kshape(arr)
        print(labels)

    def test_getRealPrice(self):
        market = CStockMarket()
        df = self.cts.filterStocks()
        dk = market.getStocksRealPrices(df)
        print(dk)

    def test_class_abc(self):
        case = CMacdBbiCase()
        case.run()

    def test_webcoket(self):
        web = CWebSocket()
        web.start()

    def test_ths_no(self):
        # self.cts.updateTHSIndex()
        # now = datetime.datetime.now().strftime('%Y%m%d')
        # start = self.tools.getDateDelta(now, -Constants.ONE_YEARE_DAYS)
        # log(f'开始更新板块资金流向（同花顺接口')
        # self.cts.updateCntMoneyFlowTHS(start, now)
        self.cts.updateThsNo()

        # now = datetime.datetime.now().strftime('%Y%m%d')
        # start = self.tools.getDateDelta(now, int(-Constants.ONE_YEARE_DAYS / 2))
        # next = start
        # while int(next)<int(now):
        #     if self.cts.isTradeDate(next):
        #         self.cts.updateMoneyFlowAll(next)
        #     next = CTools.CTools.getDateDelta(next,1)
        #     time.sleep(0.1)

    # 行业资金分析

    # 板块资金分析

    # 个股资金分析
    def test_ths_moneyflow(self):
        # date = self.cts.getPreTradeDate()
        # file = f'data/moneyflow_ths/all/' + str(date)
        # db = pd.read_csv(file)
        # db.sort_values(by=['net_amount'], ascending=False,inplace=True)
        # db1 = db.head(50)
        # print(db1)
        # print('=======================================================')
        # print(' ')
        # print('=======================================================')
        # db2 = db.tail(50)
        # print(db2)
        ret = self.cts.getStockIndex2('300674.SZ', 'N')
        print(ret)

    def test_ths_ind(self):
        db = self.cts.filterStocks2('float_mv < 120')
        print(db.shape[0])
        db = self.cts.filterStocks2('float_mv >= 120')
        print(db.shape[0])
        db = self.cts.filterStocks2('float_mv > 50 and float_mv < 70')
        print(db.shape[0])

    def getPinyin(self, text):
        try:
            # 获取每个字的拼音首字母（自动处理多音字取第一个读音）
            initials = [p[0][0].upper() for p in pinyin(text, style=Style.FIRST_LETTER)]
            return ''.join(initials)
        except:
            # 异常处理：遇到非汉字字符时保留原字符
            return ''.join([c.upper() if not '\u4e00' <= c <= '\u9fff' else '' for c in text])

    def test_ths_ind_type(self, date=datetime.datetime.now().strftime('%Y%m%d')):
        # db = self.cts.filterStocks()
        # print(db.shape[0])
        # print(self.cts.getThsIndex())
        # return
        # cpre = CDataPrepare.create()
        # db = cpre.getData()

        print(self.getPinyin('自贸区'))

        return

        df = self.cts.queryStockbaseBoardCust(Constants.MAIN_CONDITION_STR)
        dk = df['ts_code']

        da = self.cts.queryBakBasic("industry != '银行'")
        Bool = da.name.str.contains("ST")  # 去除ST
        da = da[~Bool]
        da = pd.merge(da, dk, left_on='ts_code', right_on='ts_code', how='inner')
        idx = 0
        alldb = None
        for i, row in self.cts.getThsIndex().iterrows():
            # if idx < 5:
            #     idx += 1
            #     continue
            # print(f'{row["ts_code"]} {row["name"]}')
            file = f'data/ths_member/{row.ts_code}.csv'
            if not os.path.exists(file):
                print(f'文件不存在 {file} {row["name"]}')
                continue
            dbmembers = pd.read_csv(file)
            subdb = pd.merge(da, dbmembers, left_on='ts_code', right_on='con_code', how='inner')
            if subdb.shape[0] == 0:
                continue
            subdb['rate'] = subdb.apply(lambda x: round((x.close - x.pre_close) / x.pre_close, 3), axis=1)
            subdb['con_code'] = subdb.apply(lambda x: row["ts_code"], axis=1)
            subdb['con_name'] = subdb.apply(lambda x: row["name"], axis=1)
            subdb.sort_values(by='rate', inplace=True, ascending=False)
            # ret = subdb.query('rate > 0.09')
            ret = subdb.head(3)
            if ret.shape[0] > 0:
                if alldb is None:
                    alldb = ret.copy()
                else:
                    alldb = pd.concat([alldb, ret], ignore_index=True, axis=0)
            # subdb.sort_values(by=['float_mv'],inplace=True)
            # print(subdb[['trade_date','ts_code_x','total_mv','float_mv','rate','name']])
            # break
        if not alldb is None:
            print(alldb[['trade_date', 'ts_code_x', 'total_mv', 'float_mv', 'rate', 'name', 'con_code', 'con_name']])

    # 每日交易数据统计
    def test_trade_count(self):
        case = CCatchDragonCase.create()
        sdate = '20250518'
        start = self.cts.getNextTradeDate(sdate)
        now = datetime.datetime.now().strftime('%Y%m%d')
        alldb = None
        while int(start) <= int(now):
            # case.qdate = start
            db = case.getData(start)
            if alldb is None:
                grouped = db.groupby('ind_name')
                itemcount = grouped.size().reset_index(name='counts')
                itemcount.sort_values(by=['ind_name'],inplace=True)
                alldb = pd.DataFrame(itemcount)
            alldb[f'{start}'] = alldb.apply(lambda x: self.count_rise_greater_than_5(x,db),axis=1)
            start = self.cts.getNextTradeDate(start)
        cols=list(alldb.columns)
        cols.append(cols.pop(1))
        cols.append(cols.pop(0))
        alldb=alldb[cols]
        print(alldb)
        # d1 = db.query('rate > 0.09')
        # group1 = d1.groupby(['ind_code']).size()
        # t = group1.to_frame(name='count').rename_axis('ind_code').reset_index()
        # print(t)

    def count_rise_greater_than_5(self,row,db):
        qdb = db.query(f'ind_name == "{row.ind_name}" and rate > 0.05')
        return qdb.shape[0]


    # 每日涨停分析
    def test_rise_top(self):
        pre = CDataPrepare.create()
        dbpre = pre.getData()
        db = self.cts.filterStocks()
        columns = ['s0', 's1', 's2', 's3', 's4', 'code']
        retdb = pd.DataFrame(columns=columns)
        for i, row in db.iterrows():
            diff = self.calRiseTop(row)
            retdb.loc[len(retdb)] = diff.values
        da = retdb.query('s2 > 0.09 and s0 < 0.03 and s1 < 0.03 ')
        da = pd.merge(da,dbpre, left_on='code', right_on='code', how='inner')
        da.sort_values(by=['ind_code'], inplace=True)
        print(da)

    def calRiseTop(self, row):
        file = f'data/indicators/{row.ts_code}.csv'
        if not os.path.exists(file):
            return [row.ts_code, 0, 0, 0, 0, 0]
        dk = pd.read_csv(file)
        da = dk.tail(5)
        diff = da.apply(lambda x: round((x.close - x.pre_close) / x.pre_close, 2), axis=1)
        diff.loc[len(diff)] = CTools.CTools.getOnlyCode(row.ts_code)
        return diff

    # endregion
