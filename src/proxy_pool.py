"""
Douban Crawler is a dead siple crawler for data scraping
Copyright (C) 2022 mogita <me@mogita.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
"""
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
            return resp_json["count"]["total"] if "count" in resp_json else 0
        except:
            return 0
