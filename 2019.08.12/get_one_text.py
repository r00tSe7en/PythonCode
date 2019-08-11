#!/usr/bin/env python
#coding=utf-8
import os
txt_name = 'url.txt' #写入的目标文件
path = os.getcwd()+"\src" #获取文件夹路径
files_name = os.listdir(path) #创建文件夹下所有文件名称列表
f_write = open(txt_name,'a') #打开目标文件
for file_name in files_name:
    file = open(path+"\\"+file_name) #循环打开目录下的文件
    for url in file:
        if '\n' not in url: #判断上一个文件的结尾行，没有换行符则添加
            url += '\n'
        f_write.write(url) #吧文本行写入目标文件
print("Enjoy your url.txt!")
f_write.close()


