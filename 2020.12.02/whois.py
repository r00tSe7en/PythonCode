import requests
import re
from requests.packages import urllib3

urllib3.disable_warnings()
domains = []
def GetDomain():
    with open('url.txt','r',encoding='utf-8') as f:
        url = f.readlines()
        for domain in url:
            domains.append(domain.strip())
    f.close()
def GetInfo():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36', 'Accept-Encoding': 'gzip, deflate, br'
}
    for domain in domains:
        url = 'https://whois.aite.xyz/?ajax&client&domain='+domain
        print("-----------------------------------------------------")
        print(domain)
        try:
            req = requests.get(url, headers = headers, timeout=50, verify=False)
            print("Registrar URL: "+(re.findall(r'Registrar URL: (.*?)\s',req.text))[0])
            print("Registrar Abuse Contact Email: "+(re.findall(r'Registrar Abuse Contact Email: (.*?)\s',req.text))[0])
            print("-----------------------------------------------------")
        except:
            print(domain+"查询失败")
            print("-----------------------------------------------------")
if __name__ == '__main__':
    GetDomain()
    GetInfo()