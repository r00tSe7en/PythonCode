#!/usr/bin/env python
#coding=utf-8
alien_0 = {'color':'green','points':5}
print(alien_0)
#增加
alien_0['x_position'] = 0
alien_0['y_position'] = 25
print(alien_0)
#删除
del alien_0['x_position']
del alien_0['y_position']
print(alien_0)
