#!/usr/bin/env python
#coding=utf-8
favorite_languagee = {
    'jen': 'python',
    'sarah': 'c',
    'edward': 'ruby',
    'phil': 'python',
#    'Se7en': 'php'
}
for name in favorite_languagee:
    print("name:"+name)
if 'Se7en' not in favorite_languagee.keys():
    #此处的key()返回的是一个列表
    print("please Se7en take our poll!")
if 'php' not in favorite_languagee.values():
    print("please add php in language!")