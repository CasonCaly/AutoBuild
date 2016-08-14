# coding:utf-8
import os
import datetime
from XcodeProjectDecoder import XcodeProjectDecoder
import platform
import cProfile

class XcodeProject:

    def __init__(self, projectPath, projectName):
        self.m_projectPath = projectPath
        self.m_projectName = projectName

    def parse(self):
        fullPath = self.m_projectPath + "/" + self.m_projectName + ".xcodeproj/project.pbxproj"
        if not os.path.exists(fullPath):
            return False

        file = open(fullPath)
        allText = file.read()
        project = XcodeProjectDecoder()
        project.decode(allText)

        return True

    def decode(self):

        return

def test():
    xcodeProj = None
    if sysstr == "Darwin":
        xcodeProj = XcodeProject("/Users/Nervecell/Desktop/cocos2d-x-3.8.1/build", "cocos2d_tests")
    else:
        xcodeProj = XcodeProject("F:/common/client/frameworks/cocos2d-x-3.8.1/build", "cocos2d_tests")
    project = xcodeProj.parse()

if __name__ == "__main__":

    sysstr = platform.system()
    d1 = datetime.datetime.now()
    cProfile.run("test()")
    d2 = datetime.datetime.now()
    diff = d2-d1
    print diff