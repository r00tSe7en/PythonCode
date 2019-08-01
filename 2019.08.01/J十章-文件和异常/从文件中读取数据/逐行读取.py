#!/usr/bin/env python
#coding=utf-8
file_name = 'pi_digits.txt'
with open(file_name) as file_object:
    for line in file_object:
        print(line.rstrip())