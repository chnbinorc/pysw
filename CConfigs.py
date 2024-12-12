# -*- coding: UTF-8 -*-
from xml.dom.minidom import parse
import xml.dom.minidom

'''
配置类，读取配置文件中的各项配置
'''


class CConfigs:
    _domtree: None = None
    _root: None = None
    _dataConfigs: None = None
    _moduleConfigs: None = None

    def __init__(self):
        if CConfigs._domtree is None:
            self.initData()

    def initData(self):
        CConfigs._domtree = xml.dom.minidom.parse(r'./config.xml')
        CConfigs._root = CConfigs._domtree.documentElement
        CConfigs._dataConfigs = CConfigs._root.getElementsByTagName('DataConfigs')
        CConfigs._moduleConfigs = CConfigs._root.getElementsByTagName('ModeulConfigs')

    def reLoad(self):
        self.initData()

    # 获取tushare的token
    def getTushareToken(self):
        if CConfigs._dataConfigs is not None:
            configs = CConfigs._dataConfigs[0].getElementsByTagName('Config')
            for item in configs:
                if item.hasAttribute('Name') and item.getAttribute('Name') == 'tushare':
                    return item.getAttribute('token')
        return ""

    # 获取本地数据主目录
    def getLocalDataPath(self):
        if CConfigs._dataConfigs is not None:
            configs = CConfigs._dataConfigs[0].getElementsByTagName('Config')
            for item in configs:
                if item.hasAttribute('Name') and item.getAttribute('Name') == 'local':
                    return item.getAttribute('path')
        return ""

    # 获取指定配置
    def getConfig(self, name, key):
        if CConfigs._moduleConfigs is not None:
            configs = CConfigs._moduleConfigs[0].getElementsByTagName('Config')
            for item in configs:
                if item.hasAttribute('Name') and item.getAttribute('Name') == name:
                    return item.getAttribute(key)
        return ""

    def getDataConfig(self, name, key):
        if CConfigs._dataConfigs is not None:
            configs = CConfigs._dataConfigs[0].getElementsByTagName('Config')
            for item in configs:
                if item.hasAttribute('Name') and item.getAttribute('Name') == name:
                    return item.getAttribute(key)
        return ""

    def getModeulConfig(self, name, key):
        if CConfigs._moduleConfigs is not None:
            configs = CConfigs._moduleConfigs[0].getElementsByTagName('Config')
            for item in configs:
                if item.hasAttribute('Name') and item.getAttribute('Name') == name:
                    return item.getAttribute(key)
        return ""