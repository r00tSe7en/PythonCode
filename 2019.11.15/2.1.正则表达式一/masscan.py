#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Author:Se7en
#@Time:2019/11/14 22:46
import re
import csv
#import panda as pd
#import nump as np
#__name__ 等于文件名（包含后缀 .py ）
if __name__ == '__main__':
    #先打开一个csv文件
    with open("data.csv", "w", newline="") as datafile:
        writer = csv.writer(datafile)
        writer.writerow(["Address","Port"])
        #以读的方式打开mas.txt
        with open("mas.txt","r") as file :
            #把文件中所有的数据通过换行符切割，每一行成为一个元素，放置在列表里
            lines = file.readlines()
            #print(lines)
            ips = []
            for line in lines:
                #去除换行：去掉结尾的\n
                #print(line[:-2])
                # 匹配：(?:[0-9]{1,3}\.){3}前三位重复匹配，[0-9]{1,3}匹配最后一位
                ip = re.findall(r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}",line)#findall结果返回list
                #同行有相近的数据，采取前后匹配
                port = re.search(r"port \S*?/tcp",line)
                try:
                    #端口操作
                    portID = port.group()
                    #.split通过字符分割成列表
                    portINFO = portID.split(" ")
                    #print(portINFO[1])
                    #ip操作
                    #print(str(ip)[2:-2])
                    #print(ip[0])
                    ips.append(ip[0])
                    result = [ip[0],portINFO[1]]
                    writer = csv.writer(datafile)
                    writer.writerow(result)
                except:
                    pass
            print(ips)

