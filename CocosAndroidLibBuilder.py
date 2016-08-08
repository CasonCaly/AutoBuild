# coding: UTF-8

import subprocess
import sys

class CocosAndroidLibBuilder:

    def __init__(self, projectPath, isDebugModel):
        self.m_projectPath = projectPath
        self.m_isDebugModel = isDebugModel

    def build(self):

        buildCommand = "%NDK_ROOT%/ndk-build -C " + self.m_projectPath + " -j8"
        process = subprocess.Popen(buildCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            out = process.stdout.readline()
            if out == "" and process.poll() != None:
                break
            if out != "":
                sys.stdout.write(out)
                sys.stdout.flush()
        return

build = CocosAndroidLibBuilder("F:/common/client/frameworks/prebuilt/build/android/debug", False)
build.build()