#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Host碰撞工具 - 支持自定义路径、代理、重定向跟随、详细响应信息
用法: python host_collision.py -d domain.txt -i ip.txt -k "关键词" --path "/admin" --verbose
"""

import argparse
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib3.exceptions import InsecureRequestWarning
import sys
import os
from datetime import datetime
import ssl
import urllib3
from urllib.parse import urlparse, urljoin
import json

# 彻底禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 全局变量
success_results = []
all_results = []  # 存储所有检测结果（用于详细模式）
lock = threading.Lock()
total_tasks = 0
completed_tasks = 0
keyword = ""
proxy_config = None
verbose_mode = False  # 详细模式

def create_session(proxy=None):
    """创建忽略SSL证书错误的Session，支持代理"""
    session = requests.Session()
    
    # 设置代理
    if proxy:
        proxy_dict = {
            'http': proxy,
            'https': proxy
        }
        session.proxies.update(proxy_dict)
    
    # 方法1: 通过verify=False
    session.verify = False
    
    # 方法2: 设置适配器，忽略SSL错误
    from requests.adapters import HTTPAdapter
    from urllib3.poolmanager import PoolManager
    
    class SSLAdapter(HTTPAdapter):
        def init_poolmanager(self, *args, **kwargs):
            kwargs['cert_reqs'] = ssl.CERT_NONE
            kwargs['assert_hostname'] = False
            return super().init_poolmanager(*args, **kwargs)
    
    session.mount('https://', SSLAdapter())
    
    return session

def load_domains(domain_file):
    """加载域名列表"""
    domains = []
    try:
        with open(domain_file, 'r', encoding='utf-8') as f:
            for line in f:
                domain = line.strip()
                if domain and not domain.startswith('#'):
                    domains.append(domain)
    except FileNotFoundError:
        print(f"[!] 域名文件不存在: {domain_file}")
        sys.exit(1)
    return domains

def load_ips(ip_file):
    """加载IP列表"""
    ips = []
    try:
        with open(ip_file, 'r', encoding='utf-8') as f:
            for line in f:
                ip = line.strip()
                if ip and not ip.startswith('#'):
                    ips.append(ip)
    except FileNotFoundError:
        print(f"[!] IP文件不存在: {ip_file}")
        sys.exit(1)
    return ips

def get_response_summary(response):
    """获取响应摘要信息"""
    summary = {
        'status_code': response.status_code,
        'reason': response.reason,
        'content_length': len(response.content),
        'content_type': response.headers.get('Content-Type', 'Unknown'),
        'server': response.headers.get('Server', 'Unknown'),
        'response_time': response.elapsed.total_seconds()
    }
    return summary

def print_response_details(domain, ip, url, response, redirect_chain=None, is_match=False):
    """打印详细的响应信息"""
    print("\n" + "=" * 80)
    if is_match:
        print(f"[+] 匹配成功 - {domain} -> {ip}")
    else:
        print(f"[*] 请求详情 - {domain} -> {ip}")
    print("=" * 80)
    
    print(f"[请求信息]")
    print(f"  域名: {domain}")
    print(f"  IP地址: {ip}")
    print(f"  请求URL: {url}")
    print(f"  请求头: Host={domain}")
    
    print(f"\n[响应信息]")
    print(f"  状态码: {response.status_code} {response.reason}")
    print(f"  响应时间: {response.elapsed.total_seconds():.3f}秒")
    print(f"  内容长度: {len(response.content)} 字节")
    print(f"  内容类型: {response.headers.get('Content-Type', 'Unknown')}")
    print(f"  服务器: {response.headers.get('Server', 'Unknown')}")
    
    # 打印重要响应头
    important_headers = ['Location', 'Set-Cookie', 'X-Powered-By', 'X-Frame-Options']
    custom_headers = {k: v for k, v in response.headers.items() 
                      if k not in ['Content-Type', 'Server', 'Content-Length']}
    if custom_headers:
        print(f"  其他响应头:")
        for k, v in list(custom_headers.items())[:5]:  # 只显示前5个
            print(f"    {k}: {v[:100] if len(v) > 100 else v}")
    
    # 显示重定向信息
    if redirect_chain:
        print(f"\n[重定向链] (共{len(redirect_chain)}次)")
        for idx, redirect in enumerate(redirect_chain, 1):
            print(f"  {idx}. {redirect['status_code']} -> {redirect['location']}")
        if redirect_chain:
            print(f"  最终URL: {response.url}")
    
    # 显示响应内容预览
    content_preview = response.text[:500].replace('\n', ' ').replace('\r', '')
    print(f"\n[内容预览] (前500字符)")
    print(f"  {content_preview}...")
    
    # 关键词高亮显示
    if keyword and keyword.lower() in response.text.lower():
        print(f"\n[关键词匹配] 发现关键词 '{keyword}'")
        # 找出关键词出现的位置
        text_lower = response.text.lower()
        positions = []
        start = 0
        while True:
            pos = text_lower.find(keyword.lower(), start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        print(f"  出现次数: {len(positions)}")
        # 显示关键词周围的文本
        for pos in positions[:3]:  # 最多显示3处
            start_pos = max(0, pos - 50)
            end_pos = min(len(response.text), pos + len(keyword) + 50)
            context = response.text[start_pos:end_pos].replace('\n', ' ')
            print(f"  ...{context}...")
    
    print("-" * 80)

def follow_redirects(response, session, headers, depth=0, max_depth=5):
    """
    手动跟随重定向，记录完整的重定向链
    """
    redirect_chain = []
    current_response = response
    current_depth = depth
    
    while current_response.is_redirect and current_depth < max_depth:
        # 获取重定向URL
        redirect_url = current_response.headers.get('Location')
        if not redirect_url:
            break
            
        # 处理相对路径重定向
        if not redirect_url.startswith(('http://', 'https://')):
            redirect_url = urljoin(current_response.url, redirect_url)
        
        redirect_chain.append({
            'url': current_response.url,
            'status_code': current_response.status_code,
            'location': redirect_url
        })
        
        try:
            # 跟随重定向
            current_response = session.get(
                redirect_url,
                headers=headers,
                timeout=current_response.request.timeout,
                verify=False,
                allow_redirects=False
            )
            current_depth += 1
        except Exception:
            break
    
    return current_response, redirect_chain

def host_collision(domain, ip, keyword, timeout=5, port=443, proxy=None, 
                   follow_redirects_flag=True, max_redirects=10, path=""):
    """
    执行Host碰撞检测 - 支持自定义路径
    """
    global completed_tasks, total_tasks, verbose_mode
    
    # 为每个线程创建独立的session
    session = create_session(proxy)
    
    # 构造URL，添加自定义路径
    urls_to_try = []
    base_urls = []
    
    if port == 443:
        base_urls = [f"https://{ip}", f"http://{ip}"]
    elif port == 80:
        base_urls = [f"http://{ip}", f"https://{ip}"]
    else:
        base_urls = [f"https://{ip}:{port}", f"http://{ip}:{port}"]
    
    # 添加路径
    for base in base_urls:
        if path:
            # 确保路径格式正确
            if not path.startswith('/'):
                path = '/' + path
            urls_to_try.append(base + path)
        else:
            urls_to_try.append(base)
            # 也尝试常见的路径
            if verbose_mode:
                urls_to_try.append(base + '/')
    
    headers = {
        'Host': domain,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive'
    }
    
    try:
        # 尝试所有URL组合
        for url in urls_to_try:
            try:
                # 发起请求
                response = session.get(
                    url, 
                    headers=headers, 
                    timeout=timeout,
                    verify=False,
                    allow_redirects=False,
                    stream=False
                )
                
                final_response = response
                redirect_chain = []
                
                # 手动跟随重定向
                if follow_redirects_flag and response.status_code in [301, 302, 303, 307, 308]:
                    final_response, redirect_chain = follow_redirects(
                        response, session, headers, 0, max_redirects
                    )
                
                # 获取最终响应的内容
                response_text = final_response.text
                response_text_lower = response_text.lower()
                keyword_lower = keyword.lower()
                
                # 检查是否匹配关键词
                is_match = keyword_lower in response_text_lower
                
                # 获取响应摘要
                response_summary = get_response_summary(final_response)
                
                # 构建结果
                result = {
                    'domain': domain,
                    'ip': ip,
                    'url': url,
                    'path': path,
                    'status_code': final_response.status_code,
                    'status_reason': final_response.reason,
                    'response_time': final_response.elapsed.total_seconds(),
                    'is_redirect': len(redirect_chain) > 0,
                    'redirect_chain': redirect_chain,
                    'redirect_count': len(redirect_chain),
                    'final_url': final_response.url if len(redirect_chain) > 0 else url,
                    'content_length': len(response_text),
                    'content_type': response_summary['content_type'],
                    'server': response_summary['server'],
                    'content_preview': response_text[:500].replace('\n', ' ').replace('\r', ''),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'proxy': str(proxy) if proxy else '无',
                    'is_match': is_match
                }
                
                # 详细模式：打印每个请求的详细信息
                if verbose_mode:
                    with lock:
                        print_response_details(domain, ip, url, final_response, redirect_chain, is_match)
                
                # 如果匹配关键词，保存结果
                if is_match:
                    with lock:
                        success_results.append(result)
                        # 非详细模式下打印简洁结果
                        if not verbose_mode:
                            print(f"\n[+] 发现匹配!")
                            print(f"    域名: {domain}")
                            print(f"    IP: {ip}")
                            print(f"    URL: {url}")
                            print(f"    路径: {path if path else '/'}")
                            print(f"    状态码: {final_response.status_code}")
                            print(f"    响应时间: {final_response.elapsed.total_seconds():.3f}秒")
                            print(f"    内容长度: {len(response_text)} 字节")
                            if redirect_chain:
                                print(f"    重定向: {len(redirect_chain)}次 -> {final_response.url}")
                            print("-" * 60)
                    
                    session.close()
                    return result
                elif verbose_mode:
                    # 详细模式下也保存非匹配结果（可选）
                    with lock:
                        all_results.append(result)
                
                # 如果不是匹配结果且不是详细模式，继续
                    
            except requests.exceptions.Timeout:
                if verbose_mode:
                    with lock:
                        print(f"\n[!] 超时 [{domain} -> {ip}] {url}")
                continue
            except requests.exceptions.ConnectionError as e:
                if verbose_mode:
                    with lock:
                        print(f"\n[!] 连接错误 [{domain} -> {ip}] {url}: {str(e)[:100]}")
                continue
            except requests.exceptions.ProxyError as e:
                with lock:
                    print(f"\n[!] 代理错误 [{domain} -> {ip}]: {e}")
                continue
            except Exception as e:
                if verbose_mode:
                    with lock:
                        print(f"\n[!] 未知错误 [{domain} -> {ip}] {url}: {str(e)[:100]}")
                continue
                
    except Exception as e:
        pass
    finally:
        with lock:
            completed_tasks += 1
            # 显示进度
            if completed_tasks % 50 == 0 or completed_tasks == total_tasks:
                progress = (completed_tasks / total_tasks) * 100
                print(f"\r[*] 进度: {completed_tasks}/{total_tasks} ({progress:.1f}%)", end='', flush=True)
        session.close()
    
    return None

def save_results(output_file):
    """保存结果到文件"""
    if not success_results:
        print("\n[-] 未发现匹配的结果")
        # 如果详细模式且有所有结果，询问是否保存
        if verbose_mode and all_results:
            print(f"[*] 详细模式下共检测 {len(all_results)} 个请求，但无匹配关键词")
        return
    
    try:
        # 保存文本格式
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Host碰撞结果\n")
            f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 匹配关键词: {keyword}\n")
            f.write(f"# 共发现 {len(success_results)} 个匹配\n")
            f.write(f"# SSL证书验证: 已禁用\n")
            if proxy_config:
                f.write(f"# 代理设置: {proxy_config}\n")
            f.write("# 重定向跟随: 已启用\n")
            f.write("\n")
            
            for idx, result in enumerate(success_results, 1):
                f.write(f"[{idx}] 检测结果\n")
                f.write(f"域名: {result['domain']}\n")
                f.write(f"IP地址: {result['ip']}\n")
                f.write(f"请求路径: {result['path'] if result['path'] else '/'}\n")
                f.write(f"初始URL: {result['url']}\n")
                f.write(f"响应时间: {result['response_time']:.3f}秒\n")
                
                if result.get('is_redirect'):
                    f.write(f"是否重定向: 是 (共 {result['redirect_count']} 次)\n")
                    f.write(f"重定向链:\n")
                    for r_idx, redirect in enumerate(result['redirect_chain'], 1):
                        f.write(f"  {r_idx}. {redirect['status_code']} -> {redirect['location']}\n")
                    f.write(f"最终URL: {result['final_url']}\n")
                    f.write(f"最终状态码: {result['status_code']} {result.get('status_reason', '')}\n")
                else:
                    f.write(f"访问URL: {result['url']}\n")
                    f.write(f"HTTP状态码: {result['status_code']} {result.get('status_reason', '')}\n")
                
                f.write(f"响应大小: {result['content_length']} 字节\n")
                f.write(f"内容类型: {result['content_type']}\n")
                f.write(f"服务器: {result['server']}\n")
                f.write(f"检测时间: {result['timestamp']}\n")
                if result.get('proxy'):
                    f.write(f"代理: {result['proxy']}\n")
                f.write(f"内容预览:\n{result['content_preview']}\n")
                f.write("=" * 60 + "\n\n")
        
        # 保存JSON格式（可选）
        json_file = output_file.replace('.txt', '_detailed.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(success_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n\n[+] 结果已保存到:")
        print(f"    文本格式: {output_file}")
        print(f"    JSON格式: {json_file}")
        print(f"[+] 共保存 {len(success_results)} 条匹配记录")
        
    except Exception as e:
        print(f"\n[-] 保存结果失败: {e}")

def test_proxy(proxy):
    """测试代理是否可用"""
    print(f"[*] 测试代理连接: {proxy}")
    try:
        test_session = create_session(proxy)
        response = test_session.get('https://httpbin.org/ip', timeout=10, verify=False)
        if response.status_code == 200:
            print(f"[+] 代理测试成功！")
            print(f"[+] 代理IP: {response.json().get('origin', 'Unknown')}")
            return True
        else:
            print(f"[!] 代理测试失败: HTTP状态码 {response.status_code}")
            return False
    except requests.exceptions.ProxyError as e:
        print(f"[!] 代理连接失败: {e}")
        return False
    except Exception as e:
        print(f"[!] 代理测试异常: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Host碰撞检测工具 - 支持自定义路径、代理、重定向跟随、详细响应信息',
        epilog='示例: python host_collision.py -d domain.txt -i ip.txt -k "admin" --path "/admin/login" --verbose'
    )
    parser.add_argument('-d', '--domain', required=True, help='域名列表文件 (domain.txt)')
    parser.add_argument('-i', '--ip', required=True, help='IP列表文件 (ip.txt)')
    parser.add_argument('-k', '--keyword', required=True, help='匹配关键词')
    parser.add_argument('--path', default='', help='自定义请求路径 (例如: /admin, /api/v1, /login.php)')
    parser.add_argument('-t', '--threads', type=int, default=50, help='线程数 (默认: 50)')
    parser.add_argument('-o', '--output', default='success.txt', help='输出文件 (默认: success.txt)')
    parser.add_argument('--timeout', type=int, default=5, help='请求超时时间(秒) (默认: 5)')
    parser.add_argument('--port', type=int, default=443, help='端口号 (默认: 443)')
    parser.add_argument('--no-http', action='store_true', help='不尝试HTTP连接')
    parser.add_argument('-p', '--proxy', help='代理服务器 (格式: http://user:pass@host:port)')
    parser.add_argument('--test-proxy', action='store_true', help='测试代理是否可用')
    parser.add_argument('--no-follow-redirects', action='store_true', help='不跟随301/302重定向')
    parser.add_argument('--max-redirects', type=int, default=10, help='最大重定向次数 (默认: 10)')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细模式 - 打印每个请求的完整响应信息')
    
    global keyword, total_tasks, proxy_config, verbose_mode
    
    args = parser.parse_args()
    keyword = args.keyword
    proxy_config = args.proxy
    verbose_mode = args.verbose
    
    # 测试代理（如果指定）
    if args.proxy and args.test_proxy:
        if not test_proxy(args.proxy):
            print("[!] 代理测试失败，是否继续？(y/n)")
            choice = input().strip().lower()
            if choice != 'y':
                sys.exit(1)
    
    print("=" * 80)
    print("Host碰撞检测工具 v5.0 - 支持自定义路径、代理、重定向跟随、详细响应信息")
    print("=" * 80)
    print(f"[*] SSL证书验证: 已禁用")
    if args.proxy:
        print(f"[*] 代理服务器: {args.proxy}")
    if not args.no_follow_redirects:
        print(f"[*] 重定向跟随: 已启用 (最大 {args.max_redirects} 次)")
    else:
        print(f"[*] 重定向跟随: 已禁用")
    if args.path:
        print(f"[*] 自定义路径: {args.path}")
    if args.verbose:
        print(f"[*] 详细模式: 已启用 (将打印每个请求的详细信息)")
    
    # 加载域名和IP
    print(f"[*] 加载域名列表: {args.domain}")
    domains = load_domains(args.domain)
    print(f"[*] 共加载 {len(domains)} 个域名")
    
    print(f"[*] 加载IP列表: {args.ip}")
    ips = load_ips(args.ip)
    print(f"[*] 共加载 {len(ips)} 个IP")
    
    # 计算总任务数
    total_tasks = len(domains) * len(ips)
    print(f"[*] 总共需要检测: {total_tasks} 个组合")
    print(f"[*] 匹配关键词: {keyword}")
    print(f"[*] 线程数: {args.threads}")
    print(f"[*] 超时时间: {args.timeout}秒")
    print(f"[*] 目标端口: {args.port}")
    if not args.no_http:
        print(f"[*] 协议: HTTPS + HTTP")
    else:
        print(f"[*] 协议: 仅HTTPS")
    print("=" * 80)
    print("[*] 开始检测...\n")
    
    # 使用线程池执行检测
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {}
        for domain in domains:
            for ip in ips:
                future = executor.submit(
                    host_collision, 
                    domain, 
                    ip, 
                    keyword, 
                    args.timeout, 
                    args.port,
                    args.proxy,
                    not args.no_follow_redirects,
                    args.max_redirects,
                    args.path
                )
                futures[future] = (domain, ip)
        
        # 等待所有任务完成
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                if verbose_mode:
                    print(f"\n[!] 任务异常: {e}")
                pass
    
    # 保存结果
    print("\n" + "=" * 80)
    save_results(args.output)
    print(f"[*] 检测完成！共发现 {len(success_results)} 个匹配结果")
    if verbose_mode and all_results:
        print(f"[*] 详细模式: 共发送 {len(all_results)} 个请求")
    print("=" * 80)

if __name__ == "__main__":
    main()
