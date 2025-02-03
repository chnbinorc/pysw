import os.path
import pandas as pd
import datetime
import time
import CTools as ctools
import CTushare as cts
import Constants
import CStrategy as strate
from CCommon import log, warning, error
from CMacdBbiCase import CMacdBbiCase
# from CStockMarket import CStockMarket


class CDayWork:
    def __init__(self,fnend):
        self.cts = cts.CTushare()
        self.strate = strate.CStrategy()
        self.tools = ctools.CTools()
        self.bbicase = CMacdBbiCase()
        self.endtrigger = fnend

    def run(self):
        log('============开始日终处理============')
        log('更新基本信息')
        self.cts.updateAllStockBase()
        log('更新备用数据')
        self.doBakData()
        log('更新日线行情数据')
        self.doDayData()
        log('更新指标数据分析')
        self.doIndicators(False)
        # log('============日终处理结束============')

    # 更新备用数据
    def doBakData(self):
        now = datetime.datetime.now().strftime('%Y%m%d')
        # start = self.tools.getDateDelta(now, -Constants.ONE_YEARE_DAYS)
        try:
            self.cts.BakDaily(now, now)
        except Exception as er:
            error(er)

    # 更新指定日期段的备用行情
    def doBakDataBat(self, start, end):
        try:
            self.cts.BakDaily(start, end)
        except Exception as er:
            error(er)

    # 更新日线行情
    def doDayData(self):
        now = datetime.datetime.now().strftime('%Y%m%d')
        start = self.tools.getDateDelta(now, -Constants.ONE_YEARE_DAYS - Constants.ONE_MONTH_DAYS * 6)
        df = self.cts.queryStockbaseBoardCust(Constants.MAIN_CONDITION_STR)
        for i, row in df.iterrows():
            try:
                filepath = self.cts.stockPriceDayPath + row.ts_code + '.csv'
                if os.path.exists(filepath):
                    self.doDayDataCode(row.ts_code)
                else:
                    ds = self.cts.getCodeDay(row.ts_code, start, now)
                    self.cts.updateDailyCode(row.ts_code, ds)
            except Exception as er:
                error(er)

    # 更新日线行情数据，按股票代码
    def doDayDataCode(self, code):
        now = datetime.datetime.now().strftime('%Y%m%d')
        filepath = self.cts.stockPriceDayPath + code + '.csv'
        if os.path.exists(filepath):
            rows = pd.read_csv(filepath)
            date = rows['trade_date'].max()
            n = self.tools.dateDiff(now, date)
            if n > 0:
                start = self.tools.getDateDelta(now, -n + 1)
                df = self.cts.getCodeDay(code, start, now)
                # df = self.cts.getCodeDaily(code,start,now)
                if df is not None and df.shape[0] > 0:
                    rows = rows.append(df, ignore_index=True)
                self.cts.updateDailyCode(code, rows)

    # 生成指标数据
    def doIndicators(self, flag=False):
        self.strate.evtIndicatorsCompletDay = self.evtIndicatorsCompletDay
        self.strate.genIndicators('', flag)
        # total = self.filterStocks().shape[0]
        # count = 0
        # print(f'总共处理 {total}')
        # for i, row in self.filterStocks().iterrows():
        #     print(count)
        #     if count % 10 == 0:
        #         print(f'已经处理{count}')
        #     df = self.strate.genIndicatorsDayCode(row.ts_code)
        #     if flag:
        #         self.strate.draw(row.ts_code, df, row.ts_code)
        #     count += 1
        # return

    # 日线指标生成完成事件
    # 完成事件后，可进行预处理，分析等操作
    def evtIndicatorsCompletDay(self, start, end):
        self.strate.completTitles += 1
        if self.strate.completTitles == self.strate.titles:
            log(f'日终指标数据生成情况：总数{self.strate.titles},完成{self.strate.completTitles}')
            log('============生成最近交易日预处理数据============')
            self.genPreData()
            log('============生成目标预测数据============')
            self.genTargetPredictStockDay()

            log('============更新同花顺板块信息以及大盘资金流向============')
            self.updateTHSIndex()
            self.updateMarketDC()

            log('============获取个股资金流向============')
            self.updateStockMoneyFlow()
            log('============获取个股资金(同花顺)流向============')
            self.updateStockMoneyFlow_THS()
            log('============获取板块资金(同花顺)流向============')
            self.updateIndexMoneyFlow_THS()
            log('============日终处理结束============')
            if self.endtrigger is not None:
                self.endtrigger(True)
        else:
            log(f'日终指标数据生成情况：总数{self.strate.titles},完成{self.strate.completTitles}')

    # 生成预处理数据
    def genPreData(self):
        db = self.bbicase.genPredictData()

    # 生成目标预测数据
    def genTargetPredictStockDay(self):
        self.bbicase.getpredictStockDay()

    # 更新个股资金流向
    def updateStockMoneyFlow(self,all=False):
        now = datetime.datetime.now().strftime('%Y%m%d')
        if all:
            next = self.tools.getDateDelta(now,-Constants.ONE_YEARE_DAYS)
            while int(next) <= int(now):
                self.cts.updateStockMoneyFlow2(next)
                next = self.cts.getNextTradeDate(next)
        else:
            self.cts.updateStockMoneyFlow2(now)

    # 更新个股资金流向，同花顺
    def updateStockMoneyFlow_THS(self):
        now = datetime.datetime.now().strftime('%Y%m%d')
        start = self.tools.getDateDelta(now, -Constants.ONE_YEARE_DAYS)
        df = self.cts.filterStocks()
        log(f'开始更新个股资金流向（同花顺接口） 500次/分钟 ，总数{df.shape[0]}')
        for i,row in df.iterrows():
            self.cts.updateStockMoneyFlowTHS(row.ts_code,start,now)
            time.sleep(0.1)

    # 更新板块资金流向，同花顺
    def updateIndexMoneyFlow_THS(self):
        now = datetime.datetime.now().strftime('%Y%m%d')
        start = self.tools.getDateDelta(now, -Constants.ONE_YEARE_DAYS)
        log(f'开始更新板块资金流向（同花顺接口')
        self.cts.updateIndMoneyFlowTHS(start,now)

    # 更新同花顺板块行业以及成分
    def updateTHSIndex(self):
        self.cts.updateTHSIndex()

    # 更新大盘资金流向，东财
    def updateMarketDC(self):
        self.cts.updateMarketDC()