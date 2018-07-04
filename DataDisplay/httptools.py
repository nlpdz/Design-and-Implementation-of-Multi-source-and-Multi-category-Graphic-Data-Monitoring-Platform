# -*- coding: utf-8 -*-

import urllib.request
import json
import pymysql
import re
import uuid
import datetime
import os
import time


# 定义页面打开函数
def use_proxy(url, proxy_addr):
    # print(urllib.parse.quote(url, safe='/:?='))
    # req = urllib.request.Request(urllib.parse.quote(url, safe='/:?='))
    req = urllib.request.Request(url)
    req.add_header(
        "User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0")
    proxy = urllib.request.ProxyHandler({'http': proxy_addr})
    opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    data = None
    try:
        data = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
    except UnicodeEncodeError as e:
        print(e)
        raise e
    except urllib.error.HTTPError as e1:
        print('url:\t' + url)
        print('proxy_ip:\t' + proxy_addr)
        print(e1)
        if '403' in str(e1) or '418' in str(e1):
            flag = False
            for i in range(3):
                try:
                    print('use_proxy sleep 1 min')
                    time.sleep(60)
                    data = urllib.request.urlopen(
                        req).read().decode('utf-8', 'ignore')
                    flag = True
                    break
                except urllib.error.HTTPError:
                    pass
            if flag == False:
                raise e1
    return data


# 下载数据
def use_proxy_download(url, proxy_addr):
    req = urllib.request.Request(url)
    req.add_header(
        "User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0")
    proxy = urllib.request.ProxyHandler({'http': proxy_addr()})
    opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    data = urllib.request.urlopen(req).read()
    return data


if __name__ == "__main__":
    pass
