# coding:utf-8

from toolkit.List import List
from toolkit.HashMap import HashMap

class XPValue:

    def __init__(self):
        self.m_children = List()
        self.m_parent = None

    def addChild(self, xpValue):
        xpValue.m_parent = self
        self.m_children.pushBack(xpValue)

    def getParent(self):
        return self.m_parent

    def setParent(self, xpValue):
        self.m_parent = xpValue

class XPDocument(XPValue):

    def __init__(self):
        XPValue.__init__(self)
        return


class XPComments(XPValue):

    def __init__(self, isLine, comments):
        XPValue.__init__(self)
        self.m_isLine = isLine
        self.m_comments = comments

    def isLine(self):
        return self.m_isLine

    def getCommnets(self):
        return self.m_comments


class XPObject(XPValue):

    def __init__(self):
        XPValue.__init__(self)
        self.m_mapAtribute = HashMap()

    def addChild(self, xpValue):
        XPValue.addChild(self, xpValue)
        if isinstance(xpValue, XPAttribute):
            self.addValue(xpValue.getKey(), xpValue.getValue())
        return

    def addValue(self, key, xpValue):
        self.m_mapAtribute.insert(key, xpValue)

    def getValue(self, key):
        return self.m_mapAtribute.find(key)


class XPAttribute(XPValue):

    def __init__(self):
        XPValue.__init__(self)
        self.m_key = None
        self.m_value = None

    def getKey(self):
        return self.m_key

    def getValue(self):
        return self.m_value

    def setKey(self, key):
        self.m_key = key

    def setValue(self, value):
        self.m_value = value

    def addChild(self, xpValue):
        if not isinstance(xpValue, XPComments):
            self.setValue(xpValue)
        XPValue.addChild(self, xpValue)

class XPString(XPValue):

    def __init__(self, str):
        XPValue.__init__(self)
        self.m_string = str

class XPArray(XPValue):

    def __init__(self):
        XPValue.__init__(self)
        self.m_list = List()

    def insert(self, xpValue):
        self.m_list.pushBack(xpValue)

    def at(self, index):
        return self.m_list.at(index)

    def count(self):
        return self.m_list.count()