# -*- coding: utf-8 -*-
# @Time    : 2020/8/24 14:39
# @Author  : Haijun
import os
import requests
import random
import re
import http.client
from contextlib import closing

from loguru import logger as base_logger
from dynaconf import settings

http.client._is_legal_header_name = re.compile(rb'[^\s][^:\r\n]*').fullmatch
def init_logger():
    '''
    日志
    '''
    base_logger.add(os.path.join('./logs', 'spider_info_{time:YYYY-MM-DD}.log'),
                    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {file.path} | {module} | {function} | {line} | {message}",
                    level="INFO", rotation="00:00", retention='6 days', enqueue=True, encoding='utf-8')
    base_logger.add(os.path.join('./logs', 'spider_error_{time:YYYY-MM-DD}.log'),
                    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {file.path} | {module} | {function} | {line} | {message}",
                    level="ERROR", rotation="00:00", retention='6 days', enqueue=True, encoding='utf-8')
    return base_logger


logger = init_logger()


# 代理
def proxy():
    # 代理服务器
    proxyHost = "http-dyn.abuyun.com"
    proxyPort = "9020"

    # 代理隧道验证信息
    proxyUser = settings.PROXY_USER
    proxyPass = settings.PROXY_PWD
    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }
    proxies = {
        "http": proxyMeta,
        "https": proxyMeta
    }
    return proxies


def request_get(url, headers=None, proxy=None):
    '''
    get 请求
    '''
    try:
        with closing(requests.get(url=url, headers=headers, proxies=proxy, timeout=5)) as response:
            status = response.status_code
            return status, response.text
    except requests.exceptions.ProxyError as e:
        with closing(requests.get(url=url, headers=headers, timeout=5)) as response:
            status = response.status_code
            return status, response.text
    except requests.exceptions.ReadTimeout as e:
        logger.error(f'请求超时===={url}====={e}')
        return 400, None
    except Exception as e:
        logger.error(f'请求失败===={url}====={e}')
        return 400, None


def headers(path=None):
    '''
    请求头
    '''
    headers = {
        'Host': 'www.amazon.com',
        # ':method': 'GET',
        # ':path': 'Best-Sellers-Arts-Crafts-Sewing/zgbs/arts-crafts/ref=zg_bs_nav_0',
        # ':scheme': 'https',
        # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        # 'accept-encoding': 'gzip, deflate, br',
        # 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        # 'cache-control': 'max-age=0',
        'cookie': random.choice(settings.AE_COOKIE),
        # 'downlink': '1.7',
        # 'ect': '4g',
        # 'referer': 'https://www.amazon.com/',
        # 'rtt': '200',
        # 'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-fetch-dest': 'document',
        # 'sec-fetch-mode': 'navigate',
        # 'sec-fetch-site': 'same-origin',
        # 'sec-fetch-user': '?1',
        # 'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36'
    }
    return headers
