import requests
import time
import logging
from os import path, environ as env
from dotenv import load_dotenv
from src.ua import get_a_random_ua
from src.proxy_pool import get_proxy, delete_proxy, get_count

log = logging.getLogger(__name__)

load_dotenv()
w_proxy = False if env.get("WITHOUT_PROXY") == "yes" else True

rejected_proxies = {}
MAX_REJECTED = 5


def req(url):
    if w_proxy == True:
        assert get_count() > 0, "proxy pool is empty, cannot make proxied requests for now"
        return _make_req_with_proxy(url)
    else:
        return _make_req(url)


def batch_req(urls = []):
    for url in urls:
        yield req(url)


def _make_req(url):
    retry_count = 5
    source = None

    while retry_count > 0:
        time.sleep(0.1)
        try:
            resp = requests.get(url, headers={'User-Agent': get_a_random_ua()}, timeout=10)
            source = resp.text
            break
        except requests.exceptions.RequestException as err:
            retry_count -= 1

    return source, url


def _make_req_with_proxy(url):
    retry_count = 5
    proxy = next_proxy()
    source = None

    assert proxy != None, f"proxy is none while fetching {url}"

    while retry_count > 0 and proxy != None:
        time.sleep(0.1)
        try:
            log.debug(f"using proxy {proxy}")
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            resp = requests.get(url, headers={'User-Agent': get_a_random_ua()}, proxies=proxies, timeout=10)
            source = resp.text
            break
        except requests.exceptions.RequestException as err:
            retry_count -= 1
    if retry_count == 0:
        reject_proxy(proxy)

    return source, url


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
