from django.conf.urls import url
from . import views

urlpatterns=[
	url(r'^login',views.login),
	url(r'register',views.register),
	url(r'ajaxhaddle',views.ajax_response),
	url(r'alterinfo',views.alter_info),
	url(r'^MenuFrame',views.MenuFrame),
	url(r'^topFrame', views.topFrame),
	url(r'^colFrame', views.colFrame),
	url(r'^pushRLFrame', views.pushRLFrame),
	url(r'^PageFrame', views.PageFrame),
	url(r'^user', views.user),
	url(r'^Headline', views.Headline),
	url(r'^WangyiNews', views.WangyiNews),
	url(r'^SinaWeibo', views.SinaWeibo),
	url(r'^taobao', views.taobao),
	url(r'^SinaNews', views.SinaNews),
	url(r'^BaiduImg', views.BaiduImg),
	url(r'^zhihu', views.zhihu),


	url(r'^aaa', views.aaa),  # 网易新闻图片更新
	url(r'^wangyiNews_to_stop', views.wangyiNews_to_stop),  # 网易新闻图片暂停

	url(r'^headline_update', views.headline_update),   # 头条更新
	url(r'^headline_to_stop', views.headline_to_stop),  # 头条暂停
	url(r'^baidu_loading', views.baidu_loading),  # 百度图片更新
	url(r'^ZhihuToStop', views.zhihu_to_stop),  # 知乎暂停

	url(r'^bbb', views.bbb),  # 知乎更新
	url(r'^TB_to_stop', views.TB_to_stop),  # 淘宝暂停
	url(r'^TaoBao_update', views.TaoBao_update),  # 淘宝更新
	url(r'^weibo_update', views.weibo_update),  # 淘宝更新




]