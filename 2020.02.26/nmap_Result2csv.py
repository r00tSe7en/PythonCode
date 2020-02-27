#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Author:Se7en
#@Time:2020/2/26 17:06
import re
import csv
import sys

def getCsv(ips,ports):
    with open("nmap_result.csv", "w") as result_file:
        writer = csv.writer(result_file)
        flag = 0
        for ip in ips:
            writer.writerow([ips[flag]] + ports[flag])
            flag = flag + 1
    result_file.close()

def readTxt(txt_file):
    with open(txt_file, "r") as file:
        lines = file.readlines()  # 把文件中所有的数据通过换行符切割，每一行成为一个元素，放置在列表里
        ips = []  # 定义ip存放列表
        ports = []  # 定义port存放列表
        for line in lines:
            if ('Status: Up' not in line) and ('#' not in line):
                ip = re.findall(r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}", line)  # 匹配ip
                port = re.findall(r"([1-9]\d+\/.*?)\/{3}", line)  # 匹配port
                ips.append(ip[0])  # 存入ip进列表
                ports.append(port)
    file.close()
    return ips,ports

if __name__ == '__main__':
    try:
        readtxt = readTxt(sys.argv[1])
        getCsv(readtxt[0],readtxt[1])
        print("Enjoy your nmap_result.csv :)")
    except:
        print("Please input your nmap result text! \n E.g:nmap_Result2csv.py nmap_result.txt")