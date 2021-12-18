import requests
import time
import numpy as np
import logging
from src.ua import get_a_random_ua
from src.proxy_pool import get_proxy, delete_proxy

log = logging.getLogger(__name__)

rejected_proxies = {}
MAX_REJECTED = 5

def req(url):
    retry_count = 5
    proxy = next_proxy()
    source = None

    if proxy == None:
        log.error(f"proxy is none while fetching {url}")

    while retry_count > 0 and proxy != None:
        time.sleep(np.random.rand()*5)
        try:
            proxies = {"http": f"http://{proxy}"}
            resp = requests.get(url, headers={'User-Agent': get_a_random_ua()}, proxies=proxies)
            source = resp.text
            break
        except requests.exceptions.RequestException as err:
            retry_count -= 1
    if retry_count == 0:
        reject_proxy(proxy)

    return source, url


def batch_req(urls = []):
    for url in urls:
        yield req(url)

def next_proxy():
    retry_count = 10
    while retry_count > 0:
        proxy = get_proxy().get("proxy")
        if proxy not in rejected_proxies or rejected_proxies[proxy] < MAX_REJECTED:
            return proxy
        else:
            retry_count -= 1
    return None

def reject_proxy(proxy):
    if proxy not in rejected_proxies:
        rejected_proxies[proxy] = 1
    else:
        rejected_proxies[proxy] += 1

    if rejected_proxies[proxy] >= MAX_REJECTED:
        delete_proxy(proxy)

    with open("rejected_proxies.txt", "w") as file:
        file.write(repr(rejected_proxies))
        file.close()
