import CCaseBase


class CBoardCase(CCaseBase.CCaseBase):
    _obj = None

    @staticmethod
    def create():
        if CBoardCase._obj is None:
            CBoardCase._obj = CBoardCase()
        return CBoardCase._obj

    def __init__(self):
        pass

    def run(self):
        print('123')
