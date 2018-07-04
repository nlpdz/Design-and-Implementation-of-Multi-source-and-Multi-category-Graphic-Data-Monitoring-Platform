# -*- coding: utf-8 -*-

'''
    抓取微博热搜关键词，并找相应的微博，
    目前还未写数据库


'''
from httptools import *
from pyquery import PyQuery as pq
import json
import re
from config import *


def get_hotkeys():
    url = 'https://s.weibo.com/top/summary?cate=realtimehot'
    data = use_proxy(url, proxy_addr())
    doc = pq(data)
    lists = doc('script')
    hotkeys = []
    for li in lists:
        try:
            if li.text.find('STK.pageletM.view') > 0 and li.text.find('unLogin') > 0:
                first = li.text.find('(')
                jsondata = li.text[first + 1:-1]
                # print(jsondata)
                html = json.loads(jsondata).get('html')
                # print(html)
                d = pq(html)
                section = d('a[target="_blank"]')

                hotkeys.append(section.text())
        except:
            pass

    return hotkeys


# 根据关键字搜索微博，返回微博的正文
def get_hotweibo(key, page):
    url = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type=1&&q=' + \
        key + '&page=' + str(page)
    url = urllib.parse.quote(url, safe='/:?=')
    print(url)
    data = use_proxy(url, proxy_addr())
    content = json.loads(data).get("data")
    cards = content.get("cards")
    # print(data)
    hotweibo = []
    if cards != []:
        flag = True
        for i in range(len(cards)):
            print(i)
            if flag and page == 1:
                try:
                    flag = False
                    mblog = cards[i].get('mblog')
                    text = mblog.get('text')
                    username = mblog.get('user').get('screen_name')
                    print('user:')
                    print(username)
                    hotweibo.append(text)
                except Exception as e:
                    print(e)
            else:
                for group0 in cards[i].get('card_group'):
                    try:
                        mblog = group0.get('mblog')
                        text = mblog.get('text')
                        username = mblog.get('user').get('screen_name')
                        print('user:')
                        print(username)

                        hotweibo.append(text)
                    except Exception as e:
                        print(e)
    for i in range(len(hotweibo)):
        dr = re.compile(r'<[^>]+>', re.S)
        hotweibo[i] = dr.sub('', hotweibo[i])

    return hotweibo


def save_hotblog(key, hotbloglist):
    if not os.path.exists(os.path.join('hot_blogs', key)):
        os.makedirs(os.path.join('hot_blogs', key))
    with open(os.path.join('hot_blogs', key, 'bloginfo.txt'), 'a', encoding='utf-8') as f:
        for i in hotbloglist:
            f.write(i + '\n')

if __name__ == "__main__":
    hotkeys = get_hotkeys()
    keys = hotkeys[0].split(' ')
    for i in keys:
        if i is not '':
            print(i + '\n')
            for j in range(30):
                print("page: " + str(j + 1))
                hot = get_hotweibo(i, j + 1)
                save_hotblog(i, hot)
                for h in hot:
                    print(h)
                    print('\n')
                print('\n')
