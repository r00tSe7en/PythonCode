#!/usr/bin/env python
#coding=utf-8
def describe_pet(animal_type = 'dog', pet_name = 'bob'):
    """显示宠物的信息"""
    return animal_type.title(),pet_name.title()
print(describe_pet(animal_type = 'hamster',pet_name = 'harry'))