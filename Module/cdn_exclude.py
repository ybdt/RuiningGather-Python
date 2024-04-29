#!/usr/bin/env python3
# author: ybdt


# 导入官方库或第三方库
import subprocess
import threading
import queue


# 基于ping判断是否为cdn节点（云waf节点）
def exclude(q, non_cdn_ip_list, cdn_parse_record_filename):
    with open(cdn_parse_record_filename, "a") as fa:
        while True:
            if q.empty():
                return
            else:
                domain = q.get()
                domain = domain.strip("-")  # 经大量实践发现，收集到的域名会有-hideip.court.gov.cn这种情况，导致程序报错，需做处理

                # Mac
                p = subprocess.Popen(["/sbin/ping", "-c", "1", "-W", "1000", domain], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                ping_str = p.stdout.read()
                if ping_str == b"":
                    # print("Parse Error：   " + domain + "  " + "Ping请求找不到主机" + "\n")
                    fa.write("Parse Error：   " + domain + "  " + "Ping请求找不到主机" + "\n")
                    continue
                else:
                    ping_list = ping_str.decode("UTF-8").split("\n")
                    try:
                        ping_return_domain = ping_list[0].split(" ")[1]
                        ping_return_ip = ping_list[0].split(" ")[2].strip(":()")
                    except:
                        # print("格式异常的ping_list：   " + str(ping_list) + "，当前处理的域名是：" + domain)
                        fa.write("格式异常的ping_list：   " + str(ping_list) + "，当前处理的域名是：" + domain)
                        continue
                    if ping_return_domain == domain:
                        # print("Non CDN:   " + domain + "  " + ping_return_domain + "  " + ping_return_ip + "\n")
                        fa.write("Non CDN:   " + domain + "  " + ping_return_domain + "  " + ping_return_ip + "\n")
                        non_cdn_ip_list.append(ping_return_ip)
                    else:
                        # print("CDN:   " + domain + "  " + ping_return_domain + "  " + ping_return_ip + "\n")
                        fa.write("CDN:   " + domain + "  " + ping_return_domain + "  " + ping_return_ip + "\n")

                '''
                # Windows
                p = subprocess.Popen(["ping.exe", "-n", "1", "-w", "1000", domain], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                ping_str = p.stdout.read()
                # 后面的16进制字符串为："Ping 请求找不到主机"
                if ping_str.startswith(b"Ping request could not find host") or ping_str.startswith(b"Ping \xc7\xeb\xc7\xf3\xd5\xd2\xb2\xbb\xb5\xbd\xd6\xf7\xbb\xfa"):
                    non_parse_domain_list.append(domain + "__" + "ping请求找不到主机")
                    continue
                else:
                    ping_list = ping_str.decode("GBK").split("\r\n")
                    
                    # 不同输出格式，对应不同分片处理
                    # ['', '正在 Ping www.anicert.cn [39.96.183.255] 具有 32 字节的数据:', '请求超时。' ...
                    # ['', '正在 Ping appcube.anicert.cn [111.200.45.121] 具有 32 字节的数据:', '来自 111.200.45.121 的回复: 字节=32 时间=5ms TTL=128' ...
            
                    # 此处由于是对ping返回进行分片处理，经常容易报错，故添加异常处理，防止程序中断
                    try:
                        ping_return_domain = ping_list[1].split(" ")[2]
                        ping_return_ip = ping_list[1].split(" ")[3].strip("[]")
                    except:
                        print("格式异常的ping_list：" + str(ping_list) + "，当前处理的域名是：" + domain)
                        if ping_return_domain == domain:
                            non_cdn_domain_list.append(domain + "__" + ping_return_ip)
                            non_cdn_ip_list.append(ping_return_ip)
                        else:
                            cdn_domain_list.append(domain + "__" + ping_return_domain)
                '''


if __name__ == "__main__":
    # 测试代码
    sub_domain_list = ["www.jiachengnet.com", "www.baidu.com", "www.qq.com"]
    q = queue.Queue()
    for domain in sub_domain_list:
        q.put(domain)
    non_cdn_ip_list = []
    cdn_parse_record_filename = "cdn-parse-record.txt"
    threads_num = 25
    threads = []
    for i in range(threads_num):
        t = threading.Thread(target=exclude, args=(q, non_cdn_ip_list, cdn_parse_record_filename))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    print("non cdn ip list: " + str(non_cdn_ip_list))