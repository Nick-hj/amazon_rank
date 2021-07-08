# -*- coding: utf-8 -*-
# @Time    : 2021/7/7 18:10
# @Author  : Haijun

from core.children_category import ChildrenCategory
from conf.settings import load_or_create_settings
load_or_create_settings()
if __name__ == '__main__':
    ch = ChildrenCategory()
    ch.crawler()
