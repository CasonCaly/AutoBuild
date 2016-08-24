# coding: UTF-8
import os
from toolkit.Process import Process
from pbxproj.XcodeProject import XcodeProject


class CocosIOSLibBuilder:
    def __init__(self, projectPath, projectName, target):
        self.m_projectPath = projectPath
        self.m_projectName = projectName
        self.m_target = target

    def buildSimulator(self):
        fullPath = self.fullProjectPath()
        command = "xcodebuild -sdk iphonesimulator -project " + fullPath + " -target " + self.targetFilter() + " -configuration Release "
        self.useXcodeBuild(command)
        return

    def buildReleaseDevice(self):
        fullPath = self.fullProjectPath()
        command = "xcodebuild -project " + fullPath + " -target " + self.targetFilter() + " -configuration Release"
        self.useXcodeBuild(command)
        return

    def targetFilter(self):
        target = self.m_target
        if " " in self.m_target:
            target = "\"" + self.m_target + "\""
        return target

    def buildDebugDevice(self):
        self.backupFile()

        xcodeProj = XcodeProject(self.m_projectPath, self.m_projectName)
        xcodeProj.parse()
        pbxProject = xcodeProj.getPBXProject()

        pbxNativeTarget = pbxProject.getTarget(self.m_target)
        xcConfigurationList = pbxNativeTarget.getXCConfigurationList()
        xcBuildConfiguration = xcConfigurationList.getBuildConfiguration("Release")
        buildSettings = xcBuildConfiguration.getBuildSettings()
        isSuccess = buildSettings.replaceGCC_PREPROCESSOR_DEFINITIONS("NDEBUG", "COCOS2D_DEBUG=1")

        if not isSuccess:
            defaultXCConfigurationList = pbxProject.getXCConfigurationList()
            defaultXCBuildConfiguration = defaultXCConfigurationList.getBuildConfiguration("Release")
            defaultBuildSettings = defaultXCBuildConfiguration.getBuildSettings()
            isSuccess = defaultBuildSettings.replaceGCC_PREPROCESSOR_DEFINITIONS("NDEBUG", "COCOS2D_DEBUG=1")
            if not isSuccess:
                print "Can not find GCC_PREPROCESSOR_DEFINITIONS NDEBUG"
        xcodeProj.writeToFile(self.fullProjectPath(), "")
        self.buildReleaseDevice()
        self.resumeFile()

    #def replaceWith

    def backupFile(self):
        srcFullPath = self.fullProjectPath()
        srcFullPath += "/project.pbxproj"

        srcFile = open(srcFullPath)
        allText = srcFile.read()
        srcFile.close()

        destFullPath = srcFullPath + ".backup"
        destFile = open(destFullPath, "wb")
        destFile.write(allText)
        destFile.close()
        return allText

    def resumeFile(self):
        # 移除被修改的文件
        destFullPath = self.fullProjectPath()
        destFullPath += "/project.pbxproj"
        if os.path.exist(destFullPath):
            os.remove(destFullPath)

        # 将project.pbxproj.backup文件重命名为project.pbxproj
        srcFullPath = self.fullProjectPath()
        srcFullPath += "/project.pbxproj.backup"
        os.rename(srcFullPath, destFullPath)

    def useLipo(self):
        simulatorOutPath = self.fullOutPath(True)
        deviceOutPath = self.fullOutPath(False)
        lipoPath = self.fullPathInProject("build/lipo/" + self.m_target + ".a")
        command = "lipo -create " + simulatorOutPath + " " + deviceOutPath + " -output " + lipoPath
        Process.execute(command)

    def useXcodeBuild(self, command):
        Process.execute(command)

    def fullProjectPath(self):
        fullPath = self.fullPathInProject(self.m_projectName)
        return fullPath

    def fullOutPath(self, isSimulator):
        subOutPath = "build/"
        if isSimulator:
            subOutPath += "Release-iphonesimulator/" + self.targetFilter() + ".a"
        else:
            subOutPath += "Release-iphoneos/" + self.targetFilter() + ".a"
        return self.fullPathInProject(subOutPath)

    def fullPathInProject(self, subPath):
        fullPath = self.m_projectPath
        strLen = len(self.m_projectPath)
        if 0 != len:
            lastChar = self.m_projectPath[strLen - 1]
            if lastChar != '/':
                fullPath += '/'

        return fullPath + subPath + ".xcodeproj"


builder = CocosIOSLibBuilder(
    "/Users/nervecell/workspaces/boyi_all_client/common/client/frameworks/cocos2d-x-3.8.1/build", "cocos2d_libs",
    "libcocos2d iOS")
builder.buildSimulator()
builder.buildDebugDevice()
builder.useLipo()
