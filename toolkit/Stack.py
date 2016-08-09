# coding:utf-8


class Stack:

    def __init__(self):
        self.m_count = 0
        self.m_list = []

    def push(self, value):
        self.m_count += 1
        self.m_list.append(value)

    def pop(self):
        if 0 == self.m_count:
            return None
        self.m_count -= 1
        return self.m_list.pop()

    def top(self):
        if 0 == self.m_count:
            return None
        return self.m_list[self.m_count]

    def isEmpty(self):
        return 0 != self.m_count
