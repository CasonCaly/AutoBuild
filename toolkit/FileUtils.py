# coding:utf-8
from toolkit.HashMap import HashMap
# 文件实体类,用于存放上一次拷贝过程中记录下来的文件信息
class CopyInfo:

    __destPath = ""  # 目标路径
    __srcPath = ""   # 源路径

    def __init__(self, destPath, srcPath):
        self.__destPath = destPath
        self.__srcPath = srcPath

    def getDestPath(self):
        return self.__destPath

    def getSrcPath(self):
        return self.__srcPath

class FileUtils:

    __sInstance = None  # 静态实例变量
    __mapCopyInfo = HashMap()

    @classmethod
    def getIntance(cls):
        if None == FileUtils.__sInstance:
            FileUtils.__sInstance = FileUtils()
        return FileUtils.__sInstance

    @classmethod
    def copyWithRecord(cls, srcPath, destPath):

        return

util1 = FileUtils.getIntance()
util1.add("sss", "sdfds")



