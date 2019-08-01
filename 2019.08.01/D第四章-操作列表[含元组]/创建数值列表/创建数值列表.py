#!/usr/bin/env python
#coding=utf-8
#从1开始，至5结束
for value in range(1,5):
    print(value)
#创建数字列表
value = list(range(1,5))
print(value)
#创建数字列表,不断加2
value = list(range(1,5,2))
print(value)
#创建一个求平方列表
squares=[]
for value in range(1,5):
    squares.append(value**2)
print(squares)