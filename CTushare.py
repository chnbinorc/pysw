# -*- coding: UTF-8 -*-
import tushare as ts
import pandas as pd
import os
import datetime
import time

import CConfigs
import CConfigs as Configs
import Constants
import Constants as Constatans
from CTools import CTools
from CCommon import log

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 10000)
pd.set_option('display.width', 10000)

'''
积分过期查询先用接口实现，后续再做网页版
https://tushare.pro/document/1?doc_id=307
'''

'''
tushare ，数据源
'''


class CTushare:
    tsToken = ''
    pro = None

    def __init__(self):
        Configs = CConfigs.CConfigs()
        if not bool(CTushare.tsToken):
            ts.set_token(Configs.getTushareToken())
            CTushare.pro = ts.pro_api()
            CConfigs.dataPath = Configs.getLocalDataPath()
            if not os.path.exists(CConfigs.dataPath):
                os.mkdir(CConfigs.dataPath)
            CTushare.tsToken = Configs.getTushareToken()
        self.allStockFile = '%s/allstock.csv' % CConfigs.dataPath  # 股票信息
        self.stockBaseFile = '%s/stockbase.csv' % CConfigs.dataPath  # 股票基本信息
        self.stockCompanyFile = '%s/stockcompany.csv' % CConfigs.dataPath
        daypath = Configs.getDataConfig('local', 'daypath')
        bakpath = Configs.getDataConfig('local', 'bakpath')
        self.stockPriceDayPath = '{0}/{1}/'.format(CConfigs.dataPath, daypath)  # 日线行情数据
        self.stockBakDayPath = '{0}/{1}/'.format(CConfigs.dataPath, bakpath)  # 备用行情数据路径
        moneyflow = Configs.getDataConfig('local', 'moneyflow')
        self.moneyFlowPath = f'{CConfigs.dataPath}/{moneyflow}/'
        if not os.path.exists(self.moneyFlowPath):
            os.mkdir(self.moneyFlowPath)

    # region ======================   基本接口    ======================

    # 积分到期查询
    def qryPoints(self):
        print(CTushare.pro.user(token=CTushare.tsToken))

    # 获取所有股票信息
    def getAllSockInfo(self, reload=False):
        if (reload):
            df = CTushare.pro.stock_basic(
                is_hs='',
                list_status='',
                exchange='',
                ts_code='',
                market='',
                # limit='',
                # offset='',
                name='',
                fields='ts_code,symbol,name,area,industry,fullname,enname,cnspell,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')

            df.to_csv(self.allStockFile, index=False, encoding="utf_8_sig")
        df = pd.read_csv(self.allStockFile)
        return df

    # #中小板块
    # # df[df['market']=='中小板']
    # log(df[df['market']=='中小板'])
    # #主板
    # # df[df['market']=='主板']
    # log(df[df['market']=='主板'])
    # #创业板
    # # df[df['market']=='创业板']
    # log(df[df['market']=='创业板'])
    # #北交所
    # # df[df['market']=='北交所']
    # log(df[df['market']=='北交所'])
    # #科创板
    # # df[df['market']=='科创板']
    # log(df[df['market']=='科创板'])

    # 按行业

    # log(df.groupby('industry').size())

    # 获取股票基本信息
    def getStockBaseInfo(self):
        if not os.path.exists(self.stockBaseFile):
            self.updateAllStockBase()
        return pd.read_csv(self.stockBaseFile)

    # 更新所有股票基本信息
    def updateAllStockBase(self):
        df = CTushare.pro.stock_basic(
            is_hs='',
            list_status='',
            exchange='',
            ts_code='',
            market='',
            # limit='',
            # offset='',
            name='',
            fields='ts_code,symbol,name,area,industry,fullname,enname,cnspell,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')
        df.to_csv(self.stockBaseFile, index=False, encoding="utf_8_sig")

    # 日线数据
    # stockCode: 股票代码
    # tradeDate: 交易日期
    def dailyDataOneBak(self, stockCode, tradeDate):
        df = CTushare.pro.bak_daily(ts_code=stockCode,
                                    trade_date=tradeDate,
                                    fields='ts_code,trade_date,name,pct_change,close,change,open,high,low,pre_close,vol_ratio,turn_over,swing,vol,amount,selling,buying,total_share,float_share,pe,industry,area,float_mv,total_mv,avg_price,strength,activity,avg_turnover,attack,interval_3,interval_6')
        return df

    # 根据条件获取股票基本信息
    # tp: 股票分类，枚举类型
    def getStockBaseBoard(self, tp):
        df = pd.read_csv(self.stockbase)
        if tp == Constants.BIG_BOARD_TYPE_0:
            return df[df['market'] == '中小板']
        elif tp == Constants.BIG_BOARD_TYPE_1:
            return df[df['market'] == '主板']
        elif tp == Constants.BIG_BOARD_TYPE_2:
            return df[df['market'] == '创业板']
        elif tp == Constants.BIG_BOARD_TYPE_3:
            return df[df['market'] == '北交所']
        elif tp == Constants.BIG_BOARD_TYPE_4:
            return df[df['market'] == '科创板']
        else:
            return df

    # 自定义条件查询
    # condition: 查询条件
    def queryStockbaseBoardCust(self, condition):
        df = pd.read_csv(self.stockBaseFile).query('list_date < 20220101')
        return df.query(condition)

    # 交易日历
    # exchange: 市场类别
    # start: 开始日期
    # end: 结束日期
    # flag: 强制更新标记
    def getTradeCal(self, exchange, start, end, flag=False):
        filepath = CConfigs.dataPath + '/calendar.csv'
        if not os.path.exists(CConfigs.dataPath):
            os.mkdir(CConfigs.dataPath)
        df = None
        if (not os.path.exists(filepath) or flag):
            df = CTushare.pro.trade_cal(exchange=exchange,
                                        start_date=start,
                                        end_date=end,
                                        is_open=1)
            # log(df)
            df.to_csv(filepath, index=False, encoding="utf_8_sig")
        df = pd.read_csv(filepath)
        if df.shape[0] == 0:
            df = CTushare.pro.trade_cal(exchange=exchange,
                                        start_date=start,
                                        end_date=end,
                                        is_open=1)
            df.to_csv(filepath, index=False, encoding="utf_8_sig")
        return df

    # 是否交易日
    # date: 日期
    def isTradeDate(self, date):
        dk = pd.read_csv(CConfigs.dataPath + '/calendar.csv')
        filepath = CConfigs.dataPath + '/calendar.csv'
        if not os.path.exists(filepath):
            log('日历文件不存在！')
            return
        tmp = dk.query('cal_date == ' + str(date))
        if tmp.shape[0] > 0:
            return True
        else:
            return False

    # 取最近交易日期
    def getLastTradeDate(self):
        s = datetime.datetime.now()
        while not self.isTradeDate(s.strftime('%Y%m%d')):
            s = s - datetime.timedelta(days=1)
        return s.strftime('%Y%m%d')

    def getPreTradeDate(self, date=None):
        if date is None:
            tdate = datetime.datetime.now()
        else:
            tdate = datetime.datetime.strptime(str(date), '%Y%m%d')

        s = tdate - datetime.timedelta(days=1)
        while not self.isTradeDate(s.strftime('%Y%m%d')):
            s = s - datetime.timedelta(days=1)
        return s.strftime('%Y%m%d')

    def getNextTradeDate(self, date):
        s = datetime.datetime.strptime(str(date), '%Y%m%d')
        for i in range(1, 20):
            nextdate = s + datetime.timedelta(days=i)
            if self.isTradeDate(nextdate.strftime('%Y%m%d')):
                return nextdate.strftime('%Y%m%d')
        return None

    # 股票曾用名
    # code: 股票代码
    # start: 开始日期
    # end: 结束日期
    def stockOldNames(self, code, start, end):
        return CTushare.pro.namechange(ts_code=code,
                                       start_date=start,
                                       end_date=end,
                                       fields='ts_code,name,start_date,end_date,change_reason')

    # 获取上市公司基本信息
    def getStockCompany(self):
        if not os.path.exists(self.stockCompanyFile):
            self.updateStockCompany()
        return pd.read_csv(self.stockCompanyFile)

    # 更新上市公司基本信息
    def updateStockCompany(self):
        df = CTushare.pro.stock_company(
            fields='ts_code,exchange,chairman,manager,secretary,reg_capital,setup_date,province,city,introduction,'
                   'website,email,office,employees,main_business,business_scope')
        df.to_csv(self.stockCompanyFile, index=False, encoding="utf_8_sig")

    # 更新备用列表，按股票代码保存
    # code: 股票代码
    def updateBakBasic(self, code):
        filepath = '%s/%s.csv' % (self.stockBakDayPath, code)
        if not os.path.exists(filepath):
            os.mkdir(self.stockBakDayPath)
        df = CTushare.pro.bak_basic(ts_code=code,
                                    fields='trade_date,ts_code,name,industry,area,pe,float_share,total_share,total_assets,liquid_assets,fixed_assets,reserved,reserved_pershare,eps,bvps,pb,list_date,undp,per_undp,rev_yoy,profit_yoy,gpr,npr,holder_num')
        df.to_csv(filepath, index=False, encoding="utf_8_sig")

    # 更新所有备用列表
    # 查询日期
    def updateBakBasicAll(self, date):
        filepath = '%s/%s.csv' % (self.stockBakDayPath, date)
        if not os.path.exists(filepath):
            os.mkdir(self.stockBakDayPath)
        df = CTushare.pro.bak_basic(trade_date=date,
                                    fields='trade_date,ts_code,name,industry,area,pe,float_share,total_share,total_assets,liquid_assets,fixed_assets,reserved,reserved_pershare,eps,bvps,pb,list_date,undp,per_undp,rev_yoy,profit_yoy,gpr,npr,holder_num')
        df.to_csv(filepath, index=False, encoding="utf_8_sig")
        log('日线备用行情增加 OK')

    # 查询备用列表,取最新交易日期
    # condition: 查询条件
    def queryBakBasic(self, condition):
        now = datetime.datetime.now().strftime('%Y%m%d')
        # s = now.strftime('%Y%m%d')
        # s = CTools.getDateDelta(now, -1)
        s = self.getPreTradeDate()
        filepath = '{0}{1}.csv'.format(self.stockBakDayPath, s)
        if not os.path.exists(filepath):
            self.BakDaily(s, s)
        df = pd.read_csv(filepath)
        return df.query(condition)

    # 过滤股票
    def filterStocks(self, condition='float_mv > 0'):
        """ 查询主板和中小板 """
        df = self.queryStockbaseBoardCust(Constants.MAIN_CONDITION_STR)
        da = self.queryBakBasic("industry != '银行'")
        dk = pd.merge(df, da, left_on='ts_code', right_on='ts_code', how='inner')
        columns = ['ts_code', 'float_mv', 'total_mv', 'name_x',
                   'industry_x']
        dtmp = dk[columns].copy()
        dtmp = dtmp.query(condition).sort_values(by='industry_x')
        # dtmp = dk[columns].sort_values(by='industry_x')  # 按流通股排序 float_share, 按行业 industry_x
        Bool = dtmp.name_x.str.contains("ST")  # 去除ST
        dtmp = dtmp[~Bool]
        return dtmp

    # endregion

    # region ==========================  行情  ==========================

    # 初始化数据
    def initData(self):
        self.initDataDay()

    # 初始化日线数据，取最近一年
    def initDataDay(self):
        df = self.queryStockbaseBoardCust(Constants.MAIN_CONDITION_STR)
        ''' 默认取1年数据 '''
        now = datetime.datetime.now().strftime('%Y%m%d')
        start = CTools.getDateDelta(now, -Constants.ONE_YEARE_DAYS)
        for i, row in df.iterrows():
            filepath = self.stockPriceDayPath + row.ts_code + '.csv'
            if os.path.exists(filepath):
                continue
            ds = self.getCodeDay(row.ts_code, start, now)
            print(row.ts_code)
            self.updateDailyCode(row.ts_code, ds)
        log('initDataDay ok')

    # 当日日线数据增加
    def currentDataDayAppend(self):
        # 判断当日是否交易日
        now = datetime.datetime.now().strftime('%Y%m%d')
        if not self.isTradeDate(now):
            log('今天不是交易日')
            return
        df = self.queryStockbaseBoardCust(Constants.MAIN_CONDITION_STR)
        for i, row in df.iterrows():
            print(row.ts_code)
            self.currentDataDayAppendCode(row.ts_code)
        self.updateBakBasicAll(str(now))
        log('日线行情增加 ok')

    # 当日日线数据增加,指定股票代码
    # code: 股票代码
    def currentDataDayAppendCode(self, code):
        now = datetime.datetime.now().strftime('%Y%m%d')
        filepath = self.stockPriceDayPath + code + '.csv'
        if os.path.exists(self.stockPriceDayPath):
            rows = pd.read_csv(filepath)
            cond = "trade_date == {0}".format(now)
            dt = rows.query(cond)
            if dt.shape[0] > 0:
                return
            df = self.getCodeDay(code, now, now)
            rows = rows.append(df, ignore_index=True)
            rows.to_csv(filepath, index=False, encoding="utf_8")

    # 通用行情接口
    # code: 股票代码
    # start：开始日期
    # end: 结束日期
    def getCodeDay(self, code, start, end):
        df = ts.pro_bar(ts_code=code, start_date=start, end_date=end, adj='qfq')
        return df

    # 通用行情接口 获取历史所有数据
    def getCodeDayAll(self, code):
        df = ts.pro_bar(ts_code=code, adj='qfq')
        return df

    def getCodeDaily(self, code, start, end):
        df = ts.pro_api().query('daily', ts_code=code, start_date=start, end_date=end)
        return df

    '''
    更新日线行情数据
    code: 股票代码
    '''

    def updateDailyCode(self, code, rows):
        filepath = self.stockPriceDayPath + code + '.csv'
        if not os.path.exists(self.stockPriceDayPath):
            os.mkdir(self.stockPriceDayPath)
        rows.to_csv(filepath, index=False)

    '''
        有限制，每分钟5次
        '''

    def BakDaily(self, start, end, update=False):
        date = start
        if not os.path.exists(self.stockBakDayPath):
            os.mkdir(self.stockBakDayPath)
        now = datetime.datetime.now()
        s = now.strftime('%Y%m%d')

        while int(date) <= int(end):
            filepath = self.stockBakDayPath + str(date) + '.csv'
            flag = False
            if (not os.path.exists(filepath)) | update:
                flag = True
            elif os.path.exists(filepath):
                stat = os.stat(filepath)
                if stat.st_size < 1000:
                    flag = True
            if flag:
                if self.isTradeDate(date):
                    df = CTushare.pro.bak_daily(trade_date=date,
                                                fields='ts_code,trade_date,name,pct_change,close,change,open,high,'
                                                       'low,pre_close,vol_ratio,turn_over,swing,vol,amount,selling,'
                                                       'buying,total_share,float_share,pe,industry,area,float_mv,'
                                                       'total_mv,avg_price,strength,activity,avg_turnover,attack,'
                                                       'interval_3,interval_6')
                    if df.shape[0] > 0:
                        df.to_csv(filepath, index=False, encoding="utf_8_sig")
                    time.sleep(20)
            date = CTools.getDateDelta(date, 1)

    # 更新个股资金流向,小单：5万以下 中单：5万～20万 大单：20万～100万 特大单：成交额>=100万
    def updateStockMoneyFlow(self, tscode, start, end, update=False):
        fname = f'{self.moneyFlowPath}{tscode}.csv'
        if not os.path.exists(fname) or update:
            df = CTushare.pro.moneyflow(ts_code=tscode, start_date=start, end_date=end, fields='ts_code,trade_date,'
                                                                                               'buy_sm_vol,'
                                                                                               'buy_sm_amount, '
                                                                                               'sell_sm_vol,'
                                                                                               'sell_sm_amount, '
                                                                                               'buy_md_vol,'
                                                                                               'buy_md_amount, '
                                                                                               'sell_md_vol,'
                                                                                               'sell_md_amount, '
                                                                                               'buy_lg_vol,'
                                                                                               'buy_lg_amount, '
                                                                                               'sell_lg_vol,'
                                                                                               'sell_lg_amount, '
                                                                                               'buy_elg_vol,'
                                                                                               'buy_elg_amount, '
                                                                                               'sell_elg_vol,'
                                                                                               'sell_elg_amount, '
                                                                                               'net_mf_vol,'
                                                                                               'net_mf_amount '
                                        )
        else:
            df = pd.read_csv(fname, dtype={'trade_date': str})
            date = df['trade_date'].max()
            now = datetime.datetime.now().strftime('%Y%m%d')
            n = CTools.dateDiff(now, date)
            if n > 0:
                start = CTools.getDateDelta(now, -n + 1)
                dk = CTushare.pro.moneyflow(ts_code=tscode, start_date=start, end_date=now, fields='ts_code,trade_date,'
                                                                                                   'buy_sm_vol,'
                                                                                                   'buy_sm_amount, '
                                                                                                   'sell_sm_vol,'
                                                                                                   'sell_sm_amount, '
                                                                                                   'buy_md_vol,'
                                                                                                   'buy_md_amount, '
                                                                                                   'sell_md_vol,'
                                                                                                   'sell_md_amount, '
                                                                                                   'buy_lg_vol,'
                                                                                                   'buy_lg_amount, '
                                                                                                   'sell_lg_vol,'
                                                                                                   'sell_lg_amount, '
                                                                                                   'buy_elg_vol,'
                                                                                                   'buy_elg_amount, '
                                                                                                   'sell_elg_vol,'
                                                                                                   'sell_elg_amount, '
                                                                                                   'net_mf_vol,'
                                                                                                   'net_mf_amount '
                                            )
                if not dk is None and dk.shape[0] > 0:
                    df = df.append(dk, ignore_index=True)
        df.sort_values(by='trade_date', ascending=True, inplace=True)
        df.to_csv(fname, index=False)

    def updateStockMoneyFlow2(self, date=None):
        if date is None:
            s = self.getLastTradeDate()
        else:
            s = date
        fname = f'{self.moneyFlowPath}{s}.csv'
        df = CTushare.pro.moneyflow(start_date=s, end_date=s, fields='ts_code,trade_date,'
                                                                                           'buy_sm_vol,'
                                                                                           'buy_sm_amount, '
                                                                                           'sell_sm_vol,'
                                                                                           'sell_sm_amount, '
                                                                                           'buy_md_vol,'
                                                                                           'buy_md_amount, '
                                                                                           'sell_md_vol,'
                                                                                           'sell_md_amount, '
                                                                                           'buy_lg_vol,'
                                                                                           'buy_lg_amount, '
                                                                                           'sell_lg_vol,'
                                                                                           'sell_lg_amount, '
                                                                                           'buy_elg_vol,'
                                                                                           'buy_elg_amount, '
                                                                                           'sell_elg_vol,'
                                                                                           'sell_elg_amount, '
                                                                                           'net_mf_vol,'
                                                                                           'net_mf_amount '
                                        )

        df.sort_values(by='trade_date', ascending=True, inplace=True)
        df.to_csv(fname, index=False)

    # 大盘资金流向 , 北向资金不再披露了，没用了
    def updateMoneyFlowHSGT(self, start, end, update=False):
        fname = f'{self.moneyFlowPath}hsgt.csv'
        if not os.path.exists(fname) or update:
            df = CTushare.pro.moneyflow_hsgt(start_date=start, end_date=end, fields='trade_date,'
                                                                               'ggt_ss,'
                                                                               'ggt_sz, '
                                                                               'hgt,'
                                                                               'sgt, '
                                                                               'north_money,'
                                                                               'south_money, '
                                        )
        else:
            df = pd.read_csv(fname, dtype={'trade_date': str})
            date = df['trade_date'].max()
            now = datetime.datetime.now().strftime('%Y%m%d')
            n = CTools.dateDiff(now, date)
            if n > 0:
                start = CTools.getDateDelta(now, -n + 1)
                dk = CTushare.pro.moneyflow_hsgt(start_date=start, end_date=now, fields='trade_date,'
                                                                                   'ggt_ss,'
                                                                                   'ggt_sz, '
                                                                                   'hgt,'
                                                                                   'sgt, '
                                                                                   'north_money,'
                                                                                   'south_money, '
                                            )
                if not dk is None and dk.shape[0] > 0:
                    df = df.append(dk, ignore_index=True)
        df.sort_values(by='trade_date', ascending=True, inplace=True)
        df.to_csv(fname, index=False)

    # endregion

    '''
    未实现接口
    '''
    # 沪深股通成份股
    # 上市公司管理层
    # 管理层薪酬和持股
    # IPO新股列表
