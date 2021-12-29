# -*- coding: UTF-8 -*-
import IPy
 
def ipToC():
    ips = set()
    readPath = 'ip.txt'
    writePath = 'ip_c.txt'
    outFile = open(writePath, 'w')
    with open(readPath, 'r') as f:
        for line in f:
            ip = line.strip('\n')
            ip_c = IPy.IP(ip).make_net('255.255.255.0')
            if ip_c not in ips:
                outFile.write(str(ip_c) + '\n')
                ips.add(ip_c)
    outFile.close()
    print('转换结束')
if __name__ == '__main__':
    ipToC()
