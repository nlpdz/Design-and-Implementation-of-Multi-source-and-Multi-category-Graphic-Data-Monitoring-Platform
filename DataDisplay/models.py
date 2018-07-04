# coding=utf-8
from __future__ import unicode_literals

from django.db import models
# Create your models here.



#3.
class User(models.Model):
	id = models.AutoField(primary_key=True)
	username = models.CharField(max_length=90)
	password = models.CharField(max_length=16)
	shopintroduct = models.TextField()
	class Meta:
		db_table='User'



#4.商家头像
class UserHeader(models.Model):
	id = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
	#[关系映射一：（1:1）] 商家头像和商家是1:1的关系，这种关系要通过主键来映射
	url = models.FileField(upload_to='UserHeader') # 暂定字符类型
	class Meta:
		db_table='UserHeader'



class zhihu_anwsers(models.Model):
    bio = models.TextField(max_length=100, null=True)
    description = models.TextField(max_length=100, null=True)
    answer_count = models.IntegerField(null=True)
    zhihu_url = models.CharField(max_length=100, null=True)
    public_answer_count = models.IntegerField(null=True)
    user_id = models.CharField(max_length=100, null=True)
    user_name = models.TextField(max_length=100, null=True)
    gender = models.IntegerField(null=True)
    avatar_url = models.CharField(max_length=100, null=True)
    question_price = models.IntegerField(null=True)
    follower_count = models.IntegerField(null=True)



class headline_title_and_url(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.TextField(max_length=100, null=True)
	url = models.CharField(max_length=100, null=True)


class headline_images(models.Model):
	fk_id = models.IntegerField(null=True)
	images_url = models.CharField(max_length=100, null=True)
	abstracts = models.TextField(max_length=100, null=True)


class wangyi_news(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.TextField(max_length=1000, null=True)
	tag = models.TextField(max_length=100, null=True)
	overview = models.TextField(max_length=1000, null=True)


class wangyi_news_images(models.Model):
	fk_id = models.IntegerField(null=True)
	imgurl = models.CharField(max_length=100, null=True)
	note = models.TextField(max_length=1000, null=True)



class Sina_news(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.TextField(max_length=100, null=True)
	tag = models.TextField(max_length=100, null=True)
	description = models.TextField(max_length=1000, null=True)
	article = models.TextField(max_length=3000, null=True)



class Sina_weibo(models.Model):
	id = models.CharField(max_length=100, primary_key=True)
	nike = models.CharField(max_length=40, null=True)
	image_url = models.CharField(max_length=500, null=True)
	home_page = models.CharField(max_length=500, null=True)
	follow_count = models.IntegerField(null=True)
	followers_count = models.IntegerField(null=True)
	gender =models.CharField(max_length=2, null=True)
	urank = models.IntegerField(null=True)
	description = models.TextField(max_length=300, null=True)


class Sina_weibo_content(models.Model):
	id = models.CharField(max_length=100, primary_key=True)
	url = models.CharField(max_length=100, null=True)
	date = models.DateTimeField(auto_now_add=True)
	content = models.TextField(max_length=1000, null=True)
	liked_num = models.IntegerField(null=True)
	comment_num = models.IntegerField(null=True)
	shared_num = models.IntegerField(null=True)
	userid = models.CharField(max_length=20, null=True)
	source = models.CharField(max_length=20, null=True)


class taobao_goods(models.Model):
	id = models.AutoField(primary_key=True)
	image = models.CharField(max_length=100, null=True)
	price = models.CharField(max_length=100, null=True)
	deal = models.CharField(max_length=100, null=True)
	title = models.CharField(max_length=100, null=True)
	shop = models.CharField(max_length=100, null=True)
	location = models.CharField(max_length=100, null=True)


class baidu_picture(models.Model):
	id = models.AutoField(primary_key=True)
	imgurl = models.CharField(max_length=100, null=True)
	imgname = models.CharField(max_length=100, null=True)













class dianyan(models.Model):
    bio = models.TextField(max_length=100, null=True)
    description = models.TextField(max_length=100, null=True)
    answer_count = models.IntegerField(null=True)
    zhihu_url = models.CharField(max_length=100, null=True)
    public_answer_count = models.IntegerField(null=True)
    user_id = models.CharField(max_length=100, null=True)
    user_name = models.TextField(max_length=100, null=True)
    gender = models.IntegerField(null=True)
    avatar_url = models.CharField(max_length=100, null=True)
    question_price = models.IntegerField(null=True)
    follower_count = models.IntegerField(null=True)




class meishi(models.Model):
    bio = models.TextField(max_length=100, null=True)
    description = models.TextField(max_length=100, null=True)
    answer_count = models.IntegerField(null=True)
    zhihu_url = models.CharField(max_length=100, null=True)
    public_answer_count = models.IntegerField(null=True)
    user_id = models.CharField(max_length=100, null=True)
    user_name = models.TextField(max_length=100, null=True)
    gender = models.IntegerField(null=True)
    avatar_url = models.CharField(max_length=100, null=True)
    question_price = models.IntegerField(null=True)
    follower_count = models.IntegerField(null=True)




class xinlixue(models.Model):
    bio = models.TextField(max_length=100, null=True)
    description = models.TextField(max_length=100, null=True)
    answer_count = models.IntegerField(null=True)
    zhihu_url = models.CharField(max_length=100, null=True)
    public_answer_count = models.IntegerField(null=True)
    user_id = models.CharField(max_length=100, null=True)
    user_name = models.TextField(max_length=100, null=True)
    gender = models.IntegerField(null=True)
    avatar_url = models.CharField(max_length=100, null=True)
    question_price = models.IntegerField(null=True)
    follower_count = models.IntegerField(null=True)


class yinyue(models.Model):
    bio = models.TextField(max_length=100, null=True)
    description = models.TextField(max_length=100, null=True)
    answer_count = models.IntegerField(null=True)
    zhihu_url = models.CharField(max_length=100, null=True)
    public_answer_count = models.IntegerField(null=True)
    user_id = models.CharField(max_length=100, null=True)
    user_name = models.TextField(max_length=100, null=True)
    gender = models.IntegerField(null=True)
    avatar_url = models.CharField(max_length=100, null=True)
    question_price = models.IntegerField(null=True)
    follower_count = models.IntegerField(null=True)




class youxi(models.Model):
    bio = models.TextField(max_length=100, null=True)
    description = models.TextField(max_length=100, null=True)
    answer_count = models.IntegerField(null=True)
    zhihu_url = models.CharField(max_length=100, null=True)
    public_answer_count = models.IntegerField(null=True)
    user_id = models.CharField(max_length=100, null=True)
    user_name = models.TextField(max_length=100, null=True)
    gender = models.IntegerField(null=True)
    avatar_url = models.CharField(max_length=100, null=True)
    question_price = models.IntegerField(null=True)
    follower_count = models.IntegerField(null=True)


