# coding: UTF-8
import os
from toolkit.Process import Process
from pbxproj.XcodeProject import XcodeProject


class CocosIOSLibBuilder:

    def __init__(self, projectPath, projectName, target, prebuiltPath):
        self.m_projectPath = projectPath
        self.m_projectName = projectName
        self.m_target = target
        self.m_prebuiltPath = prebuiltPath

    def buildRelease(self):
        oldFullPath = self.fullProjectPath("")
        newFullPath = self.fullProjectPath("Release")
        if os.path.exists(oldFullPath):
            os.rename(oldFullPath, newFullPath)
        else:
            print "Error: Xcode Project not found "+oldFullPath
            return

        command = "xcodebuild -project " + newFullPath + " -target " + self.targetFilter() + " -configuration Release"
        Process.execute(command)
        os.rename(newFullPath, oldFullPath)

        self.copyReleaseLib()
        return

    def copyReleaseLib(self):
        deviceOutPath = "\"" + self.fullOutPath(False) + "\""
        prebuiltPath = "\"" + self.m_prebuiltPath + "/release/" + self.m_target + ".a" + "\""
        cpCommand = "cp " + deviceOutPath + " " + prebuiltPath
        Process.execute(cpCommand)

    def buildDebug(self):
        self.buildWithDebug(False)
        self.buildWithDebug(True)
        self.lipoDebugLib()

    def lipoDebugLib(self):
        simulatorOutPath = "\"" + self.fullOutPath(True) + "\""
        deviceOutPath = "\"" + self.fullOutPath(False) + "\""
        lipoPath = "\"" + self.m_prebuiltPath + "/debug/" + self.m_target + ".a" + "\""
        command = "lipo -create " + simulatorOutPath + " " + deviceOutPath + " -output " + lipoPath
        Process.execute(command)

    def buildWithDebug(self, isSimulator):
        if not self.backupFile():
            return

        xcodeProj = XcodeProject(self.m_projectPath, self.m_projectName)
        xcodeProj.parse()
        pbxProject = xcodeProj.getPBXProject()
        buildSettings = pbxProject.getBuildSettings(self.m_target, "Release")
        isSuccess = buildSettings.replaceGCC_PREPROCESSOR_DEFINITIONS("NDEBUG", "COCOS2D_DEBUG=1")

        if not isSuccess:
            defaultBuildSettings = xcodeProj.getDefaultBuildSettings("Release")
            isSuccess = defaultBuildSettings.replaceGCC_PREPROCESSOR_DEFINITIONS("NDEBUG", "COCOS2D_DEBUG=1")
            if not isSuccess:
                print "Can not find GCC_PREPROCESSOR_DEFINITIONS NDEBUG"
        xcodeProj.writeToFile(self.fullProjectPath(""), "")

        oldFullPath = self.fullProjectPath("")
        newFullPath = self.fullProjectPath("Debug")
        os.rename(oldFullPath, newFullPath)

        if isSimulator:
            command = "xcodebuild -sdk iphonesimulator -project " + newFullPath + " -target " + self.targetFilter() + " -configuration Release "
        else:
            command = "xcodebuild -project " + newFullPath + " -target " + self.targetFilter() + " -configuration Release"

        Process.execute(command)
        os.rename(newFullPath, oldFullPath)
        self.resumeFile()

    def targetFilter(self):
        target = self.m_target
        if " " in self.m_target:
            target = "\"" + self.m_target + "\""
        return target

    def backupFile(self):
        srcFullPath = self.fullProjectPath("")
        srcFullPath += "/project.pbxproj"

        if not os.path.exists(srcFullPath):
            print "Could not backup " + srcFullPath
            return False

        srcFile = open(srcFullPath)
        allText = srcFile.read()
        srcFile.close()

        destFullPath = srcFullPath + ".backup"
        destFile = open(destFullPath, "wb")
        destFile.write(allText)
        destFile.close()
        return True

    def resumeFile(self):
        # 移除被修改的文件
        destFullPath = self.fullProjectPath("")
        destFullPath += "/project.pbxproj"
        if os.path.exists(destFullPath):
            os.remove(destFullPath)

        # 将project.pbxproj.backup文件重命名为project.pbxproj
        srcFullPath = self.fullProjectPath("")
        srcFullPath += "/project.pbxproj.backup"
        os.rename(srcFullPath, destFullPath)

    def fullProjectPath(self, configType):
        if "" != configType:
            fullPath = self.m_projectPath + "/" + self.m_projectName + "_" + configType + ".xcodeproj"
        else:
            fullPath = self.m_projectPath + "/" + self.m_projectName + ".xcodeproj"
        return fullPath

    def fullOutPath(self, isSimulator):
        subOutPath = "/build/"
        if isSimulator:
            subOutPath += "Release-iphonesimulator/" + self.m_target + ".a"
        else:
            subOutPath += "Release-iphoneos/" + self.m_target + ".a"
        fullPath = self.m_projectPath + subOutPath
        return fullPath

    def fullPathInProject(self, subPath):
        fullPath = self.m_projectPath
        strLen = len(self.m_projectPath)
        if 0 != len:
            lastChar = self.m_projectPath[strLen - 1]
            if lastChar != '/':
                fullPath += '/'

        return fullPath + subPath + ".xcodeproj"


# builder = CocosIOSLibBuilder("/Users/nervecell/workspaces/boyi_all_client/common/client/frameworks/cocos2d-x-3.8.1/build", "cocos2d_libs", "libcocos2d iOS", "/Users/nervecell/workspaces/boyi_all_client/common/client/frameworks/prebuilt/build/iOS")
# builder.buildSimulator()
# builder.buildDebug()
# builder.lipoDebugLib()
# builder.buildRelease()
# builder.copyReleaseLib()