# coding:utf-8
from toolkit.Stack import Stack
from XPValue import XPDocument
from XPValue import XPComments
from XPValue import XPObject
from XPValue import XPAttribute
from XPValue import XPArray
from XPValue import XPString

"""
解码状态机中状态基类
"""


class ParseResult:
    Error = 1           # 出现错误
    NeedSwitch = 2      # 需要切换状态
    Pending = 3         # 未决，表示还未解析完成
    Finish = 4          # 解析成功并且完成
    AppendChild = 5     # 附加新的子解码器
    AppendSibling = 6   # 附加新的兄弟解码器

    PendingParseResult = None
    FinishParseResult = None

    def __init__(self, state):
        self.m_state = state
        self.m_nextDecoderName = None
        self.m_newDecoderName = None
        self.m_backNum = 0

    def getState(self):
        return self.m_state

    def setNextDecoderName(self, nextDecoderName):
        self.m_nextDecoderName = nextDecoderName

    def genNextDecoder(self):
        if None == self.m_nextDecoderName:
            return None
        return eval(self.m_nextDecoderName + "()")

    def setBackNum(self, backNum):
        self.m_backNum = backNum

    def getBackNum(self):
        return self.m_backNum

    @classmethod
    def pending(cls):
        if None == ParseResult.PendingParseResult:
            ParseResult.PendingParseResult = ParseResult(ParseResult.Pending)
        return ParseResult.PendingParseResult

    @classmethod
    def finish(cls):
        if None == ParseResult.FinishParseResult:
            ParseResult.FinishParseResult = ParseResult(ParseResult.Finish)

        return ParseResult.FinishParseResult

    @classmethod
    def needSwitch(cls, nextDecoderName, backNum):
        result = ParseResult(ParseResult.NeedSwitch)
        result.setNextDecoderName(nextDecoderName)
        result.setBackNum(backNum)
        return result

    @classmethod
    def error(cls):
        result = ParseResult(ParseResult.Error)
        return result

    @classmethod
    def appendChild(cls, nextDecoderName):
        result = ParseResult(ParseResult.AppendChild)
        result.setNextDecoderName(nextDecoderName)
        # result.setBackNum(backNum)
        return result

    @classmethod
    def appendSibling(cls, nextDecoderName):
        result = ParseResult(ParseResult.AppendSibling)
        result.setNextDecoderName(nextDecoderName)
        # result.setBackNum(backNum)
        return result


class Decoder:

    def __init__(self):
        self.m_isEnd = False
        self.m_statementStartIndex = -1
        self.m_statementLength = 0
        return

    def parseBegin(self, index):
        if self.m_statementStartIndex == -1:
            self.m_statementStartIndex = index

    def parse(self, rawText, ch, index):
        if self.m_statementStartIndex == -1:
            self.m_statementStartIndex = index
        self.m_statementLength += 1

    def parseEnd(self):
        self.m_statementLength += 1

    def genXPValue(self):
        return None

    def allowGenXPValueBeforeFinish(self):
        return True

    def allowHasChild(self, rawText):
        return True
"""
行注释解码
"""


class LineCommentsDecoder(Decoder):

    def __init__(self):
        Decoder.__init__(self)
        return

    def parse(self, rawText, ch, index):
        if self.m_statementLength == 1:
            if ch == '*':  # 如果碰到*表示本次是块注释
                return ParseResult.needSwitch("ChunckCommentsDecoder", 1)  # 回退两个字符,并转为块注释
            elif ch != '/':
                return ParseResult.error()
        elif ch == '\n':  # 碰到换行表示结束
            return ParseResult.finish()

        return ParseResult.pending()

    def allowGenXPValueBeforeFinish(self):
        return False

    def allowHasChild(self, rawText):
        return False

    def genXPValue(self, rawText):
        start = self.m_statementStartIndex + 2  # 从//之后开始所以是要加2
        end = self.m_statementStartIndex + self.m_statementLength - 1 # 去掉\n
        comments = rawText[start:end]
        return XPComments(True, comments)

"""
块注释解码
"""


class ChunckCommentsDecoder(Decoder):

    def __init__(self):
        Decoder.__init__(self)
        self.m_isEndStar = False
        return

    def parse(self, rawText, ch, index):
        if self.m_statementLength == 1:
            if ch != '*':  # 如果碰到*表示本次是块注释
                return ParseResult.error()
            else:
                return ParseResult.pending()
        elif ch == '*':
            self.m_isEndStar = True
            return ParseResult.pending()
        else:
            if self.m_isEndStar:  # 遇到*/表示注释结束
                if ch != '/':
                    return ParseResult.error()
                else:
                    return ParseResult.finish()
            else:
                return ParseResult.pending()

    def allowHasChild(self, rawText):
        return False

    def allowGenXPValueBeforeFinish(self):
        return False

    def genXPValue(self, rawText):
        start = self.m_statementStartIndex + 2  # // /*
        end = self.m_statementStartIndex + self.m_statementLength
        comments = rawText[start:end]
        return XPComments(False, comments)
"""
带""的字符串解码
"""


class StringDecoder(Decoder):

    def __init__(self):
        Decoder.__init__(self)
        return

    def parse(self, rawText, ch, index):
        if self.m_statementLength == 0:
            return ParseResult.pending()
        if ch == '"':
            return ParseResult.finish()
        else:
            return ParseResult.pending()

    def genXPValue(self, rawText):
        start = self.m_statementStartIndex
        end = self.m_statementStartIndex + self.m_statementLength
        string = rawText[start:end]
        return XPString(string)
"""
对象解码
"""


class ObjectDecoder(Decoder):

    def __init__(self):
        Decoder.__init__(self)
        return

    def parse(self, rawText, ch, index):
        if self.m_statementLength == 0:
            return ParseResult.pending()

        if ch == ' ' or ch == '\r' or ch == '\n' or ch == '\t':
            return ParseResult.pending()

        if ch == '/':
            return ParseResult.appendChild("LineCommentsDecoder")
        elif ch == '}':
            return ParseResult.finish()
        else:
            return ParseResult.appendChild("AttributeDecoder")

    def genXPValue(self, rawText):
        return XPObject()
"""
属性解码
"""


class AttributeDecoder(Decoder):
    def __init__(self):
        Decoder.__init__(self)
        self.m_attrValue = None
        self.m_keyStart = -1
        self.m_keyEnd = -1
        self.m_valueStart = -1
        self.m_valueEnd = -1
        return

    def parse(self, rawText, ch, index):
        if ch == ' ' or ch == '\r' or ch == '\n' or ch == '\t':
            return ParseResult.pending()

        if ch == '/':
            nextCh = rawText[index + 1]
            if nextCh != '/' and nextCh != '*':
                return ParseResult.pending()
            else:
                return ParseResult.appendChild("LineCommentsDecoder")
        elif ch == '"':
            if -1 == self.m_keyStart:
                self.m_keyStart = index
            return ParseResult.appendChild("StringDecoder")
        elif ch == '{':
            return ParseResult.appendChild("ObjectDecoder")
        elif ch == '(':
            return ParseResult.appendChild("ArrayDecoder")
        else:
            if -1 == self.m_keyStart:
                self.m_keyStart = index

            if ch == '=':
                if (self.m_keyStart == index) or (self.m_valueStart != -1):
                    return ParseResult.error()
                self.m_keyEnd = index
                self.genXPValue(rawText)
                key = rawText[self.m_keyStart:self.m_keyEnd]
                self.m_attrValue.setKey(key)
                self.m_attrValue.addChild(XPString(key))
                self.m_valueStart = index + 1
            elif ch == ';':
                self.m_valueEnd = index
                self.genXPValue(rawText)
                value = rawText[self.m_valueStart:self.m_valueEnd]
                self.m_attrValue.setValue(value)
                self.m_attrValue.addChild(XPString(value))
                return ParseResult.finish()

            return ParseResult.pending()

    def genXPValue(self, rawText):
        if None == self.m_attrValue:
            self.m_attrValue = XPAttribute()
        return self.m_attrValue

"""
数组解码
"""


class ArrayDecoder(Decoder):

    def __init__(self):
        Decoder.__init__(self)
        self.m_arrValue = None
        return

    def parse(self, rawText, ch, index):
        if ch == ' ' or ch == '\r' or ch == '\n' or ch == '\t':
            return ParseResult.pending()

        if ch == '/':
            return ParseResult.appendChild("LineCommentsDecoder")
        elif ch == '"':
            return ParseResult.appendChild("StringDecoder")
        elif ch == ',':
            return ParseResult.pending()
        elif ch == ')':
            return ParseResult.finish()
        return ParseResult.pending()

    def genXPValue(self, rawText):
        if None == self.m_arrValue:
            self.m_arrValue = XPArray()
        return self.m_arrValue

"""
工程文件解码器
"""


class XcodeProjectDecoder:

    def __init__(self):
        self.m_stateStack = Stack()
        self.m_document = XPDocument()
        self.m_curValue = self.m_document
        return

    # 解码器的主人口
    def decode(self, rawString):
        ch = rawString[0]
        index = 0
        length = len(rawString)
        while (ch != 0 and index < length):
            ch = rawString[index]

            if self.m_stateStack.isEmpty():
                self.autoSelect(rawString, ch)

            topDecoder = self.m_stateStack.top()
            if None == topDecoder:
                index += 1
                continue

            topDecoder.parseBegin(index)
            decodeResult = topDecoder.parse(rawString, ch, index)

            decodeState = decodeResult.getState()
            if decodeState == ParseResult.Pending:
                topDecoder.parseEnd()
            elif decodeState == ParseResult.NeedSwitch:
                index -= decodeResult.getBackNum()
                self.needSwitch(rawString, decodeResult)
                continue
            elif decodeState == ParseResult.AppendChild:
                index -= decodeResult.getBackNum()
                self.appendChild(rawString, decodeResult)
                continue
            elif decodeState == ParseResult.Finish:
                topDecoder.parseEnd()
                self.finish(rawString)
            elif decodeState == ParseResult.Error:
                break

            index += 1
        return

    # 自动选择解码器
    def autoSelect(self, rawText, ch):
        decoder = None
        if ch == '/':
            decoder = LineCommentsDecoder()
        elif ch == '{':
            decoder = ObjectDecoder()
        elif ch == '(':
            decoder = ArrayDecoder()
        elif ch != ' ' and ch != '\r' and ch != '\n' and ch != '\t':
            return
        else:
            decoder = AttributeDecoder()

        self.m_stateStack.push(decoder)
        if decoder.allowGenXPValueBeforeFinish():
            xpValue = decoder.genXPValue(rawText)
            xpValue.setParent(self.m_curValue)
            if decoder.allowHasChild(rawText):
                self.m_curValue = xpValue

        return decoder

    # 当需要切换状态是怎么处理
    def needSwitch(self, rawText, decodeResult):
        nextDecoder = decodeResult.genNextDecoder()
        self.m_stateStack.pop()
        self.m_stateStack.push(nextDecoder)
        if nextDecoder.allowGenXPValueBeforeFinish():
            xpValue = nextDecoder.genXPValue(rawText)
            xpValue.setParent(self.m_curValue)
            if nextDecoder.allowHasChild(rawText):
                self.m_curValue = xpValue
        return

    def appendChild(self, rawText, decodeResult):
        nextDecoder = decodeResult.genNextDecoder()
        self.m_stateStack.push(nextDecoder)
        if nextDecoder.allowGenXPValueBeforeFinish():
            xpValue = nextDecoder.genXPValue(rawText)
            xpValue.setParent(self.m_curValue)
            if nextDecoder.allowHasChild(rawText):
                self.m_curValue = xpValue
        return

    def finish(self, rawText):
        topDecoder = self.m_stateStack.pop()
        if not topDecoder.allowGenXPValueBeforeFinish():
            xpValue = topDecoder.genXPValue(rawText)
            self.m_curValue.addChild(xpValue)
        else:# 当解析完成之后之后，需要把当前的Value还原成parent
            if topDecoder.allowHasChild(rawText):
                xpValue = self.m_curValue
                self.m_curValue = xpValue.getParent()
                self.m_curValue.addChild(xpValue)
            else:
                xpValue = topDecoder.genXPValue(rawText)
                self.m_curValue.addChild(xpValue)
        return
