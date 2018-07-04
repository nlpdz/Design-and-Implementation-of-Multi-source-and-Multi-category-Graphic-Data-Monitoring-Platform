# Design-and-Implementation-of-Multi-source-and-Multi-category-Graphic-Data-Monitoring-Platform
多源多分类图文数据监控平台设计与实现（Python、Django、爬虫、Echarts等技术）
> 简介：该系统基于Python3.6，使用了Django框架搭建web站点，主要功能是将今日头条、淘宝、Sina新闻，Sina微博，
网易新闻、百度图片、知乎答主爬虫集中在一个站点，各个爬虫在进行抓取数据的同时将采集数据过程可视化，前端可视化
主要用到了Echarts图表插件。

## 快速开始
1. 克隆项目：
```
git clone https://github.com/nlpdz/Design-and-Implementation-of-Multi-source-and-Multi-category-Graphic-Data-Monitoring-Platform.git
```
2. 安装pip，通过pip安装Django：

```
pip install Django
```
3. 进入到Design-and-Implementation-of-Multi-source-and-Multi-category-Graphic-Data-Monitoring-Platform根目录，运行命令：

```
python manage.py runserver
```
4. 访问登陆界面，地址为：

```
127.0.0.1:8000/login
```

## 目录说明

```
├──Design-and-----------------------------根目录</br>
├────DataAnalysis-------------------------Django项目的核心</br>
├-----└──settings-------------------------配置文件</br>
├-----└──urls-----------------------------路由</br>
├────DataDisplay--------------------------我们创建的app项目</br>
├-----└──migrations-----------------------数据库迁移文件</br>
├-----└──models---------------------------数据库配置文件</br>
├-----└──urls-----------------------------局部路由</br>
├-----└──views----------------------------函数控制文件</br>
├-----└──static---------------------------静态文件目录</br>
├-------└──css------------------------------样式们</br>
├-------└──imgs-----------------------------图片们</br>
├-------└──js-------------------------------js们</br>
├-------└──plugins--------------------------插件们</br>
├-------└──templates------------------------html集合</br>
├────media--------------------------------主要存放用户头像</br>
├────results------------------------------百度爬虫的图片下载目录</br>
├────db.sqlite3---------------------------数据库</br>
├────manage.py----------------------------入口
```

## 开发流程

1. 创建页面  
Templates文件夹下创建html页；
views.py中return页面；
urls.py中注册路径；

2. 创建model  
models.py中建类
确定settings中注册app；
python manage.py makemigrations（保存临时）；
python manage.py migrate（真正创建）；
在views.py中实现相关功能；

3. 修改model  
在models.py中修改；
python manage.py makemigrations；
python manage.py migrate；
更新model失败：给字段增加参数null=True，重新运行；

4. 静态文件更新不及时  
静态目录被访问多次后会加入缓存，可以修改一下静态文件名（推荐增加前缀）

5. 注册管理员  
```
    python manage.py createsuperuser
```

6. 注册管理员站点  
修改admin.py，其中UserInfo是表，DataDisplay是app名字
```
    from django.contrib import admin
    from DataDisplay.models import UserInfo
    
    admin.site.register(UserInfo)
```
7. 输入网址访问本地后台管理

```
    120.0.0.1/admin
```

***未提及的部分请善用开源Django文档以及网络。***
