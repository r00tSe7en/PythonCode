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
        #给子类定义属性和方法
    def get_descriptive_name(self):
        '''返回简洁的描述信息'''
        long_name = str(self.year) + ' ' + self.make + ' ' + self.model
        return  long_name.title()
    def update_odometer(self,mileage):
        '''打印一条指出汽车里程消息'''
        self.odometer_reading = mileage
        print("This car has " + str(self.odometer_reading) + " miles on it")
class Battery():
    def __init__(self, battery_size=70):
        '''初始化电瓶的属性'''
        self.battery_size = battery_size
    def describe_battery(self):
        '''打印一条描述电瓶容量的消息'''
        print("This car has a " + str(self.battery_size) + "-kWh battery.")
class ElectricCar(Car):
    '''电动汽车的独特之处'''
    def __init__(self, make, model, year):
        super().__init__(make, model, year)
        self.battery = Battery()

my_tesla = ElectricCar('tesla', 'model s', 2019)
print(my_tesla.get_descriptive_name())
my_tesla.update_odometer(66)
my_tesla.battery.describe_battery()