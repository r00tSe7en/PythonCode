#!/usr/bin/env python
#coding=utf-8
list = ['abcd','ABCD','1234','5678']
print(list)
del list[0]
print(list)
list.pop(0)
print(list)
#根据值删除元素
list.remove('1234')
print(list)