# -*- coding: utf-8 -*-
# @Time    : 2021/7/4 18:37
# @Author  : Haijun
import json
import re
import http.client
import time

import redis
import requests

from parsel import Selector
from lib.base_fun import logger, proxy, request_get, headers
from dynaconf import settings

http.client._is_legal_header_name = re.compile(rb'[^\s][^:\r\n]*').fullmatch


class ChildrenCategory(object):
    def __init__(self):
        self.start_url = [
            # 'https://www.amazon.com/Best-Sellers-Office-Products-Bookcases/zgbs/office-products/10824421/ref=zg_bs_nav_op_3_1069108',
            'https://www.amazon.com/Best-Sellers-Arts-Crafts-Sewing/zgbs/arts-crafts/ref=zg_bs_nav_0',
            'https://www.amazon.com/Best-Sellers-Baby/zgbs/baby-products/ref=zg_bs_nav_0',
            'https://www.amazon.com/Best-Sellers-Beauty/zgbs/beauty/ref=zg_bs_nav_0',
            'https://www.amazon.com/Best-Sellers/zgbs/fashion/ref=zg_bs_nav_0',
            'https://www.amazon.com/Best-Sellers-Grocery-Gourmet-Food/zgbs/grocery/ref=zg_bs_nav_0',
            'https://www.amazon.com/Best-Sellers-Handmade/zgbs/handmade/ref=zg_bs_nav_0',
            'https://www.amazon.com/Best-Sellers-Health-Personal-Care/zgbs/hpc/ref=zg_bs_nav_0',
            'https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden/ref=zg_bs_nav_0',
            'https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/ref=zg_bs_nav_0',
            'https://www.amazon.com/Best-Sellers-Musical-Instruments/zgbs/musical-instruments/ref=zg_bs_nav_0',
            'https://www.amazon.com/Best-Sellers-Office-Products/zgbs/office-products/ref=zg_bs_nav_0',
            'https://www.amazon.com/Best-Sellers-Garden-Outdoor/zgbs/lawn-garden/ref=zg_bs_nav_0',
            'https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods/ref=zg_bs_nav_0',
            'https://www.amazon.com/Best-Sellers-Home-Improvement/zgbs/hi/ref=zg_bs_nav_0'
        ]

        self.redis_conn = redis.StrictRedis(host=settings.REDIS.HOST, port=settings.REDIS.PORT, db=settings.REDIS.DB,
                                            password=settings.REDIS.PASSWD)

    def crawler(self):
        for url in self.start_url:
            # logger.info(url)
            try:
                self.parser_page(url)
            except Exception as e:
                pass

    def requests_page(self, url):
        status, response = request_get(url=url, headers=headers(), proxy=proxy())
        if status == 200:
            return Selector(response)
        return None

    def parser_page(self, url, category_full_path='', retry_times=0):
        '''

        :param url:
        :param category_full_path:
        :param retry_times: 重试次数
        :return:
        '''
        html = self.requests_page(url)
        if html:
            try:
                cur_cate = html.xpath('//span[@class="zg_selected"]')
                # 当前元素`span[@class="zg_selected"]`的父元素li是否有兄弟元素ul,
                # 如果有，说明当前类目不是叶子类目，否则当前类目为叶子类目
                cate_ul = cur_cate.xpath('./parent::li/following-sibling::ul')
                if cate_ul:
                    urls = cate_ul.xpath('./li/a/@href').extract()
                    _category = cur_cate.xpath('./text()').get()
                    if category_full_path:
                        category_full_path = category_full_path + '>' + _category
                    else:
                        category_full_path = _category
                    for url in urls:
                        self.parser_page(url, category_full_path)
                else:
                    leaf_category = cur_cate.xpath('./text()').get()
                    category_full_path = category_full_path + '>' + leaf_category
                    url_data = {
                        'url': url,
                        'categoryFullPath': category_full_path,
                        'leafCategory': leaf_category
                    }
                    url_json = json.dumps(url_data, ensure_ascii=False)
                    self.redis_conn.sadd('amazon_category_url', url_json)
                    logger.info(url_json)
                    time.sleep(1)
            except Exception as e:
                if retry_times <= 5:
                    retry_times += 1
                    logger.error(f'获取类目失败,重试第{retry_times}次==url=={url}={e}')
                    self.parser_page(url, category_full_path, retry_times)
        else:
            if retry_times <= 5:
                retry_times += 1
                logger.error(f'获取类目失败,请求失败,重试第{retry_times}次==url=={url}')
                self.parser_page(url, category_full_path, retry_times)
