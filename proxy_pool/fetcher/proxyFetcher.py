"""
This file works under the proxy_pool project. Refer to https://github.com/jhao104/proxy_pool/blob/master/README.md#%E6%89%A9%E5%B1%95%E4%BB%A3%E7%90%86 to learn more.
"""
import re
from time import sleep
from os import environ as env
from util.webRequest import WebRequest
import logging

log = logging.getLogger(__name__)

class ProxyFetcher(object):
    @staticmethod
    def zhimaProxy():
        log.info("zhimaProxy fetching proxies...")
        url = env.get("ZHIMA_PROXY_URL", None)
        if url == None:
            log.error("ZHIMA_PROXY_URL must be a valid URL in order to call zhimaProxy")
            return
        resp = WebRequest().get(url)
        proxies = resp.split('\n')
        for proxy in proxies:
            yield proxy

