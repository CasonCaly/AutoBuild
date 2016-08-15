# coding:utf-8

from toolkit.HashMap import HashMap
from XPValue import XPDocument
from XPValue import XPComments
from XPValue import XPObject
from XPValue import XPAttribute
from XPValue import XPArray
from XPValue import XPString

"""
工程文件解码器缓存项
"""


class DecoderCacheItem:
    def __init__(self, decoderName):
        self.m_decoderName = decoderName
        self.m_unusedQueue = []
        self.m_count = 0

    def newDecoder(self):
        if self.m_count == 0:
            decoder = eval(self.m_decoderName + "()")
        else:
            self.m_count -= 1
            decoder = self.m_unusedQueue.pop()
        return decoder

    def resumeDecoder(self, decoder):
        decoder.clean()
        self.m_count += 1
        self.m_unusedQueue.append(decoder)


class DecoderCache:
    s_instance = None

    def __init__(self):
        self.m_mapDecoder = {}

    def newDecoder(self, decoderName):
        cacheItem = None
        if decoderName in self.m_mapDecoder:
            cacheItem = self.m_mapDecoder[decoderName]

        if cacheItem is None:
            cacheItem = DecoderCacheItem(decoderName)
            self.m_mapDecoder[decoderName] = cacheItem
        return cacheItem.newDecoder()

    def resumeDecoder(self, decoder):
        cacheItem = self.m_mapDecoder[decoder.className()]
        cacheItem.resumeDecoder(decoder)

    @classmethod
    def getInstance(self):
        if DecoderCache.s_instance is None:
            DecoderCache.s_instance = DecoderCache()
        return DecoderCache.s_instance


"""
解码状态机中状态基类
"""


class ParseResult:
    Error = 1  # 出现错误
    Pending = 2  # 未决，表示还未解析完成
    Finish = 3  # 解析成功并且完成
    AppendChild = 4  # 附加新的子解码器

    PendingParseResult = None
    FinishParseResult = None

    s_resultCache = []
    s_resultCacheCount = 0

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
        if self.m_nextDecoderName is None:
            return None
        return DecoderCache.getInstance().newDecoder(self.m_nextDecoderName)

    def setBackNum(self, backNum):
        self.m_backNum = backNum

    def getBackNum(self):
        return self.m_backNum

    def clean(self, state):
        self.m_state = state
        self.m_nextDecoderName = None
        self.m_newDecoderName = None
        self.m_backNum = 0

    @classmethod
    def init(cls):
        ParseResult.PendingParseResult = ParseResult(ParseResult.Pending)
        ParseResult.FinishParseResult = ParseResult(ParseResult.Finish)

    @classmethod
    def error(cls):
        result = ParseResult(ParseResult.Error)
        return result

    @classmethod
    def appendChild(cls, nextDecoderName):
        result = None
        if ParseResult.s_resultCacheCount == 0:
            result = ParseResult(ParseResult.AppendChild)
        else:
            result = ParseResult.s_resultCache.pop()
            ParseResult.s_resultCacheCount -= 1
            result.clean(ParseResult.AppendChild)
        result.setNextDecoderName(nextDecoderName)
        return result

    @classmethod
    def resumeResult(cls, result):
        ParseResult.s_resultCache.append(result)
        ParseResult.s_resultCacheCount += 1


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

    def increaseStatementLenght(self, diffStatementLength):
        self.m_statementLength += diffStatementLength

    def getStatementLength(self):
        return self.m_statementLength

    def genXPValue(self):
        return None

    def allowGenXPValueBeforeFinish(self):
        return True

    def allowHasChild(self, rawText):
        return True

    def clean(self):
        self.m_isEnd = False
        self.m_statementStartIndex = -1
        self.m_statementLength = 0
        return

    def className(self):
        return "Decoder"


"""
行注释解码
"""


class CommentsDecoder(Decoder):
    def __init__(self):
        Decoder.__init__(self)
        self.m_isLine = True
        self.m_isEndStar = False  # 是否是块注释后面的*
        return

    def parse(self, rawText, ch, index):
        if self.m_statementLength == 1:  # 检测第二个字符
            if ch == '*':  # 如果碰到*表示本次是块注释
                self.m_isLine = False
                return ParseResult.PendingParseResult
            elif ch != '/':  # 如果是行注释，同时第二个字符不是/那么就表示错误
                return ParseResult.error()

        if self.m_isLine:
            if ch == '\n':  # 碰到换行表示结束
                return ParseResult.FinishParseResult
        else:
            if ch == '*':
                self.m_isEndStar = True
            else:
                if self.m_isEndStar:  # 遇到*/表示注释结束
                    if ch != '/':
                        return ParseResult.error()
                    else:
                        return ParseResult.FinishParseResult

        return ParseResult.PendingParseResult

    def allowGenXPValueBeforeFinish(self):
        return False

    def allowHasChild(self, rawText):
        return False

    def genXPValue(self, rawText):
        if self.m_isLine:
            start = self.m_statementStartIndex + 2  # 从//之后开始所以是要加2
            end = self.m_statementStartIndex + self.m_statementLength - 1  # 去掉\n
            comments = rawText[start:end]
            return XPComments(True, comments)
        else:
            start = self.m_statementStartIndex + 2  # // /*
            end = self.m_statementStartIndex + self.m_statementLength
            comments = rawText[start:end]
            return XPComments(False, comments)

    def clean(self):
        Decoder.clean(self)
        self.m_isLine = True
        self.m_isEndStar = False
        return

    def className(self):
        return "CommentsDecoder"


"""
带""的字符串解码
"""


class StringDecoder(Decoder):

    # allocCount = 1

    def __init__(self):
        Decoder.__init__(self)
        return

    def parse(self, rawText, ch, index):
        if self.m_statementLength == 0:
            return ParseResult.PendingParseResult
        if ch != '"':
            return ParseResult.PendingParseResult
        else:
            lastCh = rawText[index - 1]
            if lastCh != '\\':
                return ParseResult.FinishParseResult
            else:
                return ParseResult.PendingParseResult

    def genXPValue(self, rawText):
        start = self.m_statementStartIndex
        end = self.m_statementStartIndex + self.m_statementLength
        string = rawText[start:end]
        return XPString(string)

    def allowGenXPValueBeforeFinish(self):
        return False
    
    def className(self):
        return "StringDecoder"


"""
对象解码
"""


class ObjectDecoder(Decoder):
    def __init__(self):
        Decoder.__init__(self)
        return

    def parse(self, rawText, ch, index):
        if self.m_statementLength == 0:
            return ParseResult.PendingParseResult

        if ch == ' ' or ch == '\r' or ch == '\n' or ch == '\t':
            return ParseResult.PendingParseResult

        if ch == '/':
            return ParseResult.appendChild("CommentsDecoder")
        elif ch == '}':
            return ParseResult.FinishParseResult
        else:
            return ParseResult.appendChild("AttributeDecoder")

    def genXPValue(self, rawText):
        return XPObject()

    def className(self):
        return "ObjectDecoder"


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
            return ParseResult.PendingParseResult

        if ch == '/':
            nextCh = rawText[index + 1]
            if nextCh != '/' and nextCh != '*':
                return ParseResult.PendingParseResult
            else:
                return ParseResult.appendChild("CommentsDecoder")
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
                #  下面步骤剔除空格
                self.m_keyEnd = index
                while True:
                    lastCh = rawText[self.m_keyEnd - 1]  # 闭区间缘故所以要-1
                    if lastCh == ' ':
                        self.m_keyEnd -= 1
                    else:
                        break

                self.genXPValue(rawText)
                key = rawText[self.m_keyStart:self.m_keyEnd]
                self.m_attrValue.setKey(key)
                self.m_attrValue.addChild(XPString(key))
                self.m_valueStart = index + 1
            elif ch == ';':
                while True:
                    lastCh = rawText[self.m_valueStart]  # 开区间所以是从start开始
                    if lastCh == ' ':
                        self.m_valueStart += 1
                    else:
                        break

                self.m_valueEnd = index
                self.genXPValue(rawText)
                value = rawText[self.m_valueStart:self.m_valueEnd]
                self.m_attrValue.setValue(value)
                self.m_attrValue.addChild(XPString(value))
                return ParseResult.FinishParseResult

            return ParseResult.PendingParseResult

    def genXPValue(self, rawText):
        if self.m_attrValue is None:
            self.m_attrValue = XPAttribute()
        return self.m_attrValue

    def clean(self):
        Decoder.clean(self)
        self.m_attrValue = None
        self.m_keyStart = -1
        self.m_keyEnd = -1
        self.m_valueStart = -1
        self.m_valueEnd = -1
        return

    def className(self):
        return "AttributeDecoder"


"""
数组解码
"""


class ArrayDecoder(Decoder):
    def __init__(self):
        Decoder.__init__(self)
        self.m_arrValue = None
        self.m_nextValueBegin = -1
        self.m_nextValueLength = 0
        self.m_valueWithQuotation = False  # 数组的值是否有引号
        return

    def parse(self, rawText, ch, index):
        if ch == ' ' or ch == '\r' or ch == '\n' or ch == '\t':
            return ParseResult.PendingParseResult

        if ch == '/':
            nextCh = rawText[index + 1]
            if nextCh == '/' or nextCh == '*':
                return ParseResult.appendChild("CommentsDecoder")
            else:
                if -1 != self.m_nextValueBegin:
                    self.m_nextValueLength += 1
        elif ch == '"':
            self.m_valueWithQuotation = True
            return ParseResult.appendChild("StringDecoder")
        elif ch == ',':
            if not self.m_valueWithQuotation:  # 如果有引号的话不需要处理StringDecoder会自动把值加入到XPArray中
                strValue = rawText[self.m_nextValueBegin:self.m_nextValueBegin + self.m_nextValueLength]
                self.genXPValue(rawText)
                self.m_arrValue.addChild(XPString(strValue))
            self.cleanValueInfo()
            return ParseResult.PendingParseResult
        elif ch == ')':
            return ParseResult.FinishParseResult
        else:
            if 0 != self.m_statementLength:
                if -1 == self.m_nextValueBegin:
                    self.m_nextValueBegin = index
                self.m_nextValueLength += 1
        return ParseResult.PendingParseResult

    def genXPValue(self, rawText):
        if self.m_arrValue is None:
            self.m_arrValue = XPArray()
        return self.m_arrValue

    def cleanValueInfo(self):
        self.m_nextValueBegin = -1
        self.m_valueWithQuotation = False
        self.m_nextValueLength = 0

    def clean(self):
        Decoder.clean(self)
        self.cleanValueInfo()
        self.m_arrValue = None
        return

    def className(self):
        return "ArrayDecoder"


"""
工程文件解码器
"""


class XcodeProjectDecoder:
    def __init__(self):
        self.m_decoderStack = []
        self.m_decoderCount = 0
        self.m_document = XPDocument()
        self.m_curValue = self.m_document
        ParseResult.init()
        return

    def getDocument(self):
        return self.m_document

    # 解码器的主人口
    def decode(self, rawString):
        ch = rawString[0]
        index = 0
        length = len(rawString)
        while (ch != 0 and index < length):
            ch = rawString[index]

            if self.m_decoderCount == 0:
                self.autoSelect(rawString, ch)

            topDecoder = self.m_decoderStack[self.m_decoderCount - 1]
            if topDecoder is None:
                index += 1
                continue

            if topDecoder.m_statementStartIndex == -1:
                topDecoder.m_statementStartIndex = index

            decodeResult = topDecoder.parse(rawString, ch, index)
            decodeState = decodeResult.m_state
            if decodeState == ParseResult.Pending:
                topDecoder.m_statementLength += 1
            elif decodeState == ParseResult.AppendChild:
                self.appendChild(rawString, decodeResult)
                ParseResult.resumeResult(decodeResult)
                continue
            elif decodeState == ParseResult.Finish:
                topDecoder.m_statementLength += 1
                self.finish(rawString)
            elif decodeState == ParseResult.Error:
                break

            index += 1

        return

    # 自动选择解码器
    def autoSelect(self, rawText, ch):
        decoderCache = DecoderCache.getInstance()
        decoder = None

        if ch == '{':
            decoder = decoderCache.newDecoder("ObjectDecoder")
        elif ch == '(':
            decoder = decoderCache.newDecoder("ArrayDecoder")
        elif ch == '/':
            decoder = decoderCache.newDecoder("CommentsDecoder")
        elif ch != ' ' and ch != '\r' and ch != '\n' and ch != '\t':
            return
        else:
            decoder = decoderCache.newDecoder("AttributeDecoder")

        self.m_decoderStack.append(decoder)
        self.m_decoderCount += 1
        if decoder.allowGenXPValueBeforeFinish():
            xpValue = decoder.genXPValue(rawText)
            xpValue.setParent(self.m_curValue)
            if decoder.allowHasChild(rawText):
                self.m_curValue = xpValue

        return decoder

    def appendChild(self, rawText, decodeResult):
        nextDecoder = decodeResult.genNextDecoder()
        self.m_decoderStack.append(nextDecoder)
        self.m_decoderCount += 1
        if nextDecoder.allowGenXPValueBeforeFinish():
            xpValue = nextDecoder.genXPValue(rawText)
            xpValue.setParent(self.m_curValue)
            if nextDecoder.allowHasChild(rawText):
                self.m_curValue = xpValue
        return

    def finish(self, rawText):
        topDecoder = self.m_decoderStack.pop()
        self.m_decoderCount -= 1
        statementLength = topDecoder.getStatementLength()

        if not topDecoder.allowGenXPValueBeforeFinish():
            xpValue = topDecoder.genXPValue(rawText)
            self.m_curValue.addChild(xpValue)
        else:  # 当解析完成之后之后，需要把当前的Value还原成parent
            if topDecoder.allowHasChild(rawText):
                xpValue = self.m_curValue
                self.m_curValue = xpValue.getParent()
                self.m_curValue.addChild(xpValue)
            else:
                xpValue = topDecoder.genXPValue(rawText)
                self.m_curValue.addChild(xpValue)

        if 0 == self.m_decoderCount:
            return

        newTopDecoder = self.m_decoderStack[self.m_decoderCount - 1]
        if newTopDecoder is not None:
            newTopDecoder.increaseStatementLenght(statementLength)
        DecoderCache.getInstance().resumeDecoder(topDecoder)
        return
