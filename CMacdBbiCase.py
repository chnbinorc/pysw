import CCaseBase
import os
import CTushare as cts
import datetime
import pandas as pd
import Constants
import CTools
from CMacdBbiCaseStock import CMacdBbiCaseStock

# macd,bbi,obv 指标，批量处理

class CMacdBbiCase(CCaseBase.CCaseBase):

    def __init__(self):
        super().__init__()
        self.predictMacdBbiPath = '{0}/{1}/'.format(self.stockIndiPath, 'predict_macd_bbi')
        if not os.path.exists(self.predictMacdBbiPath):
            os.mkdir(self.predictMacdBbiPath)
        self.cts = cts.CTushare()
        return

    # 生成预测数据，便于实际运行计算
    def genPredictData(self):
        # now = datetime.datetime.now().strftime('%Y%m%d')
        # result = None
        # if not self.cts.isTradeDate(now):
        #     return
        df = self.cts.filterStocks()


    # 查询个股最近一个月双金叉情况，如果双金叉在3个交易日内发生，则返回最近此双金叉前12个交易日的BBI变化数组，包含此双金叉发生的交易日
    def getDoubleGoldBBI(self,db):
        db = None
        for i, row in db.iterrows():
            stock = CMacdBbiCaseStock(row.ts_code)
            dk = stock.getRecentSignData()
            if dk is not None:
                if db is None:
                    db = dk
                else:
                    db = pd.concat([db, dk], ignore_index=True, axis=0)
        print(db)

    def checkBBIGold(self,df):
        return
    def checkMacdGold(self,df):
        return

    def buyCondition(self,df):
        return

    # 过滤股票
    def filterStocks(self):
        """ 查询主板和中小板 """
        df = self.cts.queryStockbaseBoardCust(Constants.MAIN_CONDITION_STR)
        da = self.cts.queryBakBasic("industry != '银行'")
        dk = pd.merge(df, da, left_on='ts_code', right_on='ts_code', how='inner')
        columns = ['ts_code', 'float_mv', 'total_mv', 'name_x',
                   'industry_x']
        dtmp = dk[columns].copy()
        dtmp = dtmp.query('float_mv > 50').sort_values(by='industry_x')
        Bool = dtmp.name_x.str.contains("ST")  # 去除ST
        dtmp = dtmp[~Bool]
        return dtmp

    # 生成macdbbi指标模型
    def genMacdBBIModel(self):
        db = None
        idx = 0
        for i, row in self.cts.filterStocks().iterrows():
            # if row.ts_code != '000977.SZ':
            #     continue
            # print(row['ts_code'])
            # if idx > 600:
            #     break
            stock = CMacdBbiCaseStock(row.ts_code)
            dk = stock.simpleIndicatorModel()
            if dk is None or dk.shape[0] == 0:
                continue
            if db is None:
                db = dk
            else:
                db = pd.concat([db, dk], ignore_index=True, axis=0)
            idx += 1
        if db is not None:
            db.to_csv('d:/temp/bbidata.csv', index=False, encoding="utf_8_sig")

    # 样本检测
    def testSimple(self):
        df = pd.read_csv('d:/temp/bbidata.csv')
        # dk = df.query('quaprice < 6 and quavol > 8').copy()
        # # dk.drop(columns=['s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11'], inplace=True)
        # # print(dk)
        # d1 = dk.query('income > 0')
        # d2 = dk.query('income < 0')
        # print(f'{len(dk)} , { round(len(d1)/len(dk),3) }, { round(len(d2)/len(dk),3) }')
        print(f'样本总数：{df.shape[0]}')
        for i in range(5):
            for j in range(5):
                cond = f'quaprice == {i} and quavol == {j}'
                dk = df.query(cond).copy()
                d1 = dk.query('income > 0')
                d2 = dk.query('income < 0')
                print(
                    f'条件：价格区间：{i} 成交量区间:{j}  总数： {len(dk)} , 成功：{round(len(d1) / len(dk), 3)}, 失败：{round(len(d2) / len(dk), 3)}')
            print('==========================================================')
