# coding:utf-8

from toolkit import List
from toolkit import HashMap

class XPValue:

    def __init__(self):
        self.m_children = List()
        self.m_parent = None

    def addChild(self, xpValue):
        xpValue.m_parent = self
        self.m_children.pushBack(xpValue)

    def getParent(self):
        return self.m_parent

class XPDocument(XPValue):

    def __init__(self):
        return

class XPComments(XPValue):

    def __init__(self, isLine, comments):
        self.m_isLine = isLine
        self.m_comments = comments

    def isLine(self):
        return self.m_isLine

    def getCommnets(self):
        return self.m_comments

class XPObject(XPValue):
    def __init__(self):
        self.m_mapAtribute = HashMap()

    def addChild(self, xpValue):
        super.addChild(xpValue)
        if isinstance(xpValue, XPAttribute):
            self.addValue(xpValue.getKey(), xpValue.getValue())
        return

    def addValue(self, key, xpValue):
        self.m_mapAtribute.insert(key, xpValue)

    def getValue(self, key):
        return self.m_mapAtribute.find(key)

class XPAttribute(XPValue):

    def __init__(self, key, value):
        self.m_key = key
        self.m_value = value

    def getKey(self):
        return self.m_key

    def getValue(self):
        return self.m_value

class XPArray(XPValue):

    def __init__(self):
        self.m_list = List()

    def insert(self, xpValue):
        self.m_list.pushBack(xpValue)

    def at(self, index):
        return self.m_list.at(index)

    def count(self):
        return self.m_list.count()