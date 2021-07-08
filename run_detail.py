# -*- coding: utf-8 -*-
# @Time    : 2021/7/7 18:40
# @Author  : Haijun
import time
from core.goods_detail import CrawlerGoodsDetail


if __name__ == '__main__':
    d = CrawlerGoodsDetail()
    d.start_crawl_detail()
    time.sleep(1)
