# coding:utf-8
import Stack


"""
解码状态机中状态基类
"""


class Decoder:

    Error = 1       # 出现错误
    NeedSwitch = 2  # 需要切换状态
    Pending = 3     # 未决，表示还未解析完成
    Finish = 4      # 解析成功并且完成

    def __init__(self):
        self.m_isEnd = False
        self.m_statementStartIndex = -1
        self.m_statementLength = 0
        self.m_backCharNumWhenSwitch = 0
        return

    def parse(self, ch, index):
        if self.m_statementStartIndex == -1:
            self.m_statementStartIndex = index
        self.m_statementLength += 1

        return

    # 本次状态是否已经结束
    def isEnd(self):
        return self.m_isEnd

    # 设置是否已经结束
    def setIsEnd(self, isEnd):
        self.m_isEnd = isEnd

    # 当状态切换的时候需要回退的字符数
    def backCharNumWhenSwitch(self):
        return self.m_backCharNumWhenSwitch
"""
行注释状态
"""


class LineCommandDecoder(Decoder):
    def __init__(self):

        return

    def parse(self, ch, index):
        if self.m_statementStartIndex == -1:
            self.m_statementStartIndex = index
        else:
            if self.m_statementLength == 1 and ch == '*': # 如果碰到*表示本次是块注释
                self.m_backCharNumWhenSwitch = 2 # 回退两个字符
                return Decoder.NeedSwitch
            elif ch == '\n': #碰到换行表示结束
                return Decoder.Finish

        self.m_statementLength += 1

        return Decoder.Pending


"""
块注释状态
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
            index += 1
            if self.m_stateStack.isEmpty():
                self.autoState(ch)
            else:
                self.stateSwitch(ch)
            topState = self.m_stateStack.top()
            backCharNumWhenSwitch = topState.backCharNumWhenSwitch()
            if 0 != backCharNumWhenSwitch:
                self.m_stateStack.pop()
            index -= backCharNumWhenSwitch

        return

    # 自动选择解析状态
    def autoState(self, ch):
        state = None
        if ch == '/':
            state = LineCommandDecoder()
        elif ch == '{':
            state = ObjectDecoder()
        else:
            state = KeyValueState()

        state.parse(ch)
        self.m_stateStack.push(state)
        return

    def stateSwitch(self, ch):
        return


