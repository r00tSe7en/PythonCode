#!/usr/bin/env python
#coding=utf-8
def describe_pet(animal_type = 'dog', pet_name = 'bob'):
    """显示宠物的信息"""
    print("\nI have a " + animal_type + ".")
    print("My " + animal_type + "'s name is " + pet_name.title() + ".")
describe_pet(animal_type='hamster')