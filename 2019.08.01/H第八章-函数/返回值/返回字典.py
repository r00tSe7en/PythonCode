#!/usr/bin/env python
#coding=utf-8
def build_person(first_name, last_name, age=''):
    """返回一个字典，其中包含有关一个人的信息"""
    person = {'first': first_name, 'last': last_name}
    #判断是否有age参数，有则添加进字典
    if age:
        person['age'] = age
    return person
musician = build_person('jimi', 'hendrix', age=27)
print(musician)
