# coding:utf-8
import os
import datetime
from toolkit.List import List
from XcodeProjectMetas import PBXAggregateTarget
from XcodeProjectDecoder import XcodeProjectDecoder
from XPValue import XPObject
from XPValue import XPAttribute
import platform
import cProfile

class XcodeProject:

    def __init__(self, projectPath, projectName):
        self.m_projectPath = projectPath
        self.m_projectName = projectName

        self.m_xpDocument = None
        self.m_arvhiveVersion = None
        self.m_classes = None
        self.m_objectVersion = None

        self.m_PBXAggregateTarget = PBXAggregateTarget()

    def parse(self):
        fullPath = self.m_projectPath + "/" + self.m_projectName + ".xcodeproj/project.pbxproj"
        if not os.path.exists(fullPath):
            return False

        file = open(fullPath)
        allText = file.read()
        project = XcodeProjectDecoder()
        project.decode(allText)

        self.m_xpDocument = project.getDocument()
        self.parseMetaData()
        return True

    def parseMetaData(self):
        rootObject = self.m_xpDocument.getRootValue()
        self.m_arvhiveVersion = rootObject.getValue('archiveVersion')
        self.m_classes = rootObject.getValue('classes')
        self.m_objectVersion = rootObject.getValue('objectVersion')
        objects = rootObject.getValue("objects")

        attributes = objects.getAttributes()
        for value in attributes.values():
            if isinstance(value, XPObject):
                typ = value.getValue("isa")
                if typ.equals("PBXAggregateTarget"):
                    int = 0
        #objectsValue = rootObject.getValue("objects")


    def toString(self):
        return ""

    def writeToFile(self, path):

        return

def test():
    sysstr = platform.system()
    if sysstr == "Darwin":
        xcodeProj = XcodeProject("/Users/Nervecell/Desktop/cocos2d-x-3.8.1/build", "cocos2d_libs")
    else:
        xcodeProj = XcodeProject("F:/common/client/frameworks/cocos2d-x-3.8.1/build", "cocos2d_tests")
    d1 = datetime.datetime.now()
    project = xcodeProj.parse()
    d2 = datetime.datetime.now()
    diff = d2 - d1
    print diff

if __name__ == "__main__":
    test()
    #cProfile.run("test()")
