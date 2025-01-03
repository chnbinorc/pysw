# -*- coding: UTF-8 -*-
import datetime
class CTools:

    @staticmethod
    def getOnlyCode(code):
        return str(code).lower().replace('sh','').replace('sz','').replace('.','')

    @staticmethod
    def getPreCode(code):
        cd = CTools.getOnlyCode(code)
        if cd.startswith('600') or cd.startswith('601'):
            return 'SH' + cd
        else:
            return 'SZ' + cd

    @staticmethod
    def getBackCode(code):
        cd = CTools.getOnlyCode(code)
        if cd.startswith('600') or cd.startswith('601'):
            return cd + '.SH'
        else:
            return cd + '.SZ'

    # 日期函数，前某日
    @staticmethod
    def getDateDelta(date,delta):
        dt = datetime.datetime.strptime(str(date), '%Y%m%d')
        count = datetime.timedelta(days=delta)
        dt += count
        return str(dt.strftime('%Y%m%d'))

    # 日期间隔
    @staticmethod
    def dateDiff(date1,date2):
        d1 = datetime.datetime.strptime(str(date1), '%Y%m%d')
        d2 = datetime.datetime.strptime(str(date2), '%Y%m%d')
        return (d1 - d2).days
