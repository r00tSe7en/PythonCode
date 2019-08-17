#!/usr/bin/env python
#coding=utf-8
import requests
import time
import re

url="https://www.baidu.com/admin/"
my_cookies = dict(admin='xxxxxxxxx')
my_headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36', 'Accept-Encoding' : 'gzip, deflate, sdch'}

def sleep_time(hour, min, sec):
    return hour * 3600 + min * 60 + sec

#时间设置 时/分/秒
second = sleep_time(0, 0, 10)

def keep_session():
    response = requests.get(url, cookies=my_cookies,headers=my_headers)
    #正则匹配网页返回源码中是否含有目标用户名
    result = re.search(r'forixadmin',response.text)
    if result:
        print('All RIGHT!')
    else:
        print('FAIL!')

while True:
    time.sleep(second)
    keep_session()