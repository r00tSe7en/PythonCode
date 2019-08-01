#!/usr/bin/env python
#coding=utf-8
file_name = 'test1.txt'
try:
    with open(file_name) as file_object:
        contents = file_object.read()
        print(contents)
except FileNotFoundError:
        print("找不到文件")

