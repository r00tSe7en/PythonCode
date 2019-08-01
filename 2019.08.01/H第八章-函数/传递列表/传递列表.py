#!/usr/bin/env python
#coding=utf-8
def get_user(info):
    for userinfo in info:
        print(userinfo.title())
userinfo = ['Se7en','boy','cool']
get_user(userinfo)