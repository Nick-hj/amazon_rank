# -*- coding: utf-8 -*-
# @Time    : 2020/8/24 14:37
# @Author  : Haijun

# from bin import crawler
from core.children_category import ChildrenCategory
from conf.settings import load_or_create_settings
load_or_create_settings()
if __name__ == '__main__':
    ch = ChildrenCategory()
    ch.crawler()
