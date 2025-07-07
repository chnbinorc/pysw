import pandas as pd
import CCaseBase
from CDataPrepare import CDataPrepare
from CTools import CTools
from CTushare import CTushare
import json

class CStockInfoCase(CCaseBase.CCaseBase):
    _obj = None

    @staticmethod
    def create():
        if CStockInfoCase._obj is None:
            CStockInfoCase._obj = CStockInfoCase()
        return CStockInfoCase._obj

    def __init__(self):
        super().__init__()
        self.cts = CTushare()
        self.db = self.cts.getStockCompany()

    def run(self,vdata):
        xdata = {
            'name': 'CStockInfoCase',
            'command': 'CStockInfoCase_ret',
            'data': 'no data'
        }
        try:

            code = CTools.getBackCode(vdata)
            if self.db is None or self.db.shape[0] == 0:
                print('未获取到个股基本信息!!')
            else:
                rows = self.db.query(f'ts_code == "{code}"')
                business_scope = rows.iloc[0]['business_scope']
                employees = rows.iloc[0]['employees']
                main_business = rows.iloc[0]['main_business']
                retstr = f'主营业务:\r\n    {main_business}\r\n\r\n业务范围:\r\n    {business_scope}\r\n\r\n从业人数:\r\n{employees}\r\n\r\n'
                xdata['data'] = retstr
            return json.dumps(xdata)
        except Exception as er:
            print(er)
            return json.dumps(xdata)
