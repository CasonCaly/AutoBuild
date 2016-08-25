# coding: UTF-8
from pbxproj.XcodeProject import XcodeProject


class XCodeProjectBatchModifier:

    FrameworkModel = 1
    ProjectModel = 2

    FrameworkProject = {"build/cocos2d_libs":"libcocos2d iOS",
                        "cocos/scripting/lua-bindings/proj.ios_mac/cocos2d_lua_bindings":"libluacocos2d iOS",
                        "scx/DragonBones/proj.ios_mac/dragonbones":"libdragonbones",
                        "scx/battle/proj.ios_mac/scxbattle":"libscxbattle",
                        "scx/core/proj.ios_mac/scxcore":"libscxcore",
                        "scx/ui/proj.ios_mac/scxui":"libscxui",
                        "scx/tolua/proj.ios_mac/luascx":"libluascx",
                        "scx/objc/libscx_objc":"libscx_objc"}

    def __init__(self):
        self.m_frameworkPath = ""
        self.m_projectPath = ""
        self.m_model = -1
        self.m_frameworkXcodeProj = []
        return

    def initForFramework(self, frameworkPath):
        self.m_frameworkPath = frameworkPath
        self.m_model = XCodeProjectBatchModifier.FrameworkModel
        for projectName, target in XCodeProjectBatchModifier.FrameworkProject.items():
            fullPath = self.m_frameworkPath + "/" + projectName
            xcodeProject = XcodeProject("", "")
            xcodeProject.initWithFullPath(fullPath)
            xcodeProject.setTarget(target)
            if not xcodeProject.parse():
                print "Parse " + fullPath + " failure"
            self.m_frameworkXcodeProj.append(xcodeProject)

    def replaceFrameworkVALID_ARCHS(self, newDeine):
        for xcodeProject in self.m_frameworkXcodeProj:
            target = xcodeProject.getTarget()
            buildSettings = xcodeProject.getBuildSettings(target, XcodeProject.Release)
            buildSettings.replaceVALID_ARCHS(newDeine)
            buildSettings = xcodeProject.getBuildSettings(target, XcodeProject.Debug)
            buildSettings.replaceVALID_ARCHS(newDeine)

    def saveFramework(self):
        for xcodeProject in self.m_frameworkXcodeProj:
            xcodeProject.writeDefalt()

    def initForProject(self):
        self.m_model = XCodeProjectBatchModifier.ProjectModel


modifer = XCodeProjectBatchModifier()
# modifer.initForFramework("F:/common/client/frameworks/cocos2d-x-3.8.1")
# modifer.replaceFrameworkVALID_ARCHS("arm64 armv7 armv7s x86_64 i386")
# modifer.saveFramework()

