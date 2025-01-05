import requests
import pandas as pd
import datetime
import time
'''

最近二十天左右的每5分钟数据
http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz000001&scale=5&ma=5&datalen=1023
（参数：股票编号、分钟间隔（5、15、30、60）、均值（5、10、15、20、25）、查询个数点（最大值242））

获取的数据是类似下面的json数组：日期、开盘价、最高价、最低价、收盘价、成交量：
————————————————
版权声明：本文为CSDN博主「铁打的蛋」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/wqy161109/article/details/80052716

'''

class ClsRealTime:
    def __init__(self):
        # url = 'http://hq.sinajs.cn/list=sh601398'
        self.url = 'http://hq.sinajs.cn/list='
        self.headers = {'Accept': '/',
                   'Accept-Language': 'zh-CN,zh;q=0.9',
                   # 'Connection': 'keep-alive',
                   'Connection': 'close',
                   'Content-Length': '129',
                   'Content-Type': 'text/plain; charset=UTF-8',
                   'Cookie': 'ASP.NET_SessionId=vdl5ooxkjkazwszgvj5woewh',
                   'Referer': 'https://finance.sina.com.cn',
                   }

    def GetRealByCode(self,code):
        s1 = code.lower().split('.')
        sp = self.url + s1[1]+s1[0]
        r = requests.get(sp, headers=self.headers)
        r.encoding = 'gbk'
        p1 = r.text.index("\"") + 1
        p2 = r.text.rindex("\"") - 1
        db = r.text[p1:p2].split(',')
        return db[3]

    def GetRealByCode2(self, code):
        s1 = code.lower().split('.')
        sp = self.url + s1[1] + s1[0]
        r = requests.get(sp, headers=self.headers)
        r.encoding = 'gbk'
        return r.text

    def GetRealPrice(self,code):
        if (self.BeInTradeTime()):
            return self.GetRealByCode(code)
        return '-1'

    def GetRealPrices(self,codes):
        # if (not self.BeInTradeTime()):
        #     return None
        src = codes.split(',')
        sp = self.url
        t = ''
        for stritem in src:
            if len(stritem) == 0:
                continue
            s1 = stritem.lower().split('.')
            t = t + s1[1] + s1[0] + ','
        sp = sp + t
        r = requests.get(sp, headers=self.headers)
        print(sp)
        r.encoding = 'gbk'
        print(r.text)
        ret = []
        for retstr in r.text.split(';'):
            if (len(retstr) < 5):
                continue
            p1 = retstr.index("\"") + 1
            p2 = retstr.rindex("\"") - 1
            if p2 > p1:
                db = retstr[p1:p2].split(',')
                ret.append(db[3])
        return ret

    def GetRealPrices2(self,codes):
        src = codes.split(',')
        sp = self.url
        t = ''
        for stritem in src:
            if len(stritem) == 0:
                continue
            s1 = stritem.lower().split('.')
            if len(s1) < 2:
                t=s1[0]
                break
            t = t + s1[1] + s1[0] + ','
        sp = sp + t
        r = requests.get(sp, headers=self.headers)
        r.encoding = 'gbk'
        # print(r.text)
        cols = ['levelW', 'level','code', 'name', 'open', 'close', 'price', 'high', 'low', 'buy', 'sell', 'done_num', 'done_money', 'date', 'time']
        ret = pd.DataFrame(columns=cols,index=[])
        for retstr in r.text.split(';'):
            # print(retstr)
            if (len(retstr) < 5):
                continue
            p1 = retstr.index("\"") + 1
            p2 = retstr.rindex("\"") - 1

            if p2 > p1:
                db = retstr[p1:p2].split(',')
                if (p1 == 21):
                    code = str(retstr[13:19])
                else:
                    code = str(retstr[14:20])

                level = 1
                levelW = 1
                if (float(db[1]) == 0):
                    level = 1
                    levelW = 1
                else:
                    level = round( (float(db[3]) - float(db[2])) / float(db[2]) , 4)
                    levelW = round( (float(db[3]) - float(db[1])) / float(db[1]) , 4)

                # if (level > 0.02 and level < 1):
                #     ret.loc[len(ret)] = [level, code, db[0], db[1], db[2], db[3], db[4], db[5], db[6], db[7],
                #                          int(int(db[8]) / 1000000), round(float(db[9]) / 100000000, 2), db[30], db[31]]
                if (level != 1):
                    ret.loc[len(ret)] = [levelW, level, code, db[0], db[1], db[2], db[3], db[4], db[5], db[6], db[7],
                                     int(int(db[8]) / 100), round(float(db[9]) / 100000000, 2), db[30], db[31]]

        return ret

    def BeInMorning(self):
        t2 = self.TimeCmp(time.strptime("11:30:00", "%H:%M:%S"), time.localtime(time.time()))
        return t2 > 0

    def BeInTradeTime(self):
        t1 = self.TimeCmp(time.localtime(time.time()), time.strptime("09:25:00", "%H:%M:%S"))
        t2 = self.TimeCmp(time.strptime("11:30:00", "%H:%M:%S"), time.localtime(time.time()))
        t3 = self.TimeCmp(time.localtime(time.time()), time.strptime("13:00:00", "%H:%M:%S"))
        t4 = self.TimeCmp(time.strptime("15:00:00", "%H:%M:%S"), time.localtime(time.time()))
        if (t1 > 0 and t4 > 0):
            return True
        # if ( t1 > 0 and t2 > 0 ):
        #     return True;
        # elif ( t3 > 0 and t4 > 0 ):
        #     return True
        return False

    def BeInWarningTime(self):
        t1 = self.TimeCmp(time.localtime(time.time()), time.strptime("09:20:00", "%H:%M:%S"))
        t2 = self.TimeCmp(time.strptime("09:25:00", "%H:%M:%S"), time.localtime(time.time()))
        t3 = self.TimeCmp(time.localtime(time.time()), time.strptime("12:58:00", "%H:%M:%S"))
        t4 = self.TimeCmp(time.strptime("13:00:00", "%H:%M:%S"), time.localtime(time.time()))

        if (t1 > 0 and t2 > 0) or (t3 > 0 and t4 > 0):
            return True
        else:
            return False

    def BeInGoldenTime(self):
        t1 = self.TimeCmp(time.localtime(time.time()), time.strptime("09:25:00", "%H:%M:%S"))
        t2 = self.TimeCmp(time.strptime("11:30:00", "%H:%M:%S"), time.localtime(time.time()))
        t3 = self.TimeCmp(time.localtime(time.time()), time.strptime("13:00:00", "%H:%M:%S"))
        t4 = self.TimeCmp(time.strptime("15:00:00", "%H:%M:%S"), time.localtime(time.time()))

        if (t1 > 0 and t2 > 0) or (t3 > 0 and t4 > 0):
            return True
        else:
            return False

    def BeInTime(self,start,end):
        t1 = self.TimeCmp(time.localtime(time.time()), time.strptime(start, "%H:%M:%S"))
        t2 = self.TimeCmp(time.strptime(end, "%H:%M:%S"), time.localtime(time.time()))
        return t1 > 0 and t2 > 0


    def BeInDiamondTime(self):
        t1 = self.TimeCmp(time.localtime(time.time()), time.strptime("09:25:00", "%H:%M:%S"))
        t2 = self.TimeCmp(time.strptime("09:35:00", "%H:%M:%S"), time.localtime(time.time()))

        if (t1 > 0 and t2 > 0):
            return True
        else:
            return False

    def BeInEndTime(self):
        t4 = self.TimeCmp(time.strptime("14:58:00", "%H:%M:%S"), time.localtime(time.time()))
        if (t4 < 0):
            return True
        else:
            return False

    def isDayworkTime(self):
        t4 = self.TimeCmp(time.strptime("17:00:00", "%H:%M:%S"), time.localtime(time.time()))
        if (t4 < 0):
            return True
        else:
            return False

    def IsBeginTime(self):
        return self.TimeCmp(time.strptime("09:25:00", "%H:%M:%S"), time.localtime(time.time())) > 0

    def IsEndTime(self):
        return self.TimeCmp(time.strptime("15:00:00", "%H:%M:%S"), time.localtime(time.time())) < 0

    def IsDayWorkTime(self):
        return self.TimeCmp(time.strptime("17:00:00", "%H:%M:%S"), time.localtime(time.time())) < 0

    def isDayChange(self):
        return self.TimeCmp(time.strptime("00:05:00", "%H:%M:%S"), time.localtime(time.time())) > 0

    def TimeCmp(self,tm1, tm2):
        return int(time.strftime("%H%M%S", tm1)) - int(time.strftime("%H%M%S", tm2))

    # 计算日期区段
    def GetDatePeriod(self,dt, peod):
        ret = dt - datetime.timedelta(days=peod)
        strdt = datetime.datetime.strftime(ret, '%Y%m%d')
        return strdt
        # return dt - datetime.timedelta(days=peod)

    # 获取交易日列表
    def GetTradeDates(self,start,end):
        return []

    def GetTradeDatesDays(self,start,days):
        return []

    def testIsTradeTime(self,flag,time1):
        t1 = self.TimeCmp(time.strptime(time1, "%H:%M:%S"), time.strptime("09:25:00", "%H:%M:%S"))
        t5 = self.TimeCmp(time.strptime("09:35:00", "%H:%M:%S"), time.strptime(time1, "%H:%M:%S"))

        t6 = self.TimeCmp(time.strptime("09:30:00", "%H:%M:%S"), time.strptime(time1, "%H:%M:%S"))
        t2 = self.TimeCmp(time.strptime("11:30:00", "%H:%M:%S"), time.strptime(time1, "%H:%M:%S"))
        t7 = self.TimeCmp(time.strptime("13:00:00", "%H:%M:%S"), time.strptime(time1, "%H:%M:%S"))
        t4 = self.TimeCmp(time.strptime("15:00:00", "%H:%M:%S"), time.strptime(time1, "%H:%M:%S"))

        # 集合竞价最后5分钟+开盘后5分钟
        if 1 == flag:
            return t1 >= 0 and t5 >= 0
        # 开盘时间 包含午休
        elif 2 == flag:
            return t5 <= 0 and t4 >= 0
        # 早盘时间
        elif 3 == flag:
            return (t6 <= 0 and t2 >= 0)
        # 午盘时间
        elif 4 == flag:
            return (t7 <= 0 and t4 >= 0)
        # 开盘时间 不包含午休
        elif 5 == flag:
            return (t6 <= 0 and t2 >= 0) or (t7 <= 0 and t4 >= 0)
        # 开盘5分钟后 不包含午休
        elif 6 == flag:
            return (t5 <= 0 and t2 >= 0) or (t7 <= 0 and t4 >= 0)
        else:
            return False

    def IsTradeTime(self,flag):
        t1 = self.TimeCmp(time.localtime(time.time()), time.strptime("09:25:00", "%H:%M:%S"))
        t5 = self.TimeCmp(time.strptime("09:35:00", "%H:%M:%S"), time.localtime(time.time()))

        t6 = self.TimeCmp(time.strptime("09:30:00", "%H:%M:%S"), time.localtime(time.time()))
        t2 = self.TimeCmp(time.strptime("11:30:00", "%H:%M:%S"), time.localtime(time.time()))
        t7 = self.TimeCmp(time.strptime("13:00:00", "%H:%M:%S"), time.localtime(time.time()))
        t4 = self.TimeCmp(time.strptime("15:00:00", "%H:%M:%S"), time.localtime(time.time()))

        # 集合竞价最后5分钟+开盘后5分钟
        if 1 == flag:
            return t1 > 0 and t5 < 0
        # 开盘时间 包含午休
        elif 2 == flag:
            return t5 < 0 and t4 > 0
        # 早盘时间
        elif 3 == flag:
            return (t6 < 0 and t2 > 0)
        # 午盘时间
        elif 4 == flag:
            return (t7 < 0 and t4 > 0)
        # 开盘时间 不包含午休
        elif 5 == flag:
            return (t6 < 0 and t2 > 0) or (t7 < 0 and t4 > 0)
        # 开盘5分钟后 不包含午休
        elif 6 == flag:
            return (t5 < 0 and t2 > 0) or (t7 < 0 and t4 > 0)
        else:
            return False

'''
'工商银行',                股票名称          
'4.360',                  今日开盘价        
'4.350',                  昨日收盘价        
'4.360',                  当前价格          
'4.360',                  今日最高价        
'4.350',                  今日最低价        
'4.350',                  买一              
'4.360',                  卖一              
'14627006',               成交的股票数 / 100
'63677026.000',           成交金额   / 10000
'988500',                 买一              
'4.350',                  买一 报价         
'23208500',               买二              
'4.340',                  买二 报价         
'25711000',               买三              
'4.330',                  买三 报价         
'10433300',               买四              
'4.320',                  买四 报价         
'1237300',                买五              
'4.310',                  买五 报价         
'23202418',               卖一              
'4.360',                  卖一 报价         
'23587688',               卖二              
'4.370',                  卖二 报价         
'21923643',               卖三              
'4.380',                  卖三 报价         
'7895004',                卖四              
'4.390',                  卖四 报价         
'4311218',                卖四              
'4.400',                  卖四              
'2022-09-08', 			  日期
'09:39:29', 			  时间
'00'
'''

'''

最近二十天左右的每5分钟数据
http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz000001&scale=5&ma=5&datalen=1023
（参数：股票编号、分钟间隔（5、15、30、60）、均值（5、10、15、20、25）[no]、查询个数点（最大值242））
'''




