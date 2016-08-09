# coding:utf-8
from toolkit import Stack
from XPValue import XPDocument

"""
解码状态机中状态基类
"""


class ParseResult:
    Error = 1  # 出现错误
    NeedSwitch = 2  # 需要切换状态
    Pending = 3  # 未决，表示还未解析完成
    Finish = 4  # 解析成功并且完成
    AppendChild = 5  # 附加新的子解码器
    AppendSibling = 6  # 附加新的兄弟解码器

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

        return ParseResult.PendingParseResult

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
        self.m_xpValue = None
        return

    def parseBegin(self, index):
        if self.m_statementStartIndex == -1:
            self.m_statementStartIndex = index

    def parse(self, ch, index):
        if self.m_statementStartIndex == -1:
            self.m_statementStartIndex = index
        self.m_statementLength += 1

    def parseEnd(self):
        self.m_statementLength += 1

    def genXPValue(self):
        return self.m_xpValue

    def allowGenXPValueBeforeFinish(self):
        return True

    def allowHasChild(self):
        return True
"""
行注释解码
"""


class LineCommentsDecoder(Decoder):
    def __init__(self):

        return

    def parse(self, ch, index):
        if self.m_statementLength == 1:
            if ch == '*':  # 如果碰到*表示本次是块注释
                return Decoder.needSwitch("ChunckCommentsDecoder", 2)  # 回退两个字符,并转为块注释
            elif ch != '/':
                return Decoder.error()
        elif ch == '\n':  # 碰到换行表示结束
            return ParseResult.finish()

        return ParseResult.pending()

    def allowGenXPValueBeforeFinish(self):
        return False

    def allowHasChild(self):
        return False
"""
块注释解码
"""


class ChunckCommentsDecoder(Decoder):
    def __init__(self):
        self.m_isEndStar = False
        return

    def parse(self, ch, index):
        if self.m_statementLength == 1:
            if ch != '*':  # 如果碰到*表示本次是块注释
                return Decoder.error()
        elif ch == '*':
            self.m_isEndStar = True
        elif ch == '/' and self.m_isEndStar:  # 遇到*/表示注释结束
            return ParseResult.finish()
        else:
            self.m_isEndStar = False

        return ParseResult.pending()

    def allowHasChild(self):
        return False

"""
对象状态
"""


class ObjectDecoder(Decoder):
    def __init__(self):
        return

    def parse(self, ch, index):
        if ch != ' ' and ch != '\r' and ch != '\n' and ch != '\t':
            if ch == '/':
                return ParseResult.appendChild("LineCommandDecoder")
            else:
                return ParseResult.appendChild("KeyValueDecoder")
        elif ch == '}':
            return ParseResult.finish()
        return ParseResult.pending()


"""
键值对状态
"""


class KeyValueDecoder(Decoder):
    def __init__(self):
        return

    def parse(self, ch, index):
        if ch != ' ' and ch != '\r' and ch != '\n' and ch != '\t':
            if ch == '/':
                return ParseResult.appendChild("LineCommandDecoder")
            elif ch == '{':
                return ParseResult.appendChild("ObjectDecoder")
        elif ch == ';':
            return ParseResult.finish()
        return ParseResult.pending()


class ArrayDecoder(Decoder):
    def __init__(self):
        return

    def parse(self, ch, index):
        if ch != ' ' and ch != '\r' and ch != '\n' and ch != '\t':
            if ch == '/':
                return ParseResult.appendChild("LineCommandDecoder")
        elif ch == ',':
            return ParseResult.finish()
        return ParseResult.pending()


"""
工程文件解码器
"""


class XcodeProjectDecoder:
    def __init__(self):
        self.m_stateStack = Stack()
        self.m_document = XPDocument()
        self.m_curValue = self.m_document
        return

    def decode(self, rawString):
        ch = rawString[0]
        index = 0
        while (ch != 0):
            ch = rawString[index]

            if self.m_stateStack.isEmpty():
                autoDecoder = self.autoSelect(ch)

            topDecoder = self.m_stateStack.top()
            topDecoder.parseBegin(index)
            decodeResult = topDecoder.parse(ch, index)

            decodeState = decodeResult.getState()
            if decodeState == ParseResult.Pending:
                topDecoder.parseEnd()
                continue
            elif decodeState == ParseResult.NeedSwitch:
                index -= decodeState.getBackNum()
                self.needSwitch(decodeState)
                continue
            elif decodeState == ParseResult.AppendChild:
                index -= decodeState.getBackNum()
                self.appendChild(decodeState)
                continue
            elif decodeState == ParseResult.Finish:
                decodeState.parseEnd()
                ch = rawString[index + 1]
                self.finish()
                self.autoSelect(ch)
            elif decodeState == ParseResult.Error:
                break

            index += 1
        return

    # 自动选择解码器
    def autoSelect(self, ch):
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
            decoder = KeyValueDecoder()

        self.m_stateStack.push(decoder)
        if decoder.allowGenXPValueBeforeFinish():
            xpValue = decoder.genXPValue()
            self.m_curValue.addChild(xpValue)
            if decoder.allowHasChild():
                self.m_curValue = xpValue

        return decoder

    # 当需要切换状态是怎么处理
    def needSwitch(self, decodeState):
        nextDecoder = decodeState.genNextDecoder()
        self.m_stateStack.pop()
        self.m_stateStack.push(nextDecoder)
        if nextDecoder.allowGenXPValueBeforeFinish():
            xpValue = nextDecoder.genXPValue()
            self.m_curValue.addChild(xpValue)
            if nextDecoder.allowHasChild():
                self.m_curValue = xpValue
        return

    def appendChild(self, decodeState):
        nextDecoder = decodeState.genNextDecoder()
        self.m_stateStack.push(nextDecoder)
        if nextDecoder.allowGenXPValueBeforeFinish():
            xpValue = nextDecoder.genXPValue()
            self.m_curValue.addChild(xpValue)
            if nextDecoder.allowHasChild():
                self.m_curValue = xpValue
        return

    def finish(self):
        topDecoder = self.m_stateStack.pop()
        if not topDecoder.allowGenXPValueBeforeFinish():
            xpValue = topDecoder.genXPValue()
            self.m_curValue.addChild(xpValue)
        else:# 当解析完成之后之后，需要把当前的Value还原成parent
            self.m_curValue = self.m_curValue.getParent()
        return
