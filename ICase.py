from abc import ABCMeta, abstractmethod


class ICaseRun:
    @abstractmethod
    def run(self,realData):
        pass
