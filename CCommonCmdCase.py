import datetime
import os.path

import pandas as pd
import CCaseBase
import CRealData
from CDataPrepare import CDataPrepare
from CTools import CTools
from CTushare import CTushare
import json

class CCommonCmdCase(CCaseBase.CCaseBase):
    _obj = None

    @staticmethod
    def create():
        if CCommonCmdCase._obj is None:
            CCommonCmdCase._obj = CCommonCmdCase()
        return CCommonCmdCase._obj

    def __init__(self):
        super().__init__()
        self.cts = CTushare()

    def run(self,data):
        xdata = {
            'name': 'CCommonCmdCase',
            'command': 'CCommonCmdCase_ret',
            'data': ''
        }

        jobj = json.loads(data)
        cmd = jobj['command']
        code = CTools.getBackCode(jobj['code'])
        start = jobj['begin']
        end = jobj['end']
        filename = f'{self.moneyFlowPath_ths}{code}.csv'
        print(filename)
        if not os.path.exists(filename):
            print(f'文件不存在! {filename}')
            return json.dumps(xdata)

        sqlstr = f'trade_date >= {int(start)} and trade_date <= {int(end)}'
        print(sqlstr)
        df = pd.read_csv(filename).query(sqlstr)
        print(df)
        return json.dumps(xdata)