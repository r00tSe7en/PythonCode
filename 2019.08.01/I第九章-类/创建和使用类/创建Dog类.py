#!/usr/bin/env python
#coding=utf-8
class Dog():
    '''一次模拟小狗的简单尝试'''
    def __init__(self, name, age):
        '''初始化属性name和age'''
        self.name = name
        self.age = age
    def sit(self):
        '''模拟小狗被命令时蹲下'''
        print(self.name.title() + " is now sotting!")
    def roll_over(self):
        '''模拟小狗被命令时打滚'''
        print(self.name.title() + " rolled over!")

my_dog = Dog('willie', 6)
#访问实例的属性
print("My dog's name is " + my_dog.name.title() + ".")
print("My dog is " + str(my_dog.age) + " years old.")
#调用方法
my_dog.sit()
my_dog.roll_over()

#创建多个实例
your_dog = Dog('BOB',8)
your_dog.sit()
your_dog.roll_over()

