# coding: utf
'''
# prerequisite:
#   based on Python 2.7

# usage:

# process:


# know issues:

# Other
    Any issues or improvements please contact xxx@126.com
'''
import time

class CommentsParser(object):
    """
    lua的注释解析器
    """

    def __init__(self):
        self.is_line = True
        
    def parse(self, lua_txt, index, lua_txt_len)
        is_comments_begin = False
        cross_bar_begin = False
        cross_bar_count = 0
        loop = 0
        while True:
            ch = lua_txt[index]
            if is_comments_begin:

            else:
                if ch == '-':
                    nextCh = lua_txt[index+1]
                    if nextCh == '-':
                        is_comments_begin = True
                        loop += 2 # 跳到--下一个
                else:
                    break



class LuaGrammarParser(object):
    """
    lua语法分析器，主要用于符合博艺lua class规范的语法
    """

    def __init__(self):
        self.p = 0

    def parse(self, full_path):
        begin = time.time()
        for i in range(0, 200):
            target_file = open(full_path)
            all_txt = target_file.read()
            for index in range(len(all_txt)):
                test = all_txt[index]
            # pos = all_txt.find('unity.exports')
        end = time.time()
        print end - begin


def main():
    """
    main
    """
    auto_req = LuaGrammarParser()
    auto_req.parse("F:\\projects\\npc1\\code\\client\\trunk\\Assets\\Game\\Lua\\Game\\Controller\\Battle\\BattleViewTopPanelBehaviour.lua")

if __name__ == "__main__":
    main()
