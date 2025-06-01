# -*- coding: UTF-8 -*-
import datetime


class CTools:

    @staticmethod
    def getOnlyCode(code):
        return str(code).lower().replace('sh', '').replace('sz', '').replace('bj', '').replace('.', '')

    @staticmethod
    def getPreCode(code):
        cd = CTools.getOnlyCode(code)
        if cd.startswith('600') or cd.startswith('601') or cd.startswith('603') or cd.startswith('688'):
            return 'SH' + cd
        elif cd.startswith('4') or cd.startswith('8'):
            return 'BJ' + cd
        else:
            return 'SZ' + cd

    @staticmethod
    def getBackCode(code):
        cd = CTools.getOnlyCode(code)
        if cd.startswith('60') or cd.startswith('68'):
            return cd + '.SH'
        elif cd.startswith('4') or cd.startswith('8'):
            return cd + '.BJ'
        else:
            return cd + '.SZ'

    # 日期函数，前某日
    @staticmethod
    def getDateDelta(date, delta):
        dt = datetime.datetime.strptime(str(date), '%Y%m%d')
        count = datetime.timedelta(days=delta)
        dt += count
        return str(dt.strftime('%Y%m%d'))

    # 日期间隔
    @staticmethod
    def dateDiff(date1, date2):
        d1 = datetime.datetime.strptime(str(date1), '%Y%m%d')
        d2 = datetime.datetime.strptime(str(date2), '%Y%m%d')
        return (d1 - d2).days
