# encoding=utf-8

''' 
    项目配置文件
    数据库配置
    代理ip配置（简单配置，以后考虑从网站上爬代理ip 使其自动获取）
    header 配置（暂未使用）

'''
import urllib.request
import socket
import random
socket.setdefaulttimeout(3)


# 数据库信息
dbuser = 'root'
dbpwd = '123456'


# 代理池
proxy_addrs = ['122.114.31.177:808', '113.121.242.26:80', '115.217.255.143:34132',
               '61.135.217.7:80',   '111.155.116.236:8123', '125.115.183.87:808',
               '183.23.74.55:61234', '111.155.116.249:8123', '49.71.81.195:808',
               '115.208.120.92:808', '101.68.73.54:53281', '42.96.168.79:8888',
               '116.55.77.81:61202', '111.155.116.216:8123', '120.92.88.202:10000',
               '111.155.124.77:8123', '125.118.247.125:6666', '110.73.55.98:8123',
               '59.32.37.178:3128', '49.71.81.195:808', '125.118.147.94:808',
               '113.143.134.111:61202', '125.121.115.225:808', '180.118.242.142:808',
               '112.248.24.130:61234', '180.122.145.51:27906', '113.121.242.77:808',
               '58.216.202.149:8118', '14.118.253.135:6666', '175.155.24.43:808',
               '113.121.242.54:808', '222.89.81.224:808', '111.155.116.207:8123',
               '27.40.137.213:61234', '113.128.30.36:45865']


# 随机取代理ip
def proxy_addr():
    proxy_len = len(proxy_addrs)
    ran = random.randint(0, proxy_len - 1)
    return proxy_addrs[ran]


# header
headers = [
    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Mobile Safari/537.36']


# 测试代理ip
def test_proxy():
    httpsurl = 'https://www.baidu.com'
    httpurl = 'http://www.baidu.com'

    for proxyaddr in proxy_addrs:
        req = urllib.request.Request(httpsurl)
        req.add_header(
            "User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0")
        proxy = urllib.request.ProxyHandler({'http': proxyaddr})
        opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
        urllib.request.install_opener(opener)
        try:
            data = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
            if '百度一下' in data:
                print(proxyaddr + ': \thttps success')
            else:
                print(proxyaddr + ': \thttps failed')
        except Exception as e:
            print(e)
            print(proxyaddr + ': \thttps failed')


if __name__ == '__main__':
    test_proxy()
