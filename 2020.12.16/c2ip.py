# -*- coding: UTF-8 -*-
import IPy
 
def cTOip():
    ips = set()
    readPath = 'ip_c.txt'
    writePath = 'ip.txt'
    outFile = open(writePath, 'w')
    with open(readPath, 'r') as f:
        for line in f:
            ipc = line.strip('\n')
            ip = IPy.IP(ipc)
            for x in ip:
                if x not in ips:
                    outFile.write(str(x) + '\n')
                    ips.add(x)
    outFile.close()
    print("转换完成")
if __name__ == '__main__':
    cTOip()