# coding:utf-8

class List:

    def __init__(self):
        self.m_count = 0
        self.m_list = []

    def pushBack(self, ele):
        self.m_count += 1
        self.m_list.append(ele)

    def isEmpty(self):
        return 0 == self.m_count

    def count(self):
        return self.m_count

    def at(self, index):
        return self.m_list[index]
