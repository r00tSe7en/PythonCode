#!/usr/bin/env python
#coding=utf-8
#首先创建一个未验证用户列表
#创建一个空列表来存储已验证用户
unconfirmed_users = ['alice','brian','candace']
confirmed_users = []
#验证每个用户，直到没有未验证用户为止
#将每个经过验证的列表都移动到已验证用户列表中
while unconfirmed_users:
    current_user = unconfirmed_users.pop()
    print("Verifing user:" + current_user.title())
    confirmed_users.append(current_user)
#显示所有已验证用户
for confirmed_users in confirmed_users:
    print(confirmed_users.title())
