# coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse
from .models import User, UserHeader, zhihu_anwsers, headline_title_and_url, headline_images, wangyi_news, \
    wangyi_news_images, Sina_news, Sina_weibo, Sina_weibo_content, taobao_goods, baidu_picture, xinlixue, yinyue, dianyan, meishi, youxi

from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

from hashlib import md5  # 防止相同文件名被覆盖
from urllib.parse import urlencode  # 解析中文
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from json.decoder import JSONDecodeError

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pyquery import PyQuery as pq

from .httptools import *
from .config import *
import threadpool

import itertools
import urllib
import requests
import os
import re
import sys
import csv
import jieba
from wordcloud import WordCloud
import jieba
import time
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from os import path
import socket
socket.setdefaulttimeout(10)

# 主界面框架控制器
def index(request):
    if request.method == "POST":
        return render(request, 'index.html')
    else:
        return render(request, 'login.html')


# 主界面顶部控制器
def topFrame(request):
    return render(request, 'topFrame.html')


# 主界面顶部第二栏控制器
def colFrame(request):
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return render(request, 'colFrame.html', {"date": date})


# 主界面左侧展开收起控制器
def pushRLFrame(request):
    return render(request, 'pushRLFrame.html')


# 主界面默认内容控制器
def PageFrame(request):
    return render(request, 'PageFrame.html')


# 主界面左侧菜单控制器
def MenuFrame(request):
    return render(request, 'MenuFrame.html')


person = {}
this_user = ''


# 登陆界面
def login(request):
    if request.method == 'POST':
        # 接收登陆界面表单数据
        username = request.POST['username']
        password = request.POST['password']
        # 根据数据从数据库查找用户
        userArr = User.objects.filter(username=username)
        if userArr:
            # 用户名是正确的，进一步比较密码是否正确
            # 从userArr列表中取出一个元素
            user = userArr[0]
            if user.password == password:
                # 说明密码正确，说明登陆成功，就可以安装登陆成功以后的模板
                global person

                # 将当前查询到的对象转成字典
                global this_user
                this_user = user.username
                userDict = {'id': user.id, 'username': user.username,
                            'shopintroduct': user.shopintroduct}

                # 查询数据库中商家图像地址
                header = UserHeader.objects.filter(id_id=user.id)

                if len(header):
                    headerimg = header[0]
                    userDict['headerurl'] = headerimg.url.url

                # 构建一个模板上下文

                context = {}
                context['userinfo'] = userDict
                person = context

                return render(request, 'index.html')

            else:
                # 说明密码不准确直接给前端响应密码错误
                return HttpResponse('密码不正确！')
        else:
            # 声明用户名不准确，该用户不存在，直接给前端响应用户名不存在
            return HttpResponse('用户名不存在！')
            pass

    # 安装模板
    return render(request, "login.html")
    pass


# 用户界面
def user(request):
    global person
    global this_user
    userArr = User.objects.filter(username=this_user)
    try:
        user = userArr[0]
    except:
        userArr = User.objects.filter(username='hiddenRose')
        user = userArr[0]
    user_id = user.id
    user_name = user.username
    user_shopintroduct = user.shopintroduct
    # 查询数据库中商家图像地址
    header = UserHeader.objects.filter(id_id=user.id)
    if len(header):
        headerimg = header[0]
        user_headerimg = headerimg.url.url
    else:
        user_headerimg = ''

    return render(request, 'user.html',
                  {"user_id": user_id, "user_name": user_name, "user_shopintroduct": user_shopintroduct,
                   'user_headerimg': user_headerimg})


def register(request):
    # 模板中发生提交事件后要在下面代码中处理
    if request.method == 'POST':
        # 一旦发生poss事件，则在这里处理
        # 接收前端提交数据
        username = request.POST['username']
        password = request.POST['password']
        shopintroduct = request.POST['shopintroduct']
        # 处理前端提交数据
        # 建模
        bus = User(username=username, password=password, shopintroduct=shopintroduct)
        # 存入数据库
        bus.save()
        return HttpResponse("<script type='text/javascript'>alert('注册成功！');window.history.back(-2);</script>")

    # 安装模板
    return render(request, "register.html")
    pass


# 修改个人信息
def alter_info(request):
    if request.method == 'POST':
        if request.POST['flag'] == 'index':
            # 这里安装修改个人信息模板
            userid = request.POST['userid']
            # 根据userid查找对象
            userArr = User.objects.filter(id=userid)
            user = userArr[0]

            # 转成字典
            userDict = {'id': user.id, 'username': user.username, 'shopintroduct': user.shopintroduct,
                        'password': user.password}
            context = {'userinfo': userDict}

            return render(request, 'alterinfo.html', context)
        else:
            # 说明不是index页面发出的post请求，可能是模板页，处理模板post请求
            username = request.POST['username']
            shopintroduct = request.POST['shopintroduct']
            id = request.POST['userid']
            userArr = User.objects.filter(id=id)
            user = userArr[0]
            user.username = username
            user.shopintroduct = shopintroduct
            user.save()

            # 先和原来头像断绝关系（删除原来图片）
            res = UserHeader.objects.filter(id_id=id)
            if len(res):
                src = (settings.BASE_DIR + res[0].url.url).replace('\\', '/')
            # os.remove(src)

            # 头像上传
            # 获取提交的头像
            try:
                img = request.FILES['headerimg']
            except:

                img = (res[0].url.url)[6:]
            # img = '\\UserHeader\\default.jpg'
            header = UserHeader(id_id=id, url=img)
            header.save()
            return HttpResponse("修改成功！")
            pass


#################【公用模块】##################
# ajax请求响应
def ajax_response(request):
    username = request.POST['username']
    # 查询前端传过来的用户名是否在数据库中
    res = User.objects.filter(username=username)
    # 将查询的结果作为响应体返回

    return HttpResponse(res)
    pass


#################爬虫功能部分##################

headline_stop_flag = 0
wangyiNews_stop_flag = 0
zhihu_stop_flag = 0
taobao_stop_flag = 0


# 头条
def Headline(request):
    if request.method == 'POST':
        # 一旦发生poss事件，则在这里处理
        # 接收前端提交数据
        headline_images.objects.filter().delete()
        headline_title_and_url.objects.filter().delete()
        global headline_stop_flag
        headline_stop_flag = 0
        keyword = request.POST['keyword']
        for group in range(0, 20):
            print(group)
            headline_spider(group * 20, keyword)
        return render(request, 'Headline.html', {'success': 'success', 'keyword': keyword})
    else:
        return render(request, 'Headline.html')


# 头条更新
def headline_update(request):
    dic = {}
    img_src = ''
    img_note = ''
    img_id = ''
    img_title = ''
    headline_t_and_u = headline_title_and_url.objects.filter().order_by('-id')[0:1]
    for i in headline_t_and_u:
        img_title = i.title
        img_id = i.id

    headline_img = headline_images.objects.filter().order_by('-id')[0:1]
    for i in headline_img:
        img_src = i.images_url
        img_note = i.abstracts

    dic['imgsrc'] = img_src
    dic['imgnote'] = img_note
    dic['imgid'] = img_id
    dic['imgtitle'] = img_title

    dic_json = json.dumps(dic)
    response = HttpResponse(dic_json)
    response['Content-Type'] = "text/javascript"
    return response


# 头条停止
def headline_to_stop(request):
    global headline_stop_flag
    headline_stop_flag = 1
    return render(request, 'Headline.html')



# 网易新闻--------------------------------------
def WangyiNews(request):
    if request.method == 'POST':
        # 一旦发生poss事件，则在这里处理
        # 接收前端提交数据
        wangyi_news.objects.filter().delete()
        wangyi_news_images.objects.filter().delete()
        start = request.POST['sent']
        global wangyiNews_stop_flag
        wangyiNews_stop_flag = 0
        if start == 'start':
            wangyi_spider()
            return render(request, 'WangyiNews.html')
    else:
        return render(request, 'WangyiNews.html')


# 网易新闻刷新函数------------------------------
def aaa(request):


    dic = {}
    img_src = ''
    img_note = ''
    img_id = ''
    img_title = ''
    img_tag = ''
    img_overview = ''
    wangyi_ns = wangyi_news.objects.filter().order_by('-id')[0:1]

    for i in wangyi_ns:
        img_id = i.id
        img_title = i.title
        img_tag = i.tag
        img_overview = i.overview


    wangyi_ns_img = wangyi_news_images.objects.filter().order_by('-id')[0:1]

    for i in wangyi_ns_img:
        img_src = i.imgurl
        img_note = i.note


    dic['imgsrc'] = img_src
    dic['imgnote'] = img_note
    dic['imgid'] = img_id
    dic['imgtitle'] = img_title
    dic['imgtag'] = img_tag
    dic['imgoverview'] = img_overview

    dic_json = json.dumps(dic)
    response = HttpResponse(dic_json)
    response['Content-Type'] = "text/javascript"
    return response


# 网易新闻暂停---------------------------------
def wangyiNews_to_stop(request):
    global wangyiNews_stop_flag
    wangyiNews_stop_flag = 1
    return render(request, 'WangyiNews.html')


# 新浪微博
def SinaWeibo(request):
    if request.method == 'POST':
        # 一旦发生poss事件，则在这里处理
        # 接收前端提交数据
        Sina_weibo.objects.filter().delete()
        Sina_weibo_content.objects.filter().delete()
        searchEvent = request.POST['searchEvent']
        SinaWeibo_spider(searchEvent)
        return render(request, 'SinaWeibo.html', {'success': 'success', 'searchEvent': searchEvent})
    else:
        return render(request, 'SinaWeibo.html')


# 新浪微博更新
def weibo_update(request):
    dic = {}

    liked_num = 0
    comment_num = 0
    shared_num = 0
    liked_num_top10_url = []
    liked_num_top10_count = []
    bloggers_nike = []
    bloggers_home_page  = []
    bloggers_followers_count = []

    weibo_obj = Sina_weibo_content.objects.all()

    weibo_num = len(weibo_obj)

    for i in weibo_obj:
        liked_num += i.liked_num
        comment_num += i.comment_num
        shared_num += i.shared_num

    weibo_obj_top10 = Sina_weibo_content.objects.filter().order_by('-liked_num')[0:10]
    for i in weibo_obj_top10:
        liked_num_top10_url.append(i.url)
        liked_num_top10_count.append(i.liked_num)

    bloggers = Sina_weibo.objects.filter().order_by('-followers_count')[0:10]
    for i in bloggers:
        bloggers_nike.append(i.nike)
        bloggers_home_page.append(i.home_page)
        bloggers_followers_count.append(i.followers_count)


    dic['weibo_num'] = weibo_num
    dic['liked_num'] = liked_num
    dic['comment_num'] = comment_num
    dic['shared_num'] = shared_num
    dic['liked_num_top10_url'] = liked_num_top10_url
    dic['liked_num_top10_count'] = liked_num_top10_count
    dic['bloggers_nike'] = bloggers_nike
    dic['bloggers_home_page'] = bloggers_home_page
    dic['bloggers_followers_count'] = bloggers_followers_count

    dic_json = json.dumps(dic)
    response = HttpResponse(dic_json)
    response['Content-Type'] = "text/javascript"
    return response


# 淘宝
def taobao(request):
    if request.method == 'POST':
        taobao_goods.objects.filter().delete()
        # 一旦发生poss事件，则在这里处理
        # 接收前端提交数据
        keyword = request.POST['keyword']
        global taobao_stop_flag
        taobao_stop_flag = 0
        taobao_spider(keyword)
        return render(request, 'taobao.html', {'success': 'success', 'keyword': keyword})
    else:
        return render(request, 'taobao.html')


# 淘宝更新
def TaoBao_update(request):

    dic = {}
    # 各省市，每个省市三个属性，商家数，交易数，商品均价
    beijing = []
    tianjin = []
    hebei = []
    shanxi = []
    neimenggu = []
    liaoning = []
    jilin = []
    heilongjiang = []
    shanghai = []
    jiangsu = []
    zhejiang = []
    anhui = []
    fujian = []
    jiangxi = []
    shandong = []
    henan = []
    hubei = []
    hunan = []
    chongqin = []
    sichuan = []
    guizhou = []
    yunnan = []
    xizang = []
    sanxi = []
    gansu = []
    qinghai = []
    ningxia = []
    xinjiang = []
    guangdong = []
    guangxi = []
    hainan = []

    Beijing = taobao_goods.objects.filter(location__icontains='北京')
    bus_peo_price(Beijing, beijing)
    Tianjin = taobao_goods.objects.filter(location__icontains='天津')
    bus_peo_price(Tianjin, tianjin)
    Hebei = taobao_goods.objects.filter(location__icontains='河北')
    bus_peo_price(Hebei, hebei)
    Shanxi = taobao_goods.objects.filter(location__icontains='山西')
    bus_peo_price(Shanxi, shanxi)
    Neimenggu = taobao_goods.objects.filter(location__icontains='内蒙古')
    bus_peo_price(Neimenggu, neimenggu)
    Liaoning = taobao_goods.objects.filter(location__icontains='辽宁')
    bus_peo_price(Liaoning, liaoning)
    Jilin = taobao_goods.objects.filter(location__icontains='吉林')
    bus_peo_price(Jilin, jilin)
    Heilongjiang = taobao_goods.objects.filter(location__icontains='黑龙江')
    bus_peo_price(Heilongjiang, heilongjiang)
    Shanghai = taobao_goods.objects.filter(location__icontains='上海')
    bus_peo_price(Shanghai, shanghai)
    Jiangsu = taobao_goods.objects.filter(location__icontains='江苏')
    bus_peo_price(Jiangsu, jiangsu)
    Zhejiang = taobao_goods.objects.filter(location__icontains='浙江')
    bus_peo_price(Zhejiang, zhejiang)
    Anhui = taobao_goods.objects.filter(location__icontains='安徽')
    bus_peo_price(Anhui, anhui)
    Fujian = taobao_goods.objects.filter(location__icontains='福建')
    bus_peo_price(Fujian, fujian)
    Jiangxi = taobao_goods.objects.filter(location__icontains='江西')
    bus_peo_price(Jiangxi, jiangxi)
    Shandong = taobao_goods.objects.filter(location__icontains='山东')
    bus_peo_price(Shandong, shandong)
    Henan = taobao_goods.objects.filter(location__icontains='河南')
    bus_peo_price(Henan, henan)
    Hubei = taobao_goods.objects.filter(location__icontains='湖北')
    bus_peo_price(Hubei, hubei)
    Hunan = taobao_goods.objects.filter(location__icontains='湖南')
    bus_peo_price(Hunan, hunan)
    Chongqin = taobao_goods.objects.filter(location__icontains='重庆')
    bus_peo_price(Chongqin, chongqin)
    Sichuan = taobao_goods.objects.filter(location__icontains='四川')
    bus_peo_price(Sichuan, sichuan)
    Guizhou = taobao_goods.objects.filter(location__icontains='贵州')
    bus_peo_price(Guizhou, guizhou)
    Yunnan = taobao_goods.objects.filter(location__icontains='云南')
    bus_peo_price(Yunnan, yunnan)
    Xizang = taobao_goods.objects.filter(location__icontains='西藏')
    bus_peo_price(Xizang, xizang)
    Sanxi = taobao_goods.objects.filter(location__icontains='陕西')
    bus_peo_price(Sanxi, sanxi)
    Gansu = taobao_goods.objects.filter(location__icontains='甘肃')
    bus_peo_price(Gansu, gansu)
    Qinghai = taobao_goods.objects.filter(location__icontains='青海')
    bus_peo_price(Qinghai, qinghai)
    Ningxia = taobao_goods.objects.filter(location__icontains='宁夏')
    bus_peo_price(Ningxia, ningxia)
    Xinjiang = taobao_goods.objects.filter(location__icontains='新疆')
    bus_peo_price(Xinjiang, xinjiang)
    Guangdong = taobao_goods.objects.filter(location__icontains='广东')
    bus_peo_price(Guangdong, guangdong)
    Guangxi = taobao_goods.objects.filter(location__icontains='广西')
    bus_peo_price(Guangxi, guangxi)
    Hainan = taobao_goods.objects.filter(location__icontains='海南')
    bus_peo_price(Hainan, hainan)


    dic['beijing'] = beijing
    dic['tianjin'] = tianjin
    dic['hebei'] = hebei
    dic['shanxi'] = shanxi
    dic['neimenggu'] = neimenggu
    dic['liaoning'] = liaoning
    dic['jilin'] = jilin
    dic['heilongjiang'] = heilongjiang
    dic['shanghai'] = shanghai
    dic['jiangsu'] = jiangsu
    dic['zhejiang'] = zhejiang
    dic['anhui'] = anhui
    dic['fujian'] = fujian
    dic['jiangxi'] = jiangxi
    dic['shandong'] = shandong
    dic['henan'] = henan
    dic['hubei'] = hubei
    dic['hunan'] = hunan
    dic['chongqin'] = chongqin
    dic['sichuan'] = sichuan
    dic['guizhou'] = guizhou
    dic['yunnan'] = yunnan
    dic['xizang'] = xizang
    dic['sanxi'] = sanxi
    dic['gansu'] = gansu
    dic['qinghai'] = qinghai
    dic['ningxia'] = ningxia
    dic['xinjiang'] = xinjiang
    dic['guangdong'] = guangdong
    dic['guangxi'] = guangxi
    dic['hainan'] = hainan
    dic_json = json.dumps(dic)
    response = HttpResponse(dic_json)
    response['Content-Type'] = "text/javascript"
    return response


# 淘宝商品均价
def bus_peo_price(obj, lis):
    bus_num = len(obj)
    people_num = 0
    price = 0.0
    ave = 0
    for i in obj:
        people_num += int(i.deal[:-3])
        price += float(i.price[1:])
    if people_num:
        ave = float('%.2f' % (price / bus_num))

    lis.append(bus_num)
    lis.append(people_num)
    lis.append(ave)


# 淘宝停止
def TB_to_stop(request):
    global taobao_stop_flag
    taobao_stop_flag = 1
    return render(request, 'taobao.html')


# 新浪新闻-----------------------------------
def SinaNews(request):
    if request.method == 'POST':
        # 一旦发生poss事件，则在这里处理
        # 接收前端提交数据
        searchEvent = request.POST['searchEvent']
        SinaNews_spider(searchEvent)
        return render(request, 'SinaNews.html', {'success': 'success', 'searchEvent': searchEvent})
    else:
        return render(request, 'SinaNews.html')


# 百度图片------------------------------------
def BaiduImg(request):
    if request.method == 'POST':
        # 一旦发生poss事件，则在这里处理
        # 接收前端提交数据
        baidu_picture.objects.filter().delete()
        searchEvent = request.POST['searchEvent']
        BaiduImg_spider(searchEvent)
        return render(request, 'BaiduImg.html', {'success': 'success', 'searchEvent': searchEvent})
    else:
        return render(request, 'BaiduImg.html')


# 百度进度条----------------------------------
def baidu_loading(request):
    dic = {}
    img_id = ''
    img_src = ''
    img_name = ''
    baidu_process_1 = baidu_picture.objects.filter().order_by('-id')[0:1]
    baidu_process = baidu_picture.objects.filter()

    for i in baidu_process_1:
        img_id = i.id
        img_src = i.imgurl
        img_name = i.imgname

    dic['imgid'] = img_id
    dic['imgsrc'] = img_src
    dic['imgname'] = img_name
    dic['lenght'] = len(baidu_process)

    dic_json = json.dumps(dic)
    response = HttpResponse(dic_json)
    response['Content-Type'] = "text/javascript"
    return response


# 知乎---------------------------------------
def zhihu(request):
    if request.method == 'POST':
        # 一旦发生poss事件，则在这里处理
        # 接收前端提交数据
        start = request.POST['sent']
        global zhihu_stop_flag
        zhihu_stop_flag = 0
        if start == 'start':
            zhihu_spider()
            return render(request, 'zhihu.html')
    else:
        return render(request, 'zhihu.html')


# 知乎更新------------------------------------
def bbb(request):

    dic = {}
    xinlixue_pay = xinlixue.objects.filter()
    dianyan_pay = dianyan.objects.filter()
    youxi_pay = youxi.objects.filter()
    yinyue_pay = yinyue.objects.filter()
    meishi_pay = meishi.objects.filter()

    number = []
    number.append(len(xinlixue_pay))
    number.append(len(dianyan_pay))
    number.append(len(youxi_pay))
    number.append(len(yinyue_pay))
    number.append(len(meishi_pay))


    # 各类别，金额总和
    count = []
    xinlixue_price_count = question_price_all(xinlixue_pay) / 100
    dianyan_price_count = question_price_all(dianyan_pay) / 100
    youxi_price_count = question_price_all(youxi_pay) / 100
    yinyue_price_count = question_price_all(yinyue_pay) / 100
    meishi_price_count = question_price_all(meishi_pay) / 100
    count.append(xinlixue_price_count)
    count.append(dianyan_price_count)
    count.append(youxi_price_count)
    count.append(yinyue_price_count)
    count.append(meishi_price_count)


    # 各类别人均问价：
    ave = []

    if len(xinlixue_pay) == 0:
        xinlixue_price_ave = 0
    else:
        xinlixue_price_ave = float('%.2f' % (xinlixue_price_count / len(xinlixue_pay)))

    if len(dianyan_pay) == 0:
        dianyan_price_ave = 0
    else:
        dianyan_price_ave = float('%.2f' % (dianyan_price_count / len(dianyan_pay)))

    if len(youxi_pay) == 0:
        youxi_price_ave = 0
    else:
        youxi_price_ave = float('%.2f' % (youxi_price_count / len(youxi_pay)))

    if len(yinyue_pay) == 0:
        yinyue_price_ave = 0
    else:
        yinyue_price_ave = float('%.2f' % (yinyue_price_count / len(yinyue_pay)))

    if len(meishi_pay) == 0:
        meishi_price_ave = 0
    else:
        meishi_price_ave = float('%.2f' % (meishi_price_count / len(meishi_pay)))

    # xinlixue_price_ave = float('%.2f' % (xinlixue_price_count / len(xinlixue_pay)))
    # dianyan_price_ave = float('%.2f' % (dianyan_price_count / len(dianyan_pay)))
    # youxi_price_ave = float('%.2f' % (youxi_price_count / len(youxi_pay)))
    # yinyue_price_ave = float('%.2f' % (yinyue_price_count / len(yinyue_pay)))
    # meishi_price_ave = float('%.2f' % (meishi_price_count / len(meishi_pay)))

    ave.append(xinlixue_price_ave)
    ave.append(dianyan_price_ave)
    ave.append(youxi_price_ave)
    ave.append(yinyue_price_ave)
    ave.append(meishi_price_ave)

    name = ['心理学', '电影', '游戏', '音乐', '美食']
    number2 = []
    for i in number:
        number2.append(i / 10)

    count2 = []
    for i in count:
        count2.append(i / 1000)

    dic['name'] = name
    dic['number'] = number2
    dic['count'] = count2
    dic['ave'] = ave
    # print(dic)

    dic_json = json.dumps(dic)
    response = HttpResponse(dic_json)
    response['Content-Type'] = "text/javascript"
    return response


# 知乎停止 ----------------------------------
def zhihu_to_stop(request):
    global zhihu_stop_flag
    zhihu_stop_flag = 1
    return render(request, 'zhihu.html')


headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }


# 今日头条--------------------------------
def headline_spider(offset, keyword):
    # 根据关键字和数量，进入搜索页面，得到图册列表
    def get_page_index(offset, keyword):
        data = {
            'offset': offset,
            'format': 'json',
            'keyword': keyword,
            'autoload': 'true',
            'count': '20',
            'cur_tab': 3,
            'from': 'gallery'
        }
        url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            return None
        except RequestException:
            print('请求页面出错！')
            return None

    # 解析当前页面数据，得到每个图册url
    def parse_page_index(html):
        try:
            data = json.loads(html)
            if data and 'data' in data.keys():
                for item in data.get('data'):
                    yield item.get('article_url')
        except JSONDecodeError:
            pass

    # 得到每个图册的详细信息
    def get_page_detail(url):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            return None
        except RequestException:
            print('请求详细页出错！', url)
            return None

    # 解析每个图册，获取title,url,images
    def parse_page_detail(html, url):
        soup = BeautifulSoup(html, 'lxml')
        title = soup.select('title')[0].get_text()
        # print(title)
        image_pattern = re.compile('gallery: JSON.parse\\("(.*?)"\\),', re.S)
        result = re.search(image_pattern, html)
        if result:
            # print(result.group(1).replace('\\', ''))   #去掉所有的‘\’符号
            try:
                data = json.loads(result.group(1).replace('\\', ''))  # group(1) 表示匹配第一个括号里面的内容
                data_desc = json.loads(eval(repr(result.group(1)).replace('\\\\', '\\')))

                if data and 'sub_images' in data.keys():
                    sub_images = data.get('sub_images')
                    images = [item.get('url') for item in sub_images]
                    abstracts = data_desc.get('sub_abstracts')

                    return {
                        'title': title,
                        'url': url,
                        'images': images,
                        'abstracts': abstracts
                    }
            except:
                pass

    def main(offset, keyword):
        html = get_page_index(offset, keyword)
        # print(html)
        for url in parse_page_index(html):
            global headline_stop_flag
            if headline_stop_flag == 1:
                break
            time.sleep(3)
            html = get_page_detail(url)
            if html:
                result = parse_page_detail(html, url)
                # print(result)
            if result:
                if headline_title_and_url.objects.filter(url=result['url']):
                    continue
                headline_title_and_url.objects.create(title=result['title'], url=result['url'])
                headline_id = headline_title_and_url.objects.get(url=result['url']).id

                for img in range(len(result['images'])):
                    # print(img)
                    headline_images.objects.create(fk_id=headline_id, images_url=result['images'][img], abstracts=result['abstracts'][img])

                # print('数据入库...')


    main(offset, keyword)


# 网易新闻-------------------------------
def wangyi_spider():
    number = 10
    while number <= 5000:
        global wangyiNews_stop_flag
        if wangyiNews_stop_flag == 1:
            break
        number += 10  # 刷新一页

        first_url = 'http://pic.news.163.com/photocenter/api/list/0001/00AN0001,00AO0001,00AP0001/%d/10/cacheMoreData.json' % number
        r = requests.get(first_url)
        r.encoding = ('utf-8')
        html = r.text
        # print(html)
        lis = re.findall(r'http://news.163.com.*?.html', html, re.S)  # 获取图片集地址存入data
        # print(lis)

        for url in lis:
            try:
                r = requests.get(url)
                html = r.text
            except:
                continue
            try:

                tag = ' '.join(
                    re.findall(r'http://news.163.com/special/photo-search/#q=(.{1,10})">.*?</a>\n ', html, re.S))
                title = re.findall(r'<div class="endpage-title"><h1>(.*)</h1></div>', html, re.S)[0]
                overview = \
                re.findall(r'<div class="viewport"><div class="overview"><p>(.*)</p></div></div>', html, re.S)[0]
            except:
                tag = ''
                title = ''
                overview = ''

            imgurl = re.findall(r'"oimg": "(.{3,100})",', html, re.S)
            note2 = re.findall(r'"note": "(.{3,500})",', html, re.S)


        note = []  # 每张图片对应的 note
        for i in note2:
            i = i.split('",\n')[0]
            note.append(i)
        if len(imgurl) > len(note):
            del imgurl[-1]

        try:
            if wangyi_news.objects.filter(title=title):
                number += 50
                continue
            wangyi_news.objects.create(title=title, tag=tag, overview=overview)
            wangyi_news_id = wangyi_news.objects.all().order_by('-id')[0].id

            for i in range(len(imgurl)):
                wangyi_news_images.objects.create(fk_id=wangyi_news_id, imgurl=imgurl[i], note=note[i])
        except:
            print('wrong')


# 新浪新闻--------------------------------
def SinaNews_spider(searchEvent):
    # 存放需要放入云图的所有文字
    cloud_data = ''

    # i为页数，可以设置大一点
    for i in range(1, 5):
        url = 'http://api.search.sina.com.cn/?c=news&t=&q=%s&page=%d&sort=rel&num=10&ie=utf-8&qq-pf-to=pcqq.c2c' % (
            searchEvent, i)

        r = requests.get(url, headers=headers)
        # print(r.text)
        # 匹配所有的url,'.{3,200}' 为url为长度控制
        temp = re.findall(r'"url":"(http:.{3,200}.shtml)",', r.text, re.S)
        # print(temp)
        # print(len(temp))
        # 去掉url里面的'\',这样request就不会出错。
        # 遍历data里面的url,逐个网页获取我们要的内容，并存进数据库。   有些文章的article形式不统一，所以会出现一些空的article
        for j in temp:
            j = j.replace('\\', '')
            r = requests.get(j)
            r.encoding = ('utf-8')
            # 非常致命的一点，如果html代码开头就有注释的话，BeautifulSoup是找不到想要的标签的!!!! 所以破坏掉前面的注释！
            html = r.text.replace('<!---->', '<!--###-->')
            # html = open('1.html', 'r', encoding='utf-8').read().replace('<!---->', '<!-- -->')
            # print(html)
            title = []
            tag = []
            description = []
            article = []

            try:
                soup = BeautifulSoup(html,
                                     "html5lib")  # 配置soup  'html5lib'优点：最好的容错性，以浏览器的方式解析文档，生成HTML5格式的文档  缺点：速度慢，不依赖外部扩展

                # title = re.findall(r'<meta property="og:title" content="(.*?)" />', html, re.S)[0]  # 有缺陷，meta是写给浏览器和爬虫看的，没有这个也不会影响内容，所有尽量后body里面的属性
                # keywords = re.findall(r'<meta name="keywords" content="(.*?)" />', html, re.S)[0]
                tag = re.findall(r'<meta name="tags" content="(.*?)" />', html, re.S)[
                    0]  # 但是非title属性一般都会在mata里面有，方便浏览器检索。
                description = re.findall(r'<meta name="description" content="(.*?)" />', html, re.S)[0]
                # article = re.findall(r'<div class="article" id="article"(.*?)</div>', html, re.S)[0]

                # BeautifulSoup去掉特定标签及内容的方法！！！！ 对象为 soup对象
                [s.extract() for s in soup('script')]
                [s.extract() for s in soup('style')]

                title = soup.find_all(class_='main-title')[0]  # 寻找 'main-title'类的内容
                title = re.sub(r'<[^>]*>', "", str(title))  # 去标签！
                article = soup.find_all("div", class_='article')[0]
                article = re.sub(r'<[^>]*>', "", str(article))  # 去掉所有的html标签！！  剩下的基本上都是文本内容。
            except:
                pass
            # print(title,'\n',tag,'\n',description,'\n',article)

            try:
                Sina_news.objects.create(title=title, tag=tag, description=description, article=article)
            except:
                pass

            # 不断累积的云图内容
            cloud_data = cloud_data + str(title) + str(tag) + str(description) + str(article)
    a = []
    # print(cloud_data)  # 分词前
    words = list(jieba.cut(cloud_data))  # 分词后
    for word in words:
        if len(word) > 1:
            a.append(word)
    txt = r' '.join(a)
    # print(txt)
    wordcloudplot(txt)


# 新浪新闻生成云图---------------------------
def wordcloudplot(txt):
    path = r'DataDisplay/wordcloud/hope.ttf'   # 字体文件地址
    alice_mask = np.array(Image.open('DataDisplay/wordcloud/love.png'))  # 面具图片地址
    wordcloud = WordCloud(font_path=path,                              # 生成云图样式
                          background_color="white",                    # 背景颜色
                          margin=5, width=1800, height=800, mask=alice_mask, max_words=150, max_font_size=100,  # 词云最大词数，最大size等
                          random_state=42)
    wordcloud = wordcloud.generate(txt)     # 根据给定的文本生成词云
    wordcloud.to_file('DataDisplay/wordcloud/dora.png')  # 文件存储路径
    plt.ion()  # 交互操作模式打开,就可以用到后面的暂停关闭
    plt.imshow(wordcloud)
    plt.axis("off")  # 展示方式
    plt.show()  # 展示
    plt.pause(50)  # 暂停5s
    plt.close()  # 关闭当前显示的图像


# 新浪微博
def SinaWeibo_spider(searchEvent):
    def getuser(key, page):
        url = "https://m.weibo.cn/api/container/getIndex?containerid=100103type=3&q=" + \
              key + "&t=0&page=" + str(page)
        url = urllib.parse.quote(url, safe='/:?=')
        data = use_proxy(url, proxy_addr())
        cards = json.loads(data).get('data').get(
            'cards')
        if (cards == []):
            return []
        if page == 1:
            content = cards[1].get('card_group')
        else:
            content = cards[0].get('card_group')
        userlist = []
        for item in content:
            userid = item.get('user').get('id')
            userlist.append(userid)
        return userlist

    # 获取微博大V账号的用户基本信息，如：微博昵称、微博地址、微博头像、关注人数、粉丝数、性别、等级等
    def get_userInfo(id):

        url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + id
        data = use_proxy(url, proxy_addr())
        content = json.loads(data).get('data')
        profile_image_url = content.get('userInfo').get('profile_image_url')
        description = content.get('userInfo').get('description')
        home_page = content.get('userInfo').get('profile_url')
        verified = content.get('userInfo').get('verified')
        follow_count = content.get('userInfo').get('follow_count')
        nike = content.get('userInfo').get('screen_name')
        followers_count = content.get('userInfo').get('followers_count')
        gender = content.get('userInfo').get('gender')
        urank = content.get('userInfo').get('urank')
        print(
            "微博昵称：" + nike + "\n" + "微博主页地址：" + home_page + "\n" + "微博头像地址：" + profile_image_url + "\n" + "是否认证：" + str(
                verified) + "\n" + "微博说明：" +
            description + "\n" + "关注人数：" + str(follow_count) + "\n" + "粉丝数：" + str(
                followers_count) + "\n" + "性别：" + gender + "\n" + "微博等级：" + str(urank) + "\n")

        try:
            Sina_weibo.objects.create(id=id, nike=nike, image_url=profile_image_url, home_page=home_page,
                                      follow_count=follow_count, followers_count=followers_count, gender=gender,
                                      urank=urank, description=description)
        except urllib.error.HTTPError as e:
            print('url:\t' + url)
            print('proxy_ip:\t' + proxy_addr)
            print(e)
            if '403' in str(e) or '418' in str(e):
                raise e

    # 获取微博主页的containerid，爬取微博内容时需要此id
    def get_containerid(url):
        data = use_proxy(url, proxy_addr())
        content = json.loads(data).get('data')
        for data in content.get('tabsInfo').get('tabs'):
            if (data.get('tab_type') == 'weibo'):
                containerid = data.get('containerid')
        return containerid

    # 根据用户id获取全部微博内容信息,并保存到文本中，内容包括：每条微博的内容、
    # 微博详情页面地址、点赞数、评论数、转发数,来源等
    def get_weibo(id, jobname):
        i = 1
        url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + id
        containerid = get_containerid(url)

        while True:
            weibo_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + \
                        id + '&containerid=' + containerid + '&page=' + str(i)
            proxy_addr1 = proxy_addr()
            try:
                data = use_proxy(weibo_url, proxy_addr1)
                content = json.loads(data).get('data')
                cards = content.get('cards')
                if (len(cards) > 0):
                    for j in range(len(cards)):
                        # print("     -----正在爬取第" + str(i) + "页，第" + str(j) +
                        #       "条微博------")
                        card_type = cards[j].get('card_type')
                        if (card_type == 9):
                            mblog = cards[j].get('mblog')
                            attitudes_count = mblog.get('attitudes_count')
                            comments_count = mblog.get('comments_count')
                            created_at = mblog.get('created_at')
                            if len(created_at) < 6:
                                created_at = '2018-' + created_at
                            if '前' in created_at:
                                today = datetime.date.today()
                                created_at = '%d-%d-%d' % (today.year,
                                                           today.month, today.day)
                            if '昨天' in created_at:
                                today = datetime.date.today()
                                created_at = '%d-%d-%d' % (today.year,
                                                           today.month, today.day - 1)
                            # print('日期 ' + created_at)
                            reposts_count = mblog.get('reposts_count')
                            scheme = cards[j].get('scheme')
                            text = mblog.get('text')
                            userid = mblog.get('user').get('id')
                            wid = mblog.get('id')
                            source = mblog.get('source')
                            # 微博数据存储到数据库
                            Sina_weibo_content.objects.create(id=wid, url=scheme, date=created_at, content=text,
                                                              liked_num=int(attitudes_count),
                                                              comment_num=int(comments_count),
                                                              shared_num=int(reposts_count), userid=userid,
                                                              source=source)

                    i += 1
                    time.sleep(5)
                else:
                    break
            except urllib.error.HTTPError as e:
                print('url:\t' + url)
                print('proxy_ip:\t' + proxy_addr1)
                print(e)
                if '403' in str(e) or '418' in str(e):
                    raise e
            except Exception as e:
                print(e)
                i += 1
                pass

    # 多线程任务1 由betch_job1调用
    def job_user_and_blog(userid, jobname):
        try:
            get_userInfo(userid)
            get_weibo(userid, jobname)
        except urllib.error.HTTPError as e:
            for times in range(5):

                print('sleep 1 min ')
                time.sleep(60)
                try:
                    get_userInfo(userid)
                    get_weibo(userid, jobname)
                    break
                except urllib.error.HTTPError as e1:
                    print(e1)
                    pass

    # 批处理任务 根据关键字查找用户，再搜索微博信息
    # 多线程处理 停止后可自动重新从停止时开始
    def betch_job1(key):
        start_time = time.time()
        pool = threadpool.ThreadPool(20)
        for i in range(10):
            users1 = getuser(key, i + 1)
            users2 = getuser(key, i + 1)
            attr_list = []
            ii = 1
            for userid in users1:
                li = []
                li.append(str(userid))
                li.append('博主所有微博_' + str(i) + '_' + str(userid))
                attr_list.append((li, None))
                ii = ii + 1
            ii = 1
            for userid in users2:
                li = []
                li.append(str(userid))
                li.append('博主所有微博_' + str(i) + '_' + str(userid))
                attr_list.append((li, None))
                ii = ii + 1
            print('key:' + key + '_，正在抓取第' + str(i + 1) + '页用户')
            print(attr_list)
            requests = threadpool.makeRequests(job_user_and_blog, attr_list)
            [pool.putRequest(req) for req in requests]
            pool.wait()

        print('%d second' % (time.time() - start_time))

    # keyword = input("请输入关键词：\n")
    betch_job1(searchEvent)


# 百度图片-------------------------------------
def BaiduImg_spider(searchEvent):

    str_table = {
        '_z2C$q': ':',
        '_z&e3B': '.',
        'AzdH3F': '/'
    }

    char_table = {
        'w': 'a',
        'k': 'b',
        'v': 'c',
        '1': 'd',
        'j': 'e',
        'u': 'f',
        '2': 'g',
        'i': 'h',
        't': 'i',
        '3': 'j',
        'h': 'k',
        's': 'l',
        '4': 'm',
        'g': 'n',
        '5': 'o',
        'r': 'p',
        'q': 'q',
        '6': 'r',
        'f': 's',
        'p': 't',
        '7': 'u',
        'e': 'v',
        'o': 'w',
        '8': '1',
        'd': '2',
        'n': '3',
        '9': '4',
        'c': '5',
        'm': '6',
        '0': '7',
        'b': '8',
        'l': '9',
        'a': '0'
    }

    # str 的translate方法需要用单个字符的十进制unicode编码作为key
    # value 中的数字会被当成十进制unicode编码转换成字符
    # 也可以直接用字符串作为value
    char_table = {ord(key): ord(value) for key, value in char_table.items()}

    # 解码图片URL
    def decode(url):
        # 先替换字符串
        for key, value in str_table.items():
            url = url.replace(key, value)
        # 再替换剩下的字符
        return url.translate(char_table)

    # 生成网址列表
    def buildUrls(word):
        word = urllib.parse.quote(word)
        url = r"http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&fp=result&queryWord={word}&cl=2&lm=-1&ie=utf-8&oe=utf-8&st=-1&ic=0&word={word}&face=0&istype=2nc=1&pn={pn}&rn=60"
        urls = (url.format(word=word, pn=x) for x in itertools.count(start=0, step=60))
        return urls

    # 解析JSON获取图片URL
    re_url = re.compile(r'"objURL":"(.*?)"')

    def resolveImgUrl(html):
        imgUrls = [decode(x) for x in re_url.findall(html)]
        return imgUrls

    def downImg(imgUrl, dirpath, imgName):
        filename = os.path.join(dirpath, imgName)
        try:
            res = requests.get(imgUrl, timeout=15)
            if str(res.status_code)[0] == "4":
                print(str(res.status_code), ":", imgUrl)
                return False
        except Exception as e:
            print("抛出异常：", imgUrl)
            print(e)
            return False
        with open(filename, "wb") as f:
            f.write(res.content)
        return True

    def mkDir(dirName):
        dirpath = os.path.join(sys.path[0], dirName)
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        return dirpath


    # word = input("请输入你要下载的图片关键词：\n")
    word = searchEvent

    dirpath = mkDir("results")

    urls = buildUrls(word)
    index = 0
    for url in urls:
        print("正在请求：", url)
        html = requests.get(url, timeout=10).content.decode('utf-8')
        imgUrls = resolveImgUrl(html)
        if len(imgUrls) == 0:  # 没有图片则结束
            break
        for url in imgUrls:
            if downImg(url, dirpath, str(index) + ".jpg"):
                index += 1
                time.sleep(0.3)
                print("已下载 %s 张" % index)
                if index == 100:
                    break
            baidu_picture.objects.create(imgurl=url, imgname=word)
        if index == 100:
            break


# 淘宝商品
def taobao_spider(keyword):
    # browser = webdriver.Chrome()
    SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']
    browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)  # 无界面运行
    # browser = webdriver.PhantomJS(executable_path='D://Anaconda3//selenium//webdriver//phantomjs-2.1.1-windows//bin//phantomjs')
    wait = WebDriverWait(browser, 10)

    browser.set_window_size(1400, 900)

    def search():
        print('正在搜索')
        try:
            browser.get('https://www.taobao.com')
            input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#q')))
            submit = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
            input.send_keys(keyword)
            submit.click()
            totle = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
            get_products()

            return totle.text
        # 很重要的一点：充分的利用 try, except来解决错误！ 该处虽然也是报的跟timeout有关的错误，但是并不是TimeoutError这个错误！所以干脆捕获所有错误！
        # except TimeoutError:
        except:
            return search()  # 重新请求

    def next_page(page_number):
        # time.sleep(5)
        print('正在翻页')
        try:
            input = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
            submit = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
            input.clear()
            input.send_keys(page_number)
            submit.click()  # 执行翻页操作
            wait.until(EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number)))

            get_products()

        except TimeoutError:
            next_page(page_number)

    def get_products():
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
        html = browser.page_source
        doc = pq(html)
        items = doc('#mainsrp-itemlist .items .item').items()
        for item in items:
            product = {
                'image': item.find('.pic .img').attr('src'),
                'price': item.find('.price').text().replace('\n', ''),
                'deal': item.find('.deal-cnt').text(),
                'title': item.find('.title').text().replace('\n', ''),
                'shop': item.find('.shop').text(),
                'location': item.find('.location').text()
            }
            # print(product)
            taobao_goods.objects.create(image=product['image'], price=product['price'], deal=product['deal'],
                                        title=product['title'], shop=product['shop'], location=product['location'])

    def main():
        try:
            total = search()  # 共100页，
            total = int(re.compile('(\d+)').search(total).group(1))  # 取数字100
            print(total)  # 100
            for i in range(2, total + 1):
                global taobao_stop_flag
                if taobao_stop_flag == 1:
                    browser.close()
                next_page(i)
        except Exception:
            print(Exception)
            # finally:
            #     browser.close()

    global taobao_stop_flag
    if taobao_stop_flag == 0:
        main()



# 知乎答主
def zhihu_spider():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        'cookies': '_zap=c7375486-4e80-4d04-ab23-a660131e26f0; q_c1=44470a028b2e42a7a7a5b0c95c7162d0|1505908172000|1502961616000; q_c1=44470a028b2e42a7a7a5b0c95c7162d0|1519874338000|1502961616000; aliyungf_tc=AQAAALQ+jSqytw4Ai1G3PTU8YYDVuSz3; _xsrf=79975523c9d0e71eabc822008e319fe7; l_n_c=1; l_cap_id="ZTMxODcxNDcwMmUzNDJhOTg4MjZkOTg3NWFlMTk1ZGE=|1519965266|87a6d04c92ccd8ef081bb6378b199c184c47d888"; r_cap_id="YjIxZmJkNTU2ODgxNDc1N2IxM2YyMDkwMDY1Y2ZkNmE=|1519965266|d05a248af174b2e683e8004f343f21063b3ab036"; cap_id="ZjA0MGQwOWFkNzhhNGUxN2I5MzY0NjhiM2YwMWY2YWM=|1519965266|a58c6aeac69689f1f7677a7e29c747c64572288a"; n_c=1; __utma=155987696.1220683017.1519965266.1519965266.1519965266.1; __utmc=155987696; __utmz=155987696.1519965266.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); capsion_ticket="2|1:0|10:1519965367|14:capsion_ticket|44:MWQyZjYzY2M1ZGYwNDhjZjllMDJiYTcxOGZhMjEzOGY=|ef641fd398c8517dc6c15da7cd91c7d52c5e86136e12e767f04a59711b450a9d"; z_c0="2|1:0|10:1519965376|4:z_c0|80:MS4xeWpPT0J3QUFBQUFtQUFBQVlBSlZUY0FpaGx2YnRNdUtUWjRHQm1PRHA0RUl3NWpIOHA3S3NRPT0=|d7c9c42a6ff17ad9ecde1086d30fecbbe1d264db6910cbc91082de8646bc58d4"; __utmv=155987696.|1=userId=952884057676181504=1; d_c0="AODsWitVOQ2PTqCYYL7_hSOM-kaQUAJh5PM=|1519965831"; infinity_uid="2|1:0|10:1519967198|12:infinity_uid|24:OTUyODg0MDU3Njc2MTgxNTA0|9962897b470ac1fe68597da5b7ca7188c6a20c6a8f61d070630a0e3fa50df4e2"; __utmt=1; __utmb=155987696.115.0.1519967549997',
    }

    def parse(url, table):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # print(type(response.text))
            data = json.loads(response.text)
            for item in data['data']:
                bio = item['bio']
                description = item['description']
                answer_count = item['answer_count']
                zhihu_url = str(item['zhihu_url'])
                public_answer_count = item['public_answer_count']
                user_id = str(item['id'])
                user_name = item['name']
                gender = item['gender']
                avatar_url = str(item['avatar_url'])
                question_price = item['question_price']
                follower_count = item['follower_count']

                if table.objects.filter(user_id=user_id):
                    continue
                table.objects.create(bio=bio, description=description, answer_count=answer_count, zhihu_url=zhihu_url,
                                     public_answer_count=public_answer_count, user_id=user_id, user_name=user_name,
                                     gender=gender, avatar_url=avatar_url, question_price=question_price,
                                     follower_count=follower_count)
                print('数据入库...')

    # 心理学
    def xinlixue_spider():
        print('正在爬取心理学类答主信息...')
        for offset in range(100):
            global zhihu_stop_flag
            if zhihu_stop_flag == 1:
                break
            url = 'https://www.zhihu.com/zhi/infinity/topics/19551432/answerers?limit=10&offset=%d' % (offset * 10)
            # time.sleep(1)
            parse(url, xinlixue)
        print('完成')



    # 电影
    def dianyan_spider():
        print('正在爬取电影类答主信息...')
        for offset in range(100):
            global zhihu_stop_flag
            if zhihu_stop_flag == 1:
                break
            url = 'https://www.zhihu.com/zhi/infinity/topics/19550429/answerers?limit=10&offset=%d' % (offset * 10)
            parse(url, dianyan)
        print('完成')

    # 游戏
    def youxi_spider():
        print('正在爬取游戏类答主信息...')
        for offset in range(100):
            global zhihu_stop_flag
            if zhihu_stop_flag == 1:
                break
            url = 'https://www.zhihu.com/zhi/infinity/topics/19550994/answerers?limit=10&offset=%d' % (offset * 10)
            parse(url, youxi)
        print('完成')

    # 音乐
    def yinyue_spider():
        print('正在爬取音乐类答主信息...')
        for offset in range(100):
            global zhihu_stop_flag
            if zhihu_stop_flag == 1:
                break
            url = 'https://www.zhihu.com/zhi/infinity/topics/19550453/answerers?limit=10&offset=%d' % (offset * 10)
            parse(url, yinyue)
        print('完成')


    # 美食
    def meishi_spider():
        print('正在爬取美食类答主信息...')
        for offset in range(100):
            global zhihu_stop_flag
            if zhihu_stop_flag == 1:
                break
            url = 'https://www.zhihu.com/zhi/infinity/topics/19551137/answerers?limit=10&offset=%d' % (offset * 10)
            parse(url, meishi)
        print('完成')

    # 爬取数据
    xinlixue_spider()
    dianyan_spider()
    youxi_spider()
    yinyue_spider()
    meishi_spider()


# 知乎问价总和
def question_price_all(cls):
    price = 0
    for i in cls:
        price += i.question_price
    return price
