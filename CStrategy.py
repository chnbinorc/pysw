# '''
#
# 技术分析类
#
# '''

import CTushare
import Constants
from CCommon import log, warning, error
import os
import pandas as pd
import matplotlib

matplotlib.use('Agg')
import talib
import matplotlib.pyplot as plt
import numpy as np
import CConfigs
from mplfinance.original_flavor import candlestick_ohlc
import datetime

import mplfinance as mpf
from ClsMThreadPool import ClsMTPool


class CStrategy:

    def __init__(self):
        self.cts = CTushare.CTushare()
        Configs = CConfigs.CConfigs()
        if not os.path.exists(CConfigs.dataPath):
            os.mkdir(CConfigs.dataPath)
        self.stockPriceDayPath = '{0}/day/'.format(CConfigs.dataPath)
        self.stockIndicatorsPath = '{0}/indicators/'.format(CConfigs.dataPath)
        self.fig = None
        self.mttool = ClsMTPool.Create()
        self.titles = 0
        self.completTitles = 0
        self.evtIndicatorsCompletDay = None
        return

    # 生成技术指标
    # condition: 查询条件
    # flag: 是否生成图
    def genIndicators(self, condition='', flag=False):
        self.genIndicatorsDay(condition, flag)
        return

    # 生成日线技术指标
    # condition: 查询条件
    # flag: 是否生成图
    def genIndicatorsDay(self, condition='', flag=False):
        df = self.cts.filterStocks()
        tl = int(df.shape[0] / 100) + 1
        self.titles = tl
        self.completTitles = 0
        if df.shape[0] > 100:
            for m in range(0, tl):
                self.mttool.add(self.genIndicatorsDayMt, (m * 100, m * 100 + 100, condition, flag))
                # self.genIndicatorsDayMt()
        else:
            for i, row in df.iterrows():
                df = self.genIndicatorsDayCode(row.ts_code, condition)
                if flag:
                    self.draw(df, row.ts_code)
            log('============日终处理结束============')
        return

    # 生成日线技术指标，多线程
    def genIndicatorsDayMt(self, start, end, condition, flag):
        df = self.cts.filterStocks()
        dk = df[start:end]
        for i, row in dk.iterrows():
            ds = self.genIndicatorsDayCode(row.ts_code, condition)
            if flag:
                self.draw(row.ts_code, ds, row.ts_code)
        # log('日线指标数据生成 OK' + str(end))
        if self.evtIndicatorsCompletDay is not None:
            self.evtIndicatorsCompletDay(start,end)

    # 按股票代码生成日线技术指标
    # code: 股票代码
    # condition: 查询条件
    def genIndicatorsDayCode(self, code, condition=''):
        filepath = self.stockPriceDayPath + code + '.csv'
        filename = self.stockIndicatorsPath + code + '.csv'
        if not os.path.exists(filepath):
            warning('文件不存在[{0}]'.format(filepath))
            return
        if not os.path.exists(self.stockIndicatorsPath):
            os.mkdir(self.stockIndicatorsPath)
        cond = 'close > 0' if condition == '' else condition
        temp = pd.read_csv(filepath)
        df = temp.query(cond).copy()
        dk = self.genIndicatorsData(df)
        dk.to_csv(filename, index=False, encoding="utf_8")
        return dk

    def genIndicatorsData(self, df):
        df.sort_values(by='trade_date', ascending=True, inplace=True)
        df['MA10_talib'] = talib.MA(df['close'], timeperiod=10)
        df['EMA12'] = talib.EMA(df['close'], timeperiod=6)
        df['EMA24'] = talib.EMA(df['close'], timeperiod=12)
        df['macd_diff'], df['macd_dea'], df['macd'] = self.macd_cn(df['close'], 5, 15, 5)  # 默认是12，26，9
        df['RSI'] = talib.RSI(df['close'], timeperiod=12)
        df['MOM'] = talib.MOM(df['close'], timeperiod=5)
        df['VOL5'] = talib.MA(df['vol'], timeperiod=5)
        df['VOL10'] = talib.MA(df['vol'], timeperiod=10)
        df['VOL15'] = talib.MA(df['vol'], timeperiod=15)
        df['VOL20'] = talib.MA(df['vol'], timeperiod=20)
        df['PRICE3'] = talib.MA(df['close'], timeperiod=3)
        df['PRICE5'] = talib.MA(df['close'], timeperiod=5)
        df['PRICE6'] = talib.MA(df['close'], timeperiod=6)
        df['PRICE10'] = talib.MA(df['close'], timeperiod=10)
        df['PRICE12'] = talib.MA(df['close'], timeperiod=12)
        df['PRICE15'] = talib.MA(df['close'], timeperiod=15)
        df['PRICE20'] = talib.MA(df['close'], timeperiod=20)
        df['PRICE24'] = talib.MA(df['close'], timeperiod=24)
        df['PRICE30'] = talib.MA(df['close'], timeperiod=30)
        df['PRICE60'] = talib.MA(df['close'], timeperiod=60)
        df['BBI'] = df.apply(lambda x: self.calcBBI(x['PRICE3'], x['PRICE6'], x['PRICE12'], x['PRICE24']), axis=1)
        df['OBV'] = talib.OBV(df['close'], df['vol'])
        df['MAOBV'] = talib.MA(df['OBV'], timeperiod=30)
        df['PRE_PRICE3'] = talib.MA(df['pre_close'], timeperiod=3)
        df['PRE_PRICE6'] = talib.MA(df['pre_close'], timeperiod=6)
        df['PRE_PRICE12'] = talib.MA(df['pre_close'], timeperiod=12)
        df['PRE_PRICE15'] = talib.MA(df['pre_close'], timeperiod=15)
        df['PRE_PRICE24'] = talib.MA(df['pre_close'], timeperiod=24)
        df['PRE_BBI'] = df.apply(
            lambda x: self.calcBBI(x['PRE_PRICE3'], x['PRE_PRICE6'], x['PRE_PRICE12'], x['PRE_PRICE24']), axis=1)
        return df

    def draw(self, title, data, code):
        if self.fig is None:
            self.fig = plt.figure()

        self.fig.set_size_inches((90, 52))
        self.fig.subplots_adjust(bottom=0.1)
        ax_candle = self.fig.add_axes((0.1, 0.74, 0.8, 0.23))  # 蜡烛子图   left,bottom,width,height
        ax_candle.xaxis_date()
        # ax_vol = self.fig.add_axes((0.1, 0.28, 0.8, 0.23), sharex=ax_candle)  # 成交量子图
        # ax_rsi = fig.add_axes((0.1, 0.51, 0.8, 0.23), sharex=ax_candle)  # rsi 子图
        ax_obv = self.fig.add_axes((0.1, 0.28, 0.8, 0.23), sharex=ax_candle)  # obv 子图
        ax_bbi = self.fig.add_axes((0.1, 0.51, 0.8, 0.23), sharex=ax_candle)  # rsi 子图
        ax_macd = self.fig.add_axes((0.1, 0.05, 0.8, 0.23))  # macd 子图
        ax_candle = self.fig.add_axes((0.1, 0.74, 0.8, 0.23))  # 蜡烛子图   left,bottom,width,height

        # ax_candle.plot(np.arange(0, len(data.index)), data['VOL5'], 'black', label='VOL5')
        # ax_candle.plot(np.arange(0, len(data.index)), data['VOL10'], 'red', label='VOL10')
        # ax_candle.plot(np.arange(0, len(data.index)), data['close'], 'green', label='close')

        ohlc = []  # 存放行情数据, candlestick_ohlc需要传入固定格式的数据
        xlabel = []
        xdataticks = []
        row_number = 0
        for idx, row in data.iterrows():
            sdate = str(row.trade_date)
            tdate = datetime.datetime.strptime(sdate, '%Y%m%d')
            pdate = datetime.datetime.strftime(tdate, '%Y-%m-%d')
            # mdate = dates.date2num(tdate)
            # ohlc.append([mdate,row.open,row.high,row.low,row.close])
            ohlc.append([row_number, row.open, row.high, row.low, row.close])
            xdataticks.append(row_number)
            xlabel.append(pdate)
            row_number = row_number + 1
        candlestick_ohlc(ax_candle, ohlc, width=0.7, colorup='r', colordown='green')  # 上涨为红色K线，下跌为绿色，K线宽度为0.7
        ax_candle.legend()

        # 绘制成交量
        # ax_vol.bar(np.arange(0, len(data.index)), data["vol"] / 1000000)
        # ax_vol.set_ylabel("(Million)")
        # ax_vol.legend()

        # 绘制OBV
        # ax_obv.plot(np.arange(0, len(data.index)), data['MAOBV'], 'blue', label='maobv')
        # ax_obv.plot(np.arange(0, len(data.index)), data['OBV'], 'red', label='obv')
        # ax_obv.set_title('OBV')
        # ax_obv.legend()

        ax_obv.plot(np.arange(0, len(data.index)), data['PRICE10'], 'blue', label='10均线')
        ax_obv.plot(np.arange(0, len(data.index)), data['PRICE12'], 'red', label='12均线')
        ax_obv.plot(np.arange(0, len(data.index)), data['PRICE15'], 'black', label='15均线')
        ax_obv.set_title('OBV')
        ax_obv.legend()

        # 绘制RSI
        # ax_rsi.set_ylabel("(%)")
        # ax_rsi.plot(np.arange(0, len(data.index)), [70] * len(data.index), label="overbought")
        # ax_rsi.plot(np.arange(0, len(data.index)), [30] * len(data.index), label="oversold")
        # ax_rsi.plot(np.arange(0, len(data.index)), data["RSI"], label="rsi")
        # ax_rsi.set_title('KDJ')
        # ax_rsi.legend()

        # 绘制BBI
        ax_bbi.plot(np.arange(0, len(data.index)), data['close'], 'blue', label='close')
        ax_bbi.plot(np.arange(0, len(data.index)), data['BBI'], 'red', label='bbi')
        ax_bbi.set_title('BBI')
        ax_bbi.legend()

        # macd_dif, macd_dea, macd_bar = talib.MACD(data['close'].values, fastperiod=12, slowperiod=26,signalperiod=9)
        # ax_macd.plot(np.arange(0, len(data.index)), macd_dif, 'blue', label='macd dif')  # dif
        # ax_macd.plot(np.arange(0, len(data.index)), macd_dea, 'red', label='macd dea')  # dea
        # bar_red = np.where(macd_bar > 0, 2 * macd_bar, 0)  # 绘制BAR>0 柱状图
        # bar_green = np.where(macd_bar < 0, 2 * macd_bar, 0)  # 绘制BAR<0 柱状图
        # ax_macd.bar(np.arange(0, len(data.index)), bar_red, facecolor='red')
        # ax_macd.bar(np.arange(0, len(data.index)), bar_green, facecolor='green')
        ax_macd.plot(np.arange(0, len(data.index)), data['macd_diff'], 'blue', label='macd dif')  # dif
        ax_macd.plot(np.arange(0, len(data.index)), data['macd_dea'], 'red', label='macd dea')  # dea
        bar_red = np.where(data['macd'] > 0, data['macd'], 0)  # 绘制BAR>0 柱状图
        bar_green = np.where(data['macd'] < 0, data['macd'], 0)  # 绘制BAR<0 柱状图
        ax_macd.bar(np.arange(0, len(data.index)), bar_green, facecolor='green')
        ax_macd.bar(np.arange(0, len(data.index)), bar_red, facecolor='red')
        ax_macd.legend(loc='best', shadow=True, fontsize='10')

        plt.xticks(range(len(xdataticks)), xlabel, rotation=270)  # 日期显示的旋转角度
        plt.title(title)
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文
        plt.rcParams['axes.unicode_minus'] = False
        plt.xlabel('时间')
        plt.ylabel('价格')
        plt.grid(True)
        # 保存

        filename = self.stockIndicatorsPath + code + '.png'
        plt.savefig(filename, bbox_inches='tight')
        # plt.savefig('d:/temp/111.png', bbox_inches='tight')
        plt.cla()
        plt.clf()
        # plt.show()

    def drawMpf(self, data):
        df = data.copy()
        df['new_trade_date'] = df.apply(lambda row: datetime.datetime.strptime(str(row.trade_date), '%Y%m%d'), axis=1)
        # columns = list(data)
        # columns.insert(0,columns.pop(columns.index('trade_date')))
        # df = data.loc[:,columns]
        df = df.set_index('new_trade_date')
        df.index = pd.DatetimeIndex(df.index)
        # print(df)
        mpf.plot(df, savefig='d:/temp/234.png')

    def calcBBI(self, p3, p6, p12, p24):
        if np.isnan(p3) or np.isnan(p6) or np.isnan(p12) or np.isnan(p24):
            return np.nan
        return round((p3 + p6 + p12 + p24) / 4, 2)

    def macd_cn(self, close, fastperiod, slowperiod, signalperiod):
        macdDIFF, macdDEA, macd = talib.MACDEXT(close, fastperiod=fastperiod, fastmatype=1, slowperiod=slowperiod,
                                                slowmatype=1, signalperiod=signalperiod, signalmatype=1)
        macd = macd * 2
        return macdDIFF, macdDEA, macd
