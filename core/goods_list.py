# -*- coding: utf-8 -*-
# @Time    : 2021/7/5 15:37
# @Author  : Haijun
import re
import threading

import redis
import json
from parsel import Selector
from lib.base_fun import logger, headers, request_get, proxy
from dynaconf import settings


class CrawlerGoodsList(object):

    def __init__(self):
        self.redis_conn = redis.StrictRedis(host=settings.REDIS.HOST, port=settings.REDIS.PORT, db=settings.REDIS.DB,
                                            password=settings.REDIS.PASSWD)

    def _goods_list(self, data):
        _url = data.get('url', None)
        https_url = re.search(r'(https.*/\d+/)', _url).group(1)
        url_list = [f'{https_url}ref=zg_bs_pg_1?_encoding=UTF8&pg=1', f'{https_url}ref=zg_bs_pg_2?_encoding=UTF8&pg=2']
        for url in url_list:
            status, response = request_get(url=url, headers=headers(), proxy=proxy())
            if status == 200:
                html = Selector(response)
                goods_urls = html.xpath(
                    '//li[@class="zg-item-immersion"]//span[@class="aok-inline-block zg-item"]/a/@href').extract()
                for goods_url in goods_urls:
                    _asin = re.search(r'dp/(.*?)/', goods_url)
                    asin = _asin.group(1) if _asin else None
                    if asin:
                        goods_data = {
                            'asin': asin,
                            'goods_url': goods_url,
                            'categoryFullPath': data['categoryFullPath'],
                            'leafCategory': data['leafCategory']
                        }
                        data_json = json.dumps(goods_data, ensure_ascii=False)
                        self.redis_conn.sadd('amazon_goods_list', data_json)
                logger.info(f'采集列表成功======{url}')
            else:
                self.redis_conn.lpush('amazon_category_url_bak', json.dumps(data))
                logger.info(f'采集列表失败====={url}')

    def action_redis(self):
        '''
        类目是固定的，把类目备份一份，操作备份类目
        :return:
        '''

        # 删除redis类目
        self.redis_conn.delete('amazon_category_url_bak')
        # 取出redis所有类目，备份存储redis
        category_urls = self.redis_conn.smembers('amazon_category_url')
        for c_url in category_urls:
            self.redis_conn.lpush('amazon_category_url_bak', c_url)

    def start_crawl_list(self):
        self.action_redis()
        while True:
            t_thread = []
            for i in range(3):
                data = self.redis_conn.lpop('amazon_category_url_bak')
                if data:
                    data_dict = json.loads(data)
                    t = threading.Thread(target=self._goods_list, args=(data_dict,))
                    t_thread.append(t)
                    t.start()
                else:
                    break
            if len(t_thread) > 0:
                for k in t_thread:
                    k.join()
            else:
                break
