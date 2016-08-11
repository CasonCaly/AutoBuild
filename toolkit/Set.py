# coding:utf-8

class Set:

    def __init__(self):
        self.m_dict = {}

    def insert(self, value):
        hasKey = self.m_dict.has_key(value)
        if hasKey:
            return False
        else:
            self.m_dict[value] = value
            return True

    def find(self, value):
        hasKey = self.m_dict.has_key(value)
        if not hasKey:
            return None
        else:
            return self.m_dict[value]

    def erase(self, value):
        hasKey = self.m_dict.has_key(value)
        if hasKey:
            del self.m_dict[value]

