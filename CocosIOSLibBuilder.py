# coding: UTF-8

import subprocess


class CocosIOSLibBuilder:

    def __init__(self, projectPath, projectName, target):
        self.m_projectPath = projectPath
        self.m_projectName = projectName
        self.m_target = target

    def buildSimulator(self):
        fullPath = self.fullProjectPath()
        command = "xcodebuild -sdk iphonesimulator -project " + fullPath + " -target " + self.m_target + " -configuration Release "
        self.useXcodeBuild(command)
        return

    def buildDevice(self):
        fullPath = self.fullProjectPath()
        command = "xcodebuild -project " + fullPath + " -target " + self.m_target + " -configuration Release"
        self.useXcodeBuild(command)
        return

    def useLipo(self):
        simulatorOutPath = self.fullOutPath(True)
        deviceOutPath = self.fullOutPath(False)
        lipoPath = self.fullPathInProject("build/lipo/"+self.m_target+".a")
        command = "lipo -create " + simulatorOutPath + " " + deviceOutPath + " -output " + lipoPath
        print command
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = p.communicate()
        print output[0]

    def useXcodeBuild(self, command):
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = p.communicate()
        print output[0]
        #print p.stdout.readlines()
        #for line in p.stdout.readlines():
        #    print line

        #retval = p.wait()

    def fullProjectPath(self):
        fullPath = self.fullPathInProject(self.m_projectName)
        return fullPath

    def fullOutPath(self, isSimulator):
        subOutPath = "build/"
        if isSimulator:
            subOutPath += "Release-iphonesimulator/" + self.m_target + ".a"
        else:
            subOutPath += "Release-iphoneos/" + self.m_target + ".a"
        return self.fullPathInProject(subOutPath)

    def fullPathInProject(self, subPath):
        fullPath = self.m_projectPath
        strLen = len(self.m_projectPath)
        if 0 != len:
            lastChar = self.m_projectPath[strLen - 1]
            if lastChar != '/':
                fullPath += '/'

        return fullPath + subPath

builder = CocosIOSLibBuilder("/Users/Nervecell/Desktop/cocos2d-x-3.8.1/build", "cocos2d_libs.xcodeproj", "libcocos2d_iOS")
#builder.buildSimulator()
#builder.buildDevice()
builder.useLipo()