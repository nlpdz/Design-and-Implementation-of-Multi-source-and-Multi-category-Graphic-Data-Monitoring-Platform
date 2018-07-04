#-*- encoding: utf-8 -*import os, sys, string
import MySQLdb # 导入 MySQLdb 模块
# 连接数据库 try:
conn = MySQLdb.connect (host=' localhost',user='root',
passwd='rainman',db='rest') except Exception, e:
print e
sys.exit ()
# 获取 cursor 对象来进行操作 cursor = conn.cursor ()
# 创建表
sql = " create table if not exists test1 (name varchar (128) primary key, age int (4))"
cursor.execute (sql)
# 插入数据
sql = " insert into test1 (name, age)	values	('%s', %d)"%	(" zhaowei" , 23)
try:
cursor.execute (sql)
except Exception, e:
print e
	sql = " insert into test1 (name, age)	values('%s', %d)"%	(" 张三" , 21)
try:
cursor.execute (sql)
except Exception, e:
print e
