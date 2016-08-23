from toolkit.HashMap import HashMap


class PBXBuildFile:

    def __init__(self):
        return


class PBXFileReference:

    def __init__(self):
        return


class PBXFrameworksBuildPhase:

    def __init__(self):
        return


class PBXGroup:

    def __init__(self):
        return


class PBXHeadersBuildPhase:

    def __init__(self):
        return




class PBXSourcesBuildPhase:

    def __init__(self):
        return

class PBXAggregateTarget:

    def __init__(self):
        self.m_mapItem = HashMap()

    def addItem(self, attribute):

        return


class PBXContainerItemProxy:

    def __init__(self):
        return


class BuildSettings:

    def __init__(self):
        self.m_buildSettingsObject = None
        self.m_objects = None
        self.m_GCC_PREPROCESSOR_DEFINITIONSArray = None
        self.m_PBXProject = None
        return

    def init(self, buildSettingsObject, objects, pbxProject):
        self.m_buildSettingsObject = buildSettingsObject
        self.m_objects = objects
        self.m_PBXProject = pbxProject
        self.m_GCC_PREPROCESSOR_DEFINITIONSArray = self.m_buildSettingsObject.getValue("GCC_PREPROCESSOR_DEFINITIONS")

    def replaceGCC_PREPROCESSOR_DEFINITIONS(self, oldDefine, newDefine):
        if self.m_GCC_PREPROCESSOR_DEFINITIONSArray is None:
            return False

        children = self.m_GCC_PREPROCESSOR_DEFINITIONSArray.getChildren()
        for child in children:
            if child.equals(oldDefine):
                child.setString(newDefine)
                return True

        return False


class XCBuildConfiguration:

    def __init__(self):
        self.m_XCBuildConfigurationObject = None
        self.m_objects = None
        self.m_buildSettings = None
        self.m_name = None
        self.m_PBXProject = None
        return

    def init(self, XCBuildConfigurationObject , objects, pbxProject):
        self.m_XCBuildConfigurationObject = XCBuildConfigurationObject
        self.m_objects = objects
        self.m_PBXProject = pbxProject

    def getBuildSettings(self):
        if self.m_buildSettings is not None:
            return self.m_buildSettings
        buildSettingsObject = self.m_XCBuildConfigurationObject.getValue("buildSettings")
        self.m_buildSettings = BuildSettings()
        self.m_buildSettings.init(buildSettingsObject, self.m_objects, self.m_PBXProject)
        return self.m_buildSettings

    def getName(self):
        if self.m_name is not None:
            return self.m_name
        self.m_name = self.m_XCBuildConfigurationObject.getValue("name").getString()
        return self.m_name


class XCConfigurationList:

    def __init__(self):
        self.m_XCConfigurationListObject = None
        self.m_objects = None
        self.m_buildConfiguations = None
        self.m_PBXProject = None
        return

    def init(self, XCConfigurationListObject, objects, pbxProject):
        self.m_XCConfigurationListObject = XCConfigurationListObject
        self.m_objects = objects
        self.m_PBXProject = pbxProject

    def getBuildConfigurations(self):
        if self.m_buildConfiguations is not None:
            return self.m_buildConfiguations

        self.m_buildConfiguations = []
        buildConfigurationsArray = self.m_XCConfigurationListObject.getValue("buildConfigurations")
        children = buildConfigurationsArray.getChildren()
        for child in children:
            XCBuildConfigurationObject = self.m_objects.getValue(child.getString())
            xcBuildConfiguration = XCBuildConfiguration()
            xcBuildConfiguration.init(XCBuildConfigurationObject, self.m_objects, self.m_PBXProject)
            self.m_buildConfiguations.append(xcBuildConfiguration)

        return self.m_buildConfiguations

    def getBuildConfiguration(self, targetName):
        self.getBuildConfigurations()
        if self.m_buildConfiguations is None:
            return None

        for buildConfiguration in self.m_buildConfiguations:
            name = buildConfiguration.getName()
            if targetName == name:
                return buildConfiguration
        return None


class PBXNativeTarget:

    def __init__(self):
        self.m_pbxNativeTargetObject = None
        self.m_objects = None
        self.m_name = None
        self.m_productName = None
        self.m_XCConfigurationList = None
        self.m_PBXProject = None

    def init(self, pbxNativeTargetObject, objects, pbxProject):
        self.m_objects = objects
        self.m_pbxNativeTargetObject = pbxNativeTargetObject
        self.m_PBXProject = pbxProject

    def getName(self):
        if self.m_name is not None:
            return self.m_name
        self.m_name = self.m_pbxNativeTargetObject.getValue("name").getString()
        return self.m_name

    def getProductName(self):
        if self.m_productName is not None:
            return self.m_productName
        self.m_productName = self.m_pbxNativeTargetObject.getValue("productName")
        return self.m_productName

    def getXCConfigurationList(self):
        if self.m_XCConfigurationList is not None:
            return self.m_XCConfigurationList

        buildConfigurationListUUID = self.m_pbxNativeTargetObject.getValue("buildConfigurationList")
        XCConfigurationListObject = self.m_objects.getValue(buildConfigurationListUUID.getString())
        self.m_XCConfigurationList = XCConfigurationList()
        self.m_XCConfigurationList.init(XCConfigurationListObject, self.m_objects, self.m_PBXProject)
        return self.m_XCConfigurationList


class PBXProject:

    def __init__(self):
        self.m_objects = None
        self.m_targetsList = None
        self.m_pbxProjectObject = None
        self.m_xcConfigurationList = None
        return

    def init(self, pbxProjectObject, object):
        self.m_pbxProjectObject = pbxProjectObject
        self.m_objects = object

    def getTargets(self):
        if self.m_targetsList is not None:
            return self.m_targetsList

        self.m_targetsList = []
        targetsArray = self.m_pbxProjectObject.getValue("targets")
        children = targetsArray.getChildren()
        for child in children:
            pbxNativeTargetValue = self.m_objects.getValue(child.getString())
            pbxNativeTarget = PBXNativeTarget()
            pbxNativeTarget.init(pbxNativeTargetValue, self.m_objects, self)
            self.m_targetsList.append(pbxNativeTarget)

    def getXCConfigurationList(self):
        if self.m_xcConfigurationList is not None:
            return self.m_xcConfigurationList

        buildConfigurationListUUID = self.m_pbxProjectObject.getValue("buildConfigurationList").getString()
        xcConfigurationListObject = self.m_objects.getValue(buildConfigurationListUUID)
        self.m_xcConfigurationList = XCConfigurationList()
        self.m_xcConfigurationList.init(xcConfigurationListObject, self.m_objects, self)
        return self.m_xcConfigurationList

    def getTarget(self, nativeTargetName):
        self.getTargets()
        if self.m_targetsList is None:
            return None
        if " " in nativeTargetName:
            nativeTargetName = "\"" + nativeTargetName + "\""
        for pbxNativeTarget in self.m_targetsList:
            name = pbxNativeTarget.getName()
            if name ==  nativeTargetName:
                return pbxNativeTarget
        return None