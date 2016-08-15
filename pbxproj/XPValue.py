# coding:utf-8

from toolkit.List import List
from toolkit.HashMap import HashMap

class XPValue:

    def __init__(self):
        self.m_count = 0
        self.m_children = []
        self.m_parent = None

    def addChild(self, xpValue):
        xpValue.m_parent = self
        self.m_count += 1
        self.m_children.append(xpValue)

    def getParent(self):
        return self.m_parent

    def setParent(self, xpValue):
        self.m_parent = xpValue

    def getChildren(self):
        return self.m_children

class XPDocument(XPValue):

    def __init__(self):
        XPValue.__init__(self)
        self.m_rootValue = None
        return

    def addChild(self, xpValue):
        XPValue.addChild(self, xpValue)
        if isinstance(xpValue, XPObject):
            self.m_rootValue = xpValue
        return

    def getRootValue(self):
        return self.m_rootValue


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
        self.m_mapAtribute = {}

    def addChild(self, xpValue):
        XPValue.addChild(self, xpValue)
        if isinstance(xpValue, XPAttribute):
            self.m_mapAtribute[xpValue.m_key] = xpValue.m_value
        return

    def addValue(self, key, xpValue):
        self.m_mapAtribute[key] = xpValue

    def getValue(self, key):
        value = None
        if self.m_mapAtribute.has_key(key):
            value = self.m_mapAtribute[key]
        return value

    def getAttributes(self):
        return self.m_mapAtribute

class XPAttribute(XPValue):

    def __init__(self):
        XPValue.__init__(self)
        self.m_key = None
        self.m_value = None

    def getKey(self):
        return self.m_key

    def getValue(self):
        return self.m_value

    def valueIsObject(self):
        return isinstance(self.m_value, XPObject)

    def valueIsString(self):
        return isinstance(self.m_value, XPString)

    def setKey(self, key):
        self.m_key = key

    def setValue(self, value):
        self.m_value = value

    def addChild(self, xpValue):
        if not isinstance(xpValue, XPComments):
            self.m_value = xpValue
        XPValue.addChild(self, xpValue)

class XPString(XPValue):

    def __init__(self, str):
        XPValue.__init__(self)
        self.m_string = str

    def equals(self, str):
        return self.m_string == str

    def getString(self):
        return self.m_string

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