#!/usr/bin/env python
#coding=utf-8
def make_pizza(*toppings):
    '''打印顾客点的所有的配料'''
    print(toppings)
make_pizza('pepperoin')
make_pizza('mushroom','onion','cheese')