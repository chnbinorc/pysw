from abc import ABCMeta, abstractmethod


class ICaseRun:
    @abstractmethod
    def run(self):
        pass
