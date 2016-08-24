# coding:utf-8

import subprocess
import sys

"""
用于处理和调用外部命令有关的进程处理类
"""


class Process:

    # 静态函数，传入命令
    @classmethod
    def execute(cls, command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            out = process.stdout.readline()
            err = process.stderr
            if err is not None:
                errOut = err.readline()
                sys.stdout.write(errOut)
                sys.stdout.flush()

            if out == "" and process.poll() is not None:
                break
            if out != "":
                sys.stdout.write(out)
                sys.stdout.flush()


        return


