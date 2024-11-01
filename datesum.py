
class datesum:
    # path = 'C:/Users/Administrator/Desktop/123.txt'

    def __init__(self):
        self.path = 'C:/Users/Administrator/Desktop/123.txt'

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
                d += 1

            if line.startswith('date'):
                if not n == -1:
                    print('小计:{0}'.format(round(n,2)))
                    print('\n')
                n = 0.0

            if not line.startswith('\n'):
                print(line.strip('\n'))
            line = f.readline()

        print('小计:{0}'.format(round(n,2)))
        print('\n')

        print('天数:{0},总计：{1},平均每天花费:{2}'.format(d,round(k,2),round(k/d,2)))