#!/usr/bin/env python
#coding=utf-8
pizza = {
    'crust': 'thick',
    'toppings': ['mushrooms','extra cheese'],
}
print("you order " + pizza['crust'] + "-pizza with the following toppings:")
for topping in pizza['toppings']:
    print("\t"+topping)