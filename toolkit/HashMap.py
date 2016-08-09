# coding:utf-8

class HashMap:
    __dict = None

    def __init__(self):
        self.__dict = {}

    def insert(self, key, value):
        hasKey = self.__dict.has_key(key)
        if hasKey:
            return False
        else:
            self.__dict[key] = value
            return True

    def forceInsert(self, key, value):
        self.__dict[key] = value

    def find(self, key):
        hasKey = self.__dict.has_key(key)
        if not hasKey:
            return None
        else:
            return self.__dict[key]

