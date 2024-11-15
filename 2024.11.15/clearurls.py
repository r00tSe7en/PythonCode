import re
from collections import defaultdict

def process_file(input_file, output_file):
    # 存储每个域名对应的端口集合
    domain_ports = defaultdict(set)
    urls = []

    # 正则表达式，用于匹配 http://xxx:port 或 https://xxx:port 格式
    url_pattern = re.compile(r'(https?://[a-zA-Z0-9.-]+)(?::(\d+))?')

    # 读取输入文件，逐行处理
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            line = line.strip()
            if line:
                match = url_pattern.match(line)
                if match:
                    domain = match.group(1)  # http://xxx 或 https://xxx
                    port = match.group(2)    # 端口号（如果存在）

                    # 统计每个域名对应的端口
                    if port:
                        domain_ports[domain].add(port)

                    # 保存原始的 URL
                    urls.append(line)

    # 处理 URLs，保留符合条件的域名
    final_urls = []
    for url in urls:
        match = url_pattern.match(url)
        if match:
            domain = match.group(1)
            port = match.group(2)

            # 如果没有端口号（即 url 中没有 :port 部分），直接保留该 URL
            if not port:
                final_urls.append(url)
            else:
                # 如果该域名对应的端口数大于等于10，只保留域名部分
                if len(domain_ports[domain]) >= 10:
                    final_urls.append(domain)
                else:
                    # 否则保留带端口的完整 URL
                    final_urls.append(url)

    # 去重：将 final_urls 转换为 set，再转换回 list
    final_urls = list(set(final_urls))

    # 将结果写入输出文件
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for final_url in final_urls:
            outfile.write(final_url + '\n')

    print(f"处理完成，结果已保存到 {output_file}")

# 调用示例
input_file = 'all_active_webs.txt'  # 输入文件名
output_file = 'processed_urls3.txt'  # 输出文件名
process_file(input_file, output_file)