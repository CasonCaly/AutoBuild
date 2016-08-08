#coding:utf-8




class XcodeProject:

    def __init__(self, projectPath, projectName):
        self.m_projectPath = projectPath
        self.m_projectName = projectName

    def parse(self):
        fullPath = self.m_projectPath + "/" + self.m_projectName + ".xcodeproj/project.pbxproj"
        project = XcodeProject.Load(fullPath)
        return project

    def decode(self):

        return

xcodeProj = Xcodeproj("F:/common/client/frameworks/cocos2d-x-3.8.1/build", "cocos2d_libs")
project = xcodeProj.parse()