# -*- coding: UTF-8 -*-
#Author:Rivaill
#这是一个用于IP和域名碰撞匹配访问的小工具(多线程)
import itertools
import signal
import threading
from multiprocessing.dummy import Pool
from time import sleep
from requests.packages import chardet
import requests
import re
from lib.processbar import ProcessBar

def host_check(host_ip):
    host,ip = host_ip
    schemes = ["http://","https://"]
    for scheme in schemes:
        url = scheme+ip
        headers = {'Host':host.strip(),'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
        try:
            r = requests.session()
            requests.packages.urllib3.disable_warnings()
            res = r.get(url,verify=False,headers=headers,allow_redirects=False,timeout=30)
            charset = chardet.detect(res.content)["encoding"]
            res.encoding = charset
            title = ""
            try:
                title = re.search('<title>(.*)</title>', res.text).group(1) #获取标题
            except Exception as ex:
                title = "Failed to get title!"
            info = '%s,%s,%s,Packet size:%d,Title:%s' % (ip,host,scheme+host,len(res.text),title)
            if lock.acquire():
                try:
                    success_list.append(info)
                    pbar.echo(info)
                    pbar.update_suc()
                    with open('hosts_ok.txt','a+', encoding="utf-8") as f:
                        print(info + "\n")
                        f.write(info + "\n")
                        f.close()

                finally:
                    lock.release()

        except Exception as ex:
            if lock.acquire():
                try:
                    # print ex.message
                    # logging.exception(ex)
                    error = "%s,%s,%s,Access failed!" % (ip,host, scheme+host)
                    pbar.echo(error)
                finally:
                    lock.release()
        finally:
            pbar.update()



if __name__ == '__main__':
    lock = threading.Lock()
    success_list = []
    ip_list = open("ip.txt").read().splitlines()
    host_list = open("host.txt").read().splitlines()
    host_ip_list = list(itertools.product(host_list,ip_list))

    print("====================================Beginning====================================")

    pbar = ProcessBar(len(host_ip_list*2))

    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGINT, original_sigint_handler)

    pool = Pool(500)

    try:
        pool.map_async(host_check, host_ip_list)
        while not pbar.cur_cnt==pbar.total:
            sleep(10)

    except KeyboardInterrupt:
        pbar.echo("Ending the child thread...")
        pool.terminate()
        pool.close()

    else:
        pool.close()
        pool.join()

    pbar.close()


    print("====================================The end====================================")

