# coding:utf-8


class XPValue:

    def __init__(self):
        self.m_count = 0
        self.m_children = []
        self.m_parent = None
        self.m_userInfo = None

    def setUserInfo(self, userInfo):
        self.m_userInfo = userInfo

    def getUserInfo(self):
        return self.m_userInfo

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

    def genStream(self, ioStream, floor):
        return

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

    def genStream(self, ioStream, floor):
        for xpValue in self.m_children:
            xpValue.genStream(ioStream, 0)
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

    def genStream(self, ioStream, floor):
        if self.m_isLine:
            ioStream.write("//")
            ioStream.write(self.m_comments)
            ioStream.write("\n")
        else:
            ioStream.write("/*")
            ioStream.write(self.m_comments)
            ioStream.write("*/")
        return

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
        if key in self.m_mapAtribute:
            value = self.m_mapAtribute[key]
        return value

    def getAttributes(self):
        return self.m_mapAtribute

    def genStream(self, ioStream, floor):
        needOneLineFormat = False
        attValue = self.getValue("isa")
        if attValue is not None:
            if attValue.equals("PBXBuildFile"):
                needOneLineFormat = True
            elif attValue.equals("PBXFileReference"):
                needOneLineFormat = True

        if needOneLineFormat:
            self.genStreamOneLine(ioStream, floor)
        else:
            self.genStreamNewLine(ioStream, floor)
        return

    def genStreamNewLine(self, ioStream, floor):
        selfFloor = floor + 1
        ioStream.write("{\n")
        #  commentsCount = 0
        for xpValue in self.m_children:
            isComments = isinstance(xpValue, XPComments)
            if isComments:
                ioStream.write("\n")
                xpValue.genStream(ioStream, selfFloor)
                ioStream.write("\n")
            else:
                xpValue.genStream(ioStream, selfFloor)

        for num in range(0, floor):
            ioStream.write("\t")

        ioStream.write("}")

    def genStreamOneLine(self, ioStream, floor):
        selfFloor = floor + 1
        ioStream.write("{")

        for xpValue in self.m_children:
            isComments = isinstance(xpValue, XPComments)
            if isComments:
                xpValue.genStream(ioStream, selfFloor)
            else:
                xpValue.genStreamOneLine(ioStream, selfFloor)

        ioStream.write("}")

class XPAttribute(XPValue):

    def __init__(self):
        XPValue.__init__(self)
        self.m_key = None
        self.m_value = None
        self.m_keyComments = None
        self.m_valueComments = None

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
        else:
            isKeyComments = xpValue.getUserInfo()
            if isKeyComments:
                self.m_keyComments = xpValue
            else:
                self.m_valueComments = xpValue

    def genStream(self, ioStream, floor):
        selfFloor = floor + 1
        for num in range(0, floor):
            ioStream.write("\t")

        ioStream.write(self.m_key)
        if self.m_keyComments is not None:
            ioStream.write(" ")
            self.m_keyComments.genStream(ioStream, floor)

        ioStream.write(" = ")
        self.m_value.genStream(ioStream, floor)
        if self.m_valueComments is not None:
            ioStream.write(" ")
            self.m_valueComments.genStream(ioStream, floor)

        ioStream.write(";\n")
        return

    def genStreamOneLine(self, ioStream, floor):
        selfFloor = floor + 1

        ioStream.write(self.m_key)
        if self.m_keyComments is not None:
            ioStream.write(" ")
            self.m_keyComments.genStream(ioStream, floor)

        ioStream.write(" = ")
        self.m_value.genStream(ioStream, floor)
        if self.m_valueComments is not None:
            ioStream.write(" ")
            self.m_valueComments.genStream(ioStream, floor)

        ioStream.write("; ")
        return

class XPString(XPValue):

    def __init__(self, str):
        XPValue.__init__(self)
        self.m_string = str

    def equals(self, str):
        return self.m_string == str

    def getString(self):
        return self.m_string

    def setString(self, newStr):
        self.m_string = newStr

    def genStream(self, ioStream, floor):
        ioStream.write(self.m_string)
        return

class XPArray(XPValue):

    def __init__(self):
        XPValue.__init__(self)
        self.m_map = {}

    def addChild(self, xpValue):
        if not isinstance(xpValue, XPComments):
            XPValue.addChild(self, xpValue)
        else:
            index = xpValue.getUserInfo()
            self.m_map[index] = xpValue  # .insert(index, xpValue)

    def genStream(self, ioStream, floor):
        selfFloor = floor + 1
        strTabs = ""

        for num in range(0, selfFloor):
            strTabs += "\t"

        count = len(self.m_children)
        ioStream.write("(\n")
        for index in range(0, count):
            xpValue = self.m_children[index]
            ioStream.write(strTabs)
            xpValue.genStream(ioStream, selfFloor)
            if self.m_map.has_key(index):
                xpComment = self.m_map[index]
                ioStream.write(" ")
                xpComment.genStream(ioStream, selfFloor)

            ioStream.write(",\n")

        strTabsForClose = strTabs[0:floor]
        ioStream.write(strTabsForClose)
        ioStream.write(")")
        return