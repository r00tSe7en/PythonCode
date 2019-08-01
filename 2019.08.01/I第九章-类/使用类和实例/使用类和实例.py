#!/usr/bin/env python
#coding=utf-8
class Car():
    '''一次模拟汽车的简单尝试'''
    def __init__(self, make, model, year):
        '''初始化汽车的属性'''
        self.make = make
        self.model = model
        self.year = year
    def get_descriptive_name(self):
        '''返回简洁的描述信息'''
        long_name = str(self.year) + ' ' + self.make + ' ' + self.model
        return  long_name.title()
my_new_car = Car('audi','A8',2019)
print(my_new_car.get_descriptive_name())