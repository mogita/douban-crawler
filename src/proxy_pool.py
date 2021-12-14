from os import environ as env
import requests

host = env.get("PROXY_POOL_HOST", "http://douban-crawler-proxy-pool")

def get_proxy():
    return requests.get(f"{host}:5010/get/").json()

def delete_proxy(proxy):
    requests.get(f"{host}:5010/delete/?proxy={proxy}")


