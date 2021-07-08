# -*- coding: utf-8 -*-
# @Time    : 2021/7/8 17:22
# @Author  : Haijun
import asyncio
import aiohttp
import aioredis

from dynaconf import settings

from lib.base_fun import logger

loop = asyncio.get_event_loop()


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
        # "https": proxyMeta
    }
    return proxies['http']


async def request_get(url, headers=None, proxy=None):
    async with aiohttp.TCPConnector(limit=10, verify_ssl=False) as tc:
        async with aiohttp.ClientSession(connector=tc) as session:
            logger.info(url)
            async with session.get(url=url, headers=headers, timeout=15) as rep:
                status = rep.status
                rep_text = await rep.text()
                return status, rep_text


async def redis_pool():
    _redis = await aioredis.create_pool(
        address=(settings.REDIS.HOST, 6379), db=4, password=None, minsize=5, maxsize=10, loop=loop
    )
    return _redis
