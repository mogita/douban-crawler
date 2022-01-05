from os import environ as env
import requests

host = env.get("PROXY_POOL_HOST", "http://douban-crawler-proxy-pool:5010")

def get_proxy():
    return requests.get(f"{host}/get/").json()

def delete_proxy(proxy):
    requests.get(f"{host}/delete/?proxy={proxy}")

def get_count():
    resp = requests.get(f"{host}/count/")
    if resp == None:
        return 0
    else:
        try:
            resp_json = resp.json()
            return resp["count"]["total"] if "count" in resp else 0
        except:
            return 0
