import datetime
import os
import threading

lock = threading.Lock()


def log(msg):
    lock.acquire()
    writelog(msg)
    lock.release()


def warning(msg):
    lock.acquire()
    writelog('WARNING {0}'.format(msg))
    lock.release()


def error(msg):
    lock.acquire()
    writelog('ERROR {0}'.format(msg))
    lock.release()


def writelog(msg):
    if not os.path.exists('./log/'):
        os.mkdir('./log/')
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    time = datetime.datetime.now().strftime('%H:%M:%S')
    filename = './log/{0}.log'.format(str(date))
    content = '{0} {1} {2} \n'.format(date, time, msg)
    print(content)
    with open(filename, 'a') as f:
        f.write(content)
        f.flush()
    f.close()
