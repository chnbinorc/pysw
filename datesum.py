
import pandas as pd
from CCommon import log
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth',10000)
pd.set_option('display.width',10000)

class datesum:
    # path = 'C:/Users/Administrator/Desktop/123.txt'

    def __init__(self):
        self.path = 'C:/Users/Administrator/Desktop/123.txt'
        self.ds = None
        self.idx = 0

    def readfile(self):
        k = 0.0
        d = 0
        n = -1
        f = open(self.path, mode='r', encoding='utf-8')
        line = f.readline()
        while line:
            if not (line.startswith('date') or line.startswith('\n')):
                k += round(float(line.strip('\n')),2)
                n += round(float(line.strip('\n')),2)
            elif line.startswith('date'):
                if not n == -1:
                    log('日期：{0},小计:{1}'.format(date, (round(n, 2))))
                    self.writefile(date, round(n, 2))
                    n = 0.0
                d += 1
                # 日期
                date = line.strip('\n').replace('date:', '')

            if not line.startswith('\n'):
                log(line.strip('\n'))
            line = f.readline()

        log('日期：{0},小计:{1}'.format(date,(round(n,2))))
        self.writefile(date, round(n, 2))
        log('\n')
        log(self.ds)

        log('天数:{0},总计：{1},平均每天花费:{2}'.format(d,round(k,2),round(k/d,2)))

    def writefile(self,date,count):
        columns = ['日期','小计']
        if self.ds is None:
            self.ds = pd.DataFrame(columns=columns,index=[])
        self.ds.loc[self.idx] = [date,count]
        self.idx += 1


