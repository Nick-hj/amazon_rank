# -*- coding: utf-8 -*-
# @Time    : 2021/7/8 16:41
# @Author  : Haijun

import asyncio
from lib.base_fun import logger
from apscheduler.schedulers.blocking import BlockingScheduler
from core.goods_list import CrawlerGoodsList

scheduler = BlockingScheduler()
g = CrawlerGoodsList()
g.start_crawl_list()
# loop = asyncio.get_event_loop()
# task = asyncio.ensure_future(g.run_goods_list())
# loop.run_until_complete(task)

if __name__ == '__main__':
    # 手动触发
    # crawl_etsy_start_url()
    # 每隔一天运行一次 循环任务
    # scheduler.add_job(func=crawl_etsy_shop, trigger='interval', days=1)
    # 每天18点 定时任务
    g = CrawlerGoodsList()
    scheduler.add_job(func=g.start_crawl_list, trigger='cron', hour=1)
    try:
        scheduler.start()
    except SystemExit:
        exit()