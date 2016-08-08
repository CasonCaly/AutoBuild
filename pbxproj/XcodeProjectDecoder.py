# coding:utf-8
from toolkit import Stack

"""
解码状态机中状态基类
"""

class ParseResult:

    Error = 1       # 出现错误
    NeedSwitch = 2  # 需要切换状态
    Pending = 3     # 未决，表示还未解析完成
    Finish = 4      # 解析成功并且完成

    PendingParseResult = None
    FinishParseResult = None

    def __init__(self, state):
        self.m_state = state
        self.m_nextDecoderName = None
        self.m_backNum = 0

    def getState(self):
        return self.m_state

    def setNextDecoderName(self, nextDecoderName):
        self.m_nextDecoderName = nextDecoderName

    def genNextDecoder(self):
        if None == self.m_nextDecoderName:
            return None
        return eval(self.m_nextDecoderName+"()")

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
        return  result

class Decoder:

    def __init__(self):
        self.m_isEnd = False
        self.m_statementStartIndex = -1
        self.m_statementLength = 0
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

"""
行注释解码
"""


class LineCommandDecoder(Decoder):

    def __init__(self):

        return

    def parse(self, ch, index):
        if self.m_statementLength == 2 and ch == '*': # 如果碰到*表示本次是块注释
            return Decoder.needSwitch("ChunckCommandDecoder", 2) # 回退两个字符,并转为块注释
        elif ch == '\n': #碰到换行表示结束
            return ParseResult.finish()
        else:
            return ParseResult.pending()


"""
块注释解码
"""


class ChunckCommandDecoder(Decoder):
    def __init__(self):
        return

    def parse(self, ch, index):
        return

"""
对象状态
"""


class ObjectDecoder(Decoder):
    def __init__(self):
        return

    def parse(self, ch, index):
        return

"""
键值对状态
"""


class KeyValueState(Decoder):
    def __init__(self):
        return

    def parse(self, ch, index):
        return

"""
工程文件解码器
"""


class XcodeProjectDecoder:
    def __init__(self):
        self.m_stateStack = Stack()
        return

    def decode(self, rawString):
        ch = rawString[0]
        index = 0
        while(ch != 0):
            ch = rawString[index]

            if self.m_stateStack.isEmpty():
                self.autoSelectDecoder(ch)

            topDecoder = self.m_stateStack.top()
            topDecoder.parseBegin(index)
            decodeResult = topDecoder.parse(ch, index)
            decodeState = decodeResult.getState()

            if decodeState == ParseResult.Pending:
                continue
            elif decodeState == ParseResult.NeedSwitch:
                index -= decodeState.getBackNum()
                nextDecoder = decodeState.genNextDecoder()
                self.m_stateStack.pop()
                self.m_stateStack.push(nextDecoder)
            elif decodeState == ParseResult.Finish:
                ch = rawString[index + 1]
                self.autoSelectDecoder(ch)

            index += 1
        return

    # 自动选择解码器
    def autoSelectDecoder(self, ch):
        decoder = None
        if ch == '/':
            decoder = LineCommandDecoder()
        elif ch == '{':
            decoder = ObjectDecoder()
        else:
            decoder = KeyValueState()

        self.m_stateStack.push(decoder)
        return



