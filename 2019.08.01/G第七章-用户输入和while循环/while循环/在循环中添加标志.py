#!/usr/bin/env python
#coding=utf-8
name = input("Please input your name:")
flag = True
while flag:
    if name != 'Se7en' :
        name = input("Please input your name:")
        flag = True
    else:
        print(name)
        flag = False
