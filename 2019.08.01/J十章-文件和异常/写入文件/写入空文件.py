#!/usr/bin/env python
#coding=utf-8
file_name = 'programing.txt'
#添加到末尾用'a','w'清空并重新写入
with open(file_name, 'w') as file_object:
    file_object.write("I love Programing.\n")
    file_object.write("I love Programing.\n")
