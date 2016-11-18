# coding:utf-8
import os
import datetime
import platform
# import cProfile


from XcodeProjectMetas import PBXProject
from XcodeProjectDecoder import XcodeProjectDecoder
from cStringIO import StringIO


class XcodeProject:

    Release = "Release"
    Debug = "Debug"

    def __init__(self, projectPath, projectName):
        self.m_projectPath = projectPath
        self.m_projectName = projectName
        self.m_fullPath = None

        self.m_xpDocument = None
        self.m_archiveVersion = None
        self.m_classes = None
        self.m_objectVersion = None
        self.m_PBXProject = PBXProject()
        self.m_target = None

    def initWithFullPath(self, fullPath):
        self.m_fullPath = fullPath

    def setTarget(self, target):
        self.m_target = target

    def getTarget(self):
        return self.m_target

    def parse(self):
        if self.m_fullPath is None:
            fullPath = self.m_projectPath + "/" + \
                self.m_projectName + ".xcodeproj/project.pbxproj"
        else:
            fullPath = self.m_fullPath + ".xcodeproj/project.pbxproj"

        if not os.path.exists(fullPath):
            return False

        targetFile = open(fullPath)
        allText = targetFile.read()
        project = XcodeProjectDecoder()
        project.decode(allText)
        targetFile.close()
        self.m_xpDocument = project.getDocument()
        self.parseMetaData()
        return True

    def parseMetaData(self):
        rootObject = self.m_xpDocument.getRootValue()
        self.m_archiveVersion = rootObject.getValue('archiveVersion')
        self.m_classes = rootObject.getValue('classes')
        self.m_objectVersion = rootObject.getValue('objectVersion')

        rootObjectId = rootObject.getValue("rootObject")

        objects = rootObject.getValue("objects")
        pbxProjectValue = objects.getValue(rootObjectId.getString())
        self.m_PBXProject.init(pbxProjectValue, objects)

    def getPBXProject(self):
        return self.m_PBXProject

    def getBuildSettings(self, target, configuartion):
        pbxNativeTarget = self.m_PBXProject.getTarget(target)
        xcConfigurationList = pbxNativeTarget.getXCConfigurationList()
        xcBuildConfiguration = xcConfigurationList.getBuildConfiguration(
            configuartion)
        buildSettings = xcBuildConfiguration.getBuildSettings()
        return buildSettings

    def getDefaultBuildSettings(self, configuartion):
        defaultXCConfigurationList = self.m_PBXProject.getXCConfigurationList()
        defaultXCBuildConfiguration = defaultXCConfigurationList.getBuildConfiguration(
            configuartion)
        defaultBuildSettings = defaultXCBuildConfiguration.getBuildSettings()
        return defaultBuildSettings

    def writeToFile(self, path, name):
        fullPath = path + "/" + name + "project.pbxproj"
        stringIO = StringIO()
        self.m_xpDocument.genStream(stringIO, 0)
        fo = open(fullPath, "wb")
        fo.write(stringIO.getvalue())
        fo.close()
        return

    def writeDefalt(self):
        if self.m_fullPath is None:
            fullPath = self.m_projectPath + "/" + \
                self.m_projectName + ".xcodeproj/project.pbxproj"
        else:
            fullPath = self.m_fullPath + ".xcodeproj/project.pbxproj"

        stringIO = StringIO()
        self.m_xpDocument.genStream(stringIO, 0)
        fo = open(fullPath, "wb")
        fo.write(stringIO.getvalue())
        fo.close()


def test():
    sysstr = platform.system()
    if sysstr == "Darwin":
        xcodeProj = XcodeProject(
            "/Users/Nervecell/Desktop/cocos2d-x-3.8.1/build", "cocos2d_libs")
    else:
        xcodeProj = XcodeProject(
            "F:/common/client/frameworks/cocos2d-x-3.8.1/build", "cocos2d_libs")
    d1 = datetime.datetime.now()
    xcodeProj.parse()
    d2 = datetime.datetime.now()
    diff = d2 - d1
    print diff

    if sysstr == "Darwin":
        xcodeProj.writeToFile("/Users/Nervecell/Desktop", "libs")
    else:
        pbxProject = xcodeProj.getPBXProject()

        pbxNativeTarget = pbxProject.getTarget("libcocos2d iOS")
        xcConfigurationList = pbxNativeTarget.getXCConfigurationList()
        xcBuildConfiguration = xcConfigurationList.getBuildConfiguration(
            "Release")
        buildSettings = xcBuildConfiguration.getBuildSettings()

        isSuceess = buildSettings.replaceGCC_PREPROCESSOR_DEFINITIONS(
            "NDEBUG", "\"COCOS2D_DEBUG=1\"")
        if not isSuceess:
            defaultXCConfigurationList = pbxProject.getXCConfigurationList()
            defaultXCBuildConfiguration = defaultXCConfigurationList.getBuildConfiguration(
                "Release")
            defaultBuildSettings = defaultXCBuildConfiguration.getBuildSettings()
            defaultBuildSettings.replaceGCC_PREPROCESSOR_DEFINITIONS(
                "NDEBUG", "\"COCOS2D_DEBUG=1\"")

        xcodeProj.writeToFile("F:\\", "")

# if __name__ == "__main__":
    # test()
    # cProfile.run("test()")
