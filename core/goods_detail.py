# -*- coding: utf-8 -*-
# @Time    : 2021/7/7 18:26
# @Author  : Haijun

import re
import threading

import redis
import json

from parsel import Selector
from lib.base_fun import logger, request_get, headers, proxy
from dynaconf import settings


class CrawlerGoodsDetail(object):
    def __init__(self):
        self.redis_conn = redis.StrictRedis(host=settings.REDIS.HOST, port=settings.REDIS.PORT, db=settings.REDIS.DB,
                                            password=settings.REDIS.PASSWD)
        self.data_dict = dict()

    def get_goods_url(self):
        data = self.redis_conn.spop('amazon_goods_list')
        if data:
            data_dict = json.loads(data)
            return data_dict
        return None

    def crawl_detail(self):
        headers = {
            "Host": "www.amazon.com",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "cookie": 'session-id=132-9001681-2923327; sp-cdn="L5Z9:CN"; ubid-main=130-8020860-9388951; ld=AZUSSOA-sell; s_pers=%20s_fid%3D0CEC3543AD2E8239-30843AE20A6D66F7%7C1783221604392%3B%20s_dl%3D1%7C1625457004395%3B%20gpv_page%3DUS%253AAZ%253ASOA-overview-sell%7C1625457004403%3B%20s_ev15%3D%255B%255B%2527AZUSSOA-sell%2527%252C%25271625455204407%2527%255D%255D%7C1783221604407%3B; lc-main=en_US; session-id-eu=261-4206949-0287151; ubid-acbuk=259-3470658-8777431; x-main="aUf@eH04DJrDi??RsK0fw4KJqCvLxWKjyOi1TecQhNYPCGoC7LTK8j6SwhyTQMPf"; at-main=Atza|IwEBILl4q2iuClOzxs1GA3YXbZozqc-8puqLliuUHjRK3XgTHbY8WbPBIlaMvmFjYJfoPvLJ4YlPsQ5D7GY_fDkHciF3dWqZuHeFCaJrTS6XgeZCylFYtcZ0X95ZvGjHYEAgl4OYid3LmiC4GlpkSdmaPctuFdl6HNKyhvwtl1e9_M3dEif68IrdSdOYl2kh90oN_232I6L0t6jrKpww5hdvtutu; sess-at-main="lPtHsuxB9YB3ruyCWzTaZh01tF+/SlF1GndJWKDMg+s="; sst-main=Sst1|PQElIUNJAZjtOn9l8HHmRVH0CRPXydVkTBr_v-4dRYvMc64CtYynVHpvW0aHv-yGVrWWBLbStriubnBKkr3nn0eT1ToBDoIm6kerYtunrxHBthcIde-KoeuAy2UIfLrWSrYnWFAdVZfjjTDJk33KyI9Gg4-Ozkd4991iIanY7E_WPRhpjpNbkDiiHBKslT_GYkvRtQj4kRTUlmpgulLf4-xgvrMWXdRmNwLCT4CNwy3IEbVJ2X3PILKNP7QQdHc5xZpASNw1yEh_PJorjpUcLKySIAJdkFPlgOyr4QKSM44SdpQ; session-id-time=2082787201l; i18n-prefs=USD; session-token="2xzf26lzUVYZU+JA4d6hhjC+CjgDjOSK0IUGf4/d+vocOwZqOA2T3LAXvW6Gw1U96IiA0gqF8oZgbRua0PIdO7LY+N+GYNjsHiE4V5ZeQi36lDZ4X1NZXxuOPXUOXEGja8CobVRdqjsH/CLI6iuea1d/pbksC3gYaqQWCuzvYMqKdyLNa3vItDSzkWXCmBcuc/HlGxhG/K94A9fMr/hciQ=="; csm-hit=tb:YERFEMKYHXKCE3BZAYAA+s-TNZM7VA8HMNX320EMX0Z|1625730648100&t:1625730648100&adb:adblk_yes'
        }
        self.data_dict = self.get_goods_url()
        if self.data_dict:
            url = self.data_dict.get('goods_url', None)
            if 'https:' not in url:
                url = f'https://www.amazon.com{url}'
                self.data_dict['goods_url'] = url
            status, response = request_get(url=url, headers=headers, proxy=proxy())
            logger.info(status)
            if status == 200:
                html = Selector(response)
                self.parse_detail(html)
            else:
                logger.error(f'失败=status====={status}====={self.data_dict}')
                self.redis_conn.sadd('amazon_goods_list', json.dumps(self.data_dict))

    def parse_detail(self, html):
        _rank_list = html.xpath('//a[contains(text(),"See Top 100")]/parent::*/text()').extract()
        _rank_str = ';'.join(_rank_list) if _rank_list else None
        _sub_rank = re.search(r'#(.*?) in', _rank_str).group(1) if _rank_str else None
        sub_rank = _sub_rank.replace(",", '') if _sub_rank else None
        if sub_rank:
            self.data_dict['rank'] = sub_rank
            self.redis_conn.lpush('amazon_goods_detail', json.dumps(self.data_dict))
            logger.info(f'采集详情成功======{self.data_dict}')
        else:
            logger.error(f'排名为空==={self.data_dict}')
            self.redis_conn.sadd('amazon_goods_list', json.dumps(self.data_dict))

    def start_crawl_detail(self):

        while True:
            t_thread = []
            for i in range(5):
                t = threading.Thread(target=self.crawl_detail, args=())
                t_thread.append(t)
                t.start()
            for k in t_thread:
                k.join()
