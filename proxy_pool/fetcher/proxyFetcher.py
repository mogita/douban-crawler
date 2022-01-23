"""
Douban Crawler is a dead siple crawler for data scraping
Copyright (C) 2022 mogita <me@mogita.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
"""
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
        proxies = resp.text.split('\n')
        for proxy in proxies:
            yield proxy

