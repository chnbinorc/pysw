#!/usr/bin/python
# -*- coding: UTF-8 -*-

import queue
import threading
import time


class ClsTread(threading.Thread):
    def __init__(self, threadId, callback, args):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.callback = callback
        self.args = args

    def run(self):
        if self.callback:
            self.callback(*self.args)


# class ClsStrateThread(threading.Thread):
#     def __init__(self,threadId,callback,start,end,condition,flag):
#         threading.Thread.__init__(self)
#         self.threadId = threadId
#         self.callback = callback
#         self.start = start
#         self.end = end
#         self.condition = condition
#         self.flag = flag
#
#     def run(self):
#         if self.callback:
#             self.callback(self.start,self.end,self.condition,self.flag)

class ClsMTPool:
    mttool = None
    @staticmethod
    def Create():
        if ClsMTPool.mttool is None:
            ClsMTPool.mttool = ClsMTPool(200)
        return ClsMTPool.mttool
    def __init__(self, maxsize):
        self.maxsize = maxsize
        self.threadId = -1
        self.threads = []

    def add(self, callback, args):
        # if self.threadId > self.maxsize - 1:
        #     print('线程池已满，不能再增加')
        #     return False
        self.threadId += 1
        th = ClsTread(self.threadId, callback, args)
        self.threads.append(th)
        # th.setDaemon(True)
        th.start()
        return True

    # def addStrate(self,callback,start,end,condition,flag):
    #     self.threadId += 1
    #     th = ClsStrateThread(self.threadId,callback,start,end,condition,flag)
    #     self.threads.append(th)
    #     th.start()
    #     return True

    def getMtStatus(self, id):
        return self.threads[id].isAlive()

    def checkMtStatus(self):
        for it in self.threads:
            print('线程{0} 是否活动 : {1} '.format(it.threadId, (it.isAlive())))
