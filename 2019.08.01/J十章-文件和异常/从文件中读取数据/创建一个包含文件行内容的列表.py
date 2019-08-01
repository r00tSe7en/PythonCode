#!/usr/bin/env python
#coding=utf-8
file_name = 'pi_digits.txt'
with open(file_name) as file_project:
    lines = file_project.readlines()
print(lines)
for line in lines:
    print(line.rstrip())