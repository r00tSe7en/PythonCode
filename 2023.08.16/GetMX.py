
import dns.resolver

def query_mx_records(domain):
    print('# '+domain)
    try:
        # 查询MX记录
        mx_records = dns.resolver.resolve(domain, 'MX')
        
        # 打印MX记录
        for record in mx_records:
            print(f"MX: {record.exchange}，优先级: {record.preference}")
    except dns.resolver.NXDOMAIN:
        print("域名不存在")
    except dns.resolver.NoAnswer:
        print("未找到MX记录")
    except dns.exception.Timeout:
        print("查询超时")
    print('---')



# 打开文本文件
file = open("rootdomain.txt", "r")

# 遍历文件的每一行
for line in file:
    # 在这里执行你的操作，比如打印每一行的内容
    line = line.strip()
    # 调用函数查询MX记录
    query_mx_records(line)

# 关闭文件
file.close()