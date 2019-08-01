#!/usr/bin/env python
#coding=utf-8
class Car():
    '''一次模拟汽车的简单尝试'''
    def __init__(self, make, model, year):
        '''初始化汽车的属性'''
        self.make = make
        self.model = model
        self.year = year
        self.odometer_reading = 0
    def get_descriptive_name(self):
        '''返回简洁的描述信息'''
        long_name = str(self.year) + ' ' + self.make + ' ' + self.model
        return  long_name.title()
    def read_odometer(self):
        '''打印一条指出汽车里程消息'''
        print("This car has " + str(self.odometer_reading) + " miles on it")

my_new_car = Car('audi','A8',2019)
print(my_new_car.get_descriptive_name())
#直接访问属性
my_new_car.odometer_reading = 23
my_new_car.read_odometer()
