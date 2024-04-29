#!/usr/bin/env python3
# author: ybdt


import argparse
import time
import os
import sys
import threading
import queue
from colorama import Fore, Style
import ipaddress
import pandas as pd
from CyberSpace import fofa
from CyberSpace import hunter
from CyberSpace import quake
from CyberSpace import zoomeye
from CyberSpace import shodan_search
from CyberSpace import censys_search
from Module import cdn_exclude
from Module import serial_ip
from Module import oneforall
from Module import wafw00f
from Module import httpx
from Module import http_code


# 判断ip地址是否合法
def isIpaddress(ip_str):
    try:
        ipaddress.ip_address(ip_str)
        return True
    except:
        return False


# 对ip进行查询
def ipGather(ip_list):
    non_cdn_ip_list = []  #定义非cdn ip列表
    cdn_ip_list = []  #定义cdn ip列表
    http_url_list = []  #定义http url列表

    if ip_list == []:
        return [], [], "service-0.txt"
    else:
        for ip in ip_list:
            try:
                if ipaddress.ip_address(ip).is_private:
                    with open("internal-ip.txt", "a", encoding="utf-8") as fr:
                        fr.write(ip + "\n")
                else:
                    ip, port_list = censys_search.ipGather(ip)
                    time.sleep(1)
                    if len(port_list) > 50:  # 如果一个IP开放超过50个端口，则认为他是CDN节点
                        print("当前IP：{}开放端口超过50个，认为是CDN节点，跳到下一个".format(ip))
                        cdn_ip_list.append(ip)
                        continue
                    else:
                        non_cdn_ip_list.append(ip)
                        port_list = list(dict.fromkeys(port_list))
                        print("经Censys查询，{} ：{}".format(ip, port_list))
                        with open("service.txt", "a") as fa:
                            if 21 in port_list:
                                port_list.remove(21)
                                fa.write(ip + ":" + str(21) + "\n")
                            if 22 in port_list:
                                port_list.remove(22)
                                fa.write(ip + ":" + str(22) + "\n")
                            elif 23 in port_list:
                                port_list.remove(23)
                                fa.write(ip + ":" + str(23) + "\n")
                            elif 3389 in port_list:
                                port_list.remove(3389)
                                fa.write(ip + ":" + str(3389) + "\n")
                            elif 3306 in port_list:
                                port_list.remove(3306)
                                fa.write(ip + ":" + str(3306) + "\n")
                            elif 1433 in port_list:
                                port_list.remove(1433)
                                fa.write(ip + ":" + str(1433) + "\n")
                            elif 1521 in port_list:
                                port_list.remove(1521)
                                fa.write(ip + ":" + str(1521) + "\n")
                            elif 5432 in port_list:
                                port_list.remove(5432)
                                fa.write(ip + ":" + str(5432) + "\n")
                            elif 6379 in port_list:
                                port_list.remove(6379)
                                fa.write(ip + ":" + str(6379) + "\n")
                            elif 11211 in port_list:
                                port_list.remove(11211)
                                fa.write(ip + ":" + str(11211) + "\n")
                            elif 27017 in port_list:
                                port_list.remove(27017)
                                fa.write(ip + ":" + str(27017) + "\n")
                            elif 25 in port_list:
                                port_list.remove(25)
                                fa.write(ip + ":" + str(25) + "\n")
                            elif 110 in port_list:
                                port_list.remove(110)
                                fa.write(ip + ":" + str(110) + "\n")
                            elif 143 in port_list:
                                port_list.remove(143)
                                fa.write(ip + ":" + str(143) + "\n")
                        for port in port_list:
                            http_url = "http://" + ip + ":" + str(port)
                            http_url_list.append(http_url)
            except Exception as e:
                print("ip {} 发生异常：{}".format(ip, e))
                continue

        with open("service.txt", "r") as fr:
            lines = fr.readlines()
        service_filename = "service-{}.txt".format(len(lines))
        os.rename("service.txt", service_filename)

        if os.path.exists("internal-ip.txt"):  #当internal-ip.txt存在时，重命名它
            with open("internal-ip.txt", "r") as fr:
                lines = fr.readlines()
            internal_ip_filename = "internal-ip-{}.txt".format(str(len(lines)))
            os.rename("internal-ip.txt", internal_ip_filename)
        else:  #当internal-ip.txt不存在时，创建一个空文件
            internal_ip_filename = "internal-ip-0.txt"
            with open("internal-ip-0.txt", "w") as fr:
                pass

        return http_url_list, non_cdn_ip_list, cdn_ip_list, service_filename, internal_ip_filename


# 提取domain并写入文件
def domainExtractor(final_url_list):
    sub_domain_list = []
    for url in final_url_list:
        try:
            domain = url.strip("http://").strip("https://")
            if ":" in domain:
                index_p = domain.index(":")
                domain = domain[:index_p]
                sub_domain_list.append(domain)
            else:
                sub_domain_list.append(domain)
        except:
            print("当前目标 {} 发生异常".format(url))
            continue
    sub_domain_list = list(dict.fromkeys(sub_domain_list))
    count = str(len(sub_domain_list))
    final_domain_filename = "domain-{}.txt".format(count)
    with open(final_domain_filename, "w", encoding="UTF-8") as fw_domain:
        for domain in sub_domain_list:
            fw_domain.write(domain + "\n")
    return sub_domain_list, final_domain_filename


# 列表比较及合并
def diff(new_list, old_final_list):
    diff_list = []
    for i in new_list:
        if i in old_final_list:
            continue
        else:
            diff_list.append(i)
    final_list = old_final_list + diff_list
    return diff_list, final_list


# 对多个根域名进行查询
def domainGather(root_domain_list, ip_list, output_dir_name, oneforall_flag, oneforall_path, oneforall_domain_file_path,
                 oneforall_results_path, oneforall_bak_results_path, cdn_flag, serial_flag, filter_flag, waf_flag, wafw00f_path):

    # 定义2个空列表，用于保存url和ip
    final_url_list = []
    final_ip_list = []
    
    # 调用空间测绘
    for domain in root_domain_list:
        fofa_search_keyword = 'domain="{}"'.format(domain)
        hunter_search_keyword = 'domain.suffix="{}"'.format(domain)
        # quake_search_keyword = 'domain:"{}"'.format(domain)
        # zoomeye_search_keyword = 'q={}'.format(domain)
        # shodan_search_keyword = 'hostname:{}'.format(domain)

        fofa_filename = "fofa-" + output_dir_name
        fofa_url_list_, fofa_ip_list_, fofa_csv_data = fofa.domainGather(fofa_search_keyword, fofa_filename)
        final_url_list += fofa_url_list_
        final_ip_list += fofa_ip_list_

        time.sleep(3)  # 不间隔的话，会返回代码429，提示请求太多，经测试间隔1秒不够，增加为3秒
        hunter_url_list_, hunter_ip_list_, hunter_csv_data = hunter.hunterGather(hunter_search_keyword)
        diff_url_list, final_url_list = diff(hunter_url_list_, final_url_list)
        diff_ip_list, final_ip_list = diff(hunter_ip_list_, final_ip_list)
        # hunter_df = pd.DataFrame(hunter_csv_data)
        # hunter_df.to_csv(tmp_csv_filename, mode="a", header=False, index=False)

        # quake_filename = "quake-" + output_dir_name
        # quake_url_list_, quake_ip_list_, quake_csv_data = quake.domainGather(quake_search_keyword, quake_filename)
        # diff_url_list, final_url_list = diff(quake_url_list_, final_url_list)
        # diff_ip_list, final_ip_list = diff(quake_ip_list_, final_ip_list)
        # quake_df = pd.DataFrame(quake_csv_data)
        # quake_df.to_csv(tmp_csv_filename, mode="a", header=False, index=False)

        # zoomeye_url_list_, zoomeye_ip_list_ = zoomeye.domainGather(zoomeye_search_keyword)
        # diff_url_list, final_url_list = diff(zoomeye_url_list_, final_url_list)
        # diff_ip_list, final_ip_list = diff(zoomeye_ip_list_, final_ip_list)

        # shodan_url_list_, shodan_ip_list_ = shodan_search.domainGather(shodan_search_keyword)
        # diff_url_list, final_url_list = diff(shodan_url_list_, final_url_list)
        # diff_ip_list, final_ip_list = diff(shodan_ip_list_, final_ip_list)

    # 调用oneforall
    if oneforall_flag:
        # print()
        # os.system("read -p '下面开始调用OneForAll，OneForAll中好多接口需要翻墙，请选择是否开启Proxifier（注意：开启Proxifier后不能收集到真实IP）' var")  # mac下
        # print("下面开始调用OneForAll，OneForAll中好多接口需要翻墙，请选择是否开启Proxifier（注意：开启Proxifier后不能收集到真实IP）")  # windows下
        # os.system("pause")  # windows下
        oneforall_url_list_, oneforall_ip_list_ = oneforall.oneforall_gather(oneforall_path, oneforall_domain_file_path,
                                                                             oneforall_results_path, oneforall_bak_results_path)
        oneforall_url_list = list(set(oneforall_url_list_))
        oneforall_ip_list = list(set(oneforall_ip_list_))
        print()
        print("OneForAll共收集到URL {}条，去重后 {}条".format(len(oneforall_url_list_), len(oneforall_url_list)))
        print("OneForAll共收集到IP {}条，去重后 {}条".format(len(oneforall_ip_list_), len(oneforall_ip_list)))
        diff_url_list, final_url_list = diff(oneforall_url_list, final_url_list)
        diff_ip_list, final_ip_list = diff(oneforall_ip_list, final_ip_list)
        print(Fore.RED + "OneForAll多收集到URL {}条，OneForAll多收集到IP {}条".format(len(diff_url_list), len(diff_ip_list))
              + Style.RESET_ALL)
        # print()
        # os.system("read -p 'OneForAll调用完毕，若开启Proxifier请关闭' var")  # mac下
        # print("OneForAll调用完毕，若开启Proxifier请关闭")  # windows下
        # os.system("pause")  # windows下
        # print()

    # 提取子域名并写入文件
    sub_domain_list, final_domain_filename = domainExtractor(final_url_list)

    # 此处输出收集到的url、子域名，保证后面即使报错，也能有资产，不至于什么都没有
    final_url_filename = "temp-url-{}.txt".format(str(len(final_url_list)))
    with open(final_url_filename, "w") as fw:
        for i in final_url_list:
            try:
                fw.write(i + "\n")
            except:
                print(("当前url {} 发生异常".format(i)))
                continue

    print()
    print(Fore.YELLOW + "Final Domain输出到文件：{}".format(final_domain_filename) + Style.RESET_ALL)
    print(Fore.YELLOW + "Temp URL输出到文件：{}".format(final_url_filename) + Style.RESET_ALL)

    # 检测cdn
    non_cdn_ip_list = []
    cdn_parse_record_filename = "cdn-parse-record.txt"
    if cdn_flag:
        print()
        print(Fore.BLUE + "正在检测以下子域名是否为CDN节点或云WAF节点..." + Style.RESET_ALL)
        print(sub_domain_list)
        q = queue.Queue()
        for domain in sub_domain_list:
            q.put(domain)
        thread_num = 25
        threads = []
        for i in range(thread_num):
            t = threading.Thread(target=cdn_exclude.exclude, args=(q, non_cdn_ip_list, cdn_parse_record_filename))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        non_cdn_ip_list = list(set(non_cdn_ip_list))
        final_ip_list += non_cdn_ip_list

    # 获取连续ip
    if serial_flag:
        non_cdn_serial_ip_list = serial_ip.ipSerial(non_cdn_ip_list)
        print()
        print(Fore.BLUE + "连续IP如下：" + Style.RESET_ALL)
        print(non_cdn_serial_ip_list)
        final_ip_list += non_cdn_serial_ip_list

    # 汇总收集到的ip并输出
    non_cdn_ip_list = final_ip_list + ip_list
    print()
    print(Fore.BLUE + "共收集到非CDN IP：{}个，如下所示：".format(str(len(non_cdn_ip_list))) + Style.RESET_ALL)
    print(non_cdn_ip_list)
    print()

    # 查询ip开放的端口，挑出常见服务端口，其他端口和ip构建新的url
    http_url_list, non_cdn_ip_list, cdn_ip_list, service_filename, internal_ip_filename = ipGather(non_cdn_ip_list)
    diff_url_list, final_url_list = diff(http_url_list, final_url_list)
    print(Fore.GREEN + "查询IP开放端口后，挑出常见服务端口，多收集到URL：{}条".format(len(diff_url_list)) + Style.RESET_ALL)
    print()
    print(Fore.GREEN + "共收集到URL：{}条".format((len(root_domain_list) + len(ip_list)),
                                                               len(final_url_list)) + Style.RESET_ALL)

    # 此处输出收集到的url、子域名和ip，保证后面即使报错，也能有资产，不至于什么都没有
    final_url_filename = "url-{}.txt".format(str(len(final_url_list)))
    with open(final_url_filename, "w") as fw:
        for i in final_url_list:
            try:
                fw.write(i + "\n")
            except:
                print(("当前url {} 发生异常".format(i)))
                continue
    print(Fore.GREEN + "URL输出到文件：{}".format(final_url_filename) + Style.RESET_ALL)
    non_cdn_ip_filename = "ip-{}.txt".format(len(non_cdn_ip_list))
    with open(non_cdn_ip_filename, "w", encoding="UTF-8") as fw:
        for ip in non_cdn_ip_list:
            try:
                fw.write(ip + "\n")
            except:
                print(("当前ip {} 发生异常".format(ip)))
                continue
    print(Fore.GREEN + "非CDN IP输出到文件：{}".format(non_cdn_ip_filename) + Style.RESET_ALL)
    cdn_ip_filename = "cdn-ip-{}.txt".format(len(cdn_ip_list))
    with open(cdn_ip_filename, "w", encoding="UTF-8") as fw:
        for ip in cdn_ip_list:
            try:
                fw.write(ip + "\n")
            except:
                print(("当前ip {} 发生异常".format(ip)))
                continue
    print(Fore.GREEN + "CND IP输出到文件：{}".format(cdn_ip_filename) + Style.RESET_ALL)
    print(Fore.GREEN + "Service输出到文件：{}".format(service_filename) + Style.RESET_ALL)
    print(Fore.GREEN + "Internal IP输出到文件：{}".format(internal_ip_filename) + Style.RESET_ALL)
    # print(Fore.YELLOW + "概述信息输出到：{}".format(final_csv_filename) + Style.RESET_ALL)

    '''
    # 调用httpx，将url列表写入临时文件，并对临时文件中的url进行存活检测，最后删除临时文件
    if httpx_flag:
        httpx.alive_detect(httpx_path, final_url_filename)
        with open("url-alive.txt", "r") as fr:
            lines = fr.readlines()
        alive_url_name = "url-alive-{}.txt".format(str(len(lines)))
        os.rename("url-alive.txt", alive_url_name)
        print(Fore.GREEN + "经Httpx检测，存活URL：{}条，输出到文件：{}".format(str(len(lines)), alive_url_name) + Style.RESET_ALL)
    '''

    # 对url进行过滤
    if filter_flag:
        print()
        print(Fore.GREEN + "基于HTTP响应码对URL进行筛选" + Style.RESET_ALL)
        with open(final_url_filename, "r") as fr:
            lines = fr.readlines()
        lines = list(dict.fromkeys(lines))
        q = queue.Queue()
        for line in lines:
            line = line.strip("\n")
            q.put(line)
        alive_url_list = []
        dead_url_list = []
        alive_url_with_code_200_list = []
        alive_url_with_other_code_list = []
        threads_num = 30
        threads = []
        for i in range(threads_num):
            t = threading.Thread(target=http_code.get_code, args=(q, alive_url_list, dead_url_list,
                                 alive_url_with_code_200_list, alive_url_with_other_code_list))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        alive_url_filename = "alive-url-{}.txt".format(len(alive_url_list))
        with open(alive_url_filename, "w") as fw:
            for i in alive_url_list:
                fw.write(i + "\n")
        dead_url_filename = "deal-url-{}.txt".format(len(dead_url_list))
        with open(dead_url_filename, "w") as fw:
            for i in dead_url_list:
                fw.write(i + "\n")
        alive_url_with_code_200_filename = "alive-url-with-code_200-{}.txt".format(len(alive_url_with_code_200_list))
        with open(alive_url_with_code_200_filename, "w") as fw:
            for i in alive_url_with_code_200_list:
                fw.write(i + "\n")
        alive_url_with_other_code_filename = "alive-url-with-other_code-{}.txt".format(len(alive_url_with_other_code_list))
        with open(alive_url_with_other_code_filename, "w") as fw:
            for i in alive_url_with_other_code_list:
                fw.write(i + "\n")
        print(Fore.GREEN + "Alive URL输出到文件：{}".format(alive_url_filename) + Style.RESET_ALL)
        print(Fore.GREEN + "Dead URL输出到文件：{}".format(dead_url_filename) + Style.RESET_ALL)
        print(Fore.GREEN + "Alive URL With Code 200输出到文件：{}".format(alive_url_with_code_200_filename) + Style.RESET_ALL)
        print(Fore.GREEN + "Alive URL With Other Code输出到文件：{}".format(alive_url_with_other_code_filename) + Style.RESET_ALL)

    # 调用wafw00f对url进行waf检测
    if waf_flag:
        print()
        print('''
                    ______
                   /      \
                  (  W00f! )
                   \  ____/
                   ,,    __            404 Hack Not Found
               |`-.__   / /                      __     __
               /"  _/  /_/                       \ \   / /
              *===*    /                          \ \_/ /  405 Not Allowed
             /     )__//                           \   /
        /|  /     /---`                        403 Forbidden
        \\/`   \ |                                 / _ \
        `\    /_\\_              502 Bad Gateway  / / \ \  500 Internal Error
          `_____``-`                             /_/   \_\

                            ~ WAFW00F : v2.2.0 ~
            The Web Application Firewall Fingerprinting Toolkit
        ''')
        q = queue.Queue()
        with open(alive_url_filename, "r", encoding="UTF-8") as fr:
            with open("url-alive-without-waf.txt", "w", encoding="UTF-8") as fw1:
                with open("url-alive-with-waf.txt", "w", encoding="UTF-8") as fw2:
                    lines = fr.readlines()
                    for line in lines:
                        line = line.strip("\n")
                        # print(line)
                        q.put(line)
                    threads_num = 30
                    threads = []
                    no_waf_list = []
                    other_list = []
                    for i in range(threads_num):
                        t = threading.Thread(target=wafw00f.waf_detect,
                                             args=(q, no_waf_list, other_list, wafw00f_path))
                        threads.append(t)
                        t.start()
                    for t in threads:
                        t.join()
                    for each in no_waf_list:
                        fw1.write(each + "\n")
                    for each in other_list:
                        fw2.write(each + "\n")
        with open("url-alive-without-waf.txt", "r") as fr:
            lines = fr.readlines()
        alive_non_waf_name = "url-alive-without-waf-{}.txt".format(str(len(lines)))
        os.rename("url-alive-without-waf.txt", alive_non_waf_name)
        with open("url-alive-with-waf.txt", "r") as fr:
            lines = fr.readlines()
        alive_waf_name = "url-alive-with-waf-{}".format(str(len(lines)))
        os.rename("url-alive-with-waf.txt", alive_waf_name)
        print(Fore.GREEN + "Alive URL With WAF输出到文件：{}".format(alive_waf_name) + Style.RESET_ALL)
        print(Fore.GREEN + "Alive URL Without WAF输出到文件：{}".format(alive_non_waf_name) + Style.RESET_ALL)


def usage():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", dest="file_name", type=str,
                        help="包含根域名和ip的文件，每行一个，例如：python3 Ruining-Gather.py -f 测试.txt", required=False)
    parser.add_argument("-o", "--oneforall", dest="oneforall_flag", type=bool,
                        help="是否调用oneforall，不调用无需指定，调用例如：-o ture", default=False, required=False)
    parser.add_argument("-c", "--cdn", dest="cdn_flag", type=bool,
                        help="是否检测cdn，不调用无需指定，调用例如：-c ture", default=False, required=False)
    parser.add_argument("-s", "--serial", dest="serial_flag", type=bool,
                        help="是否获取连续ip，不调用无需指定，调用例如：-s ture", default=False, required=False)
    # parser.add_argument("-httpx", dest="httpx_flag", type=bool,
    # help="是否调用httpx，例如：-httpx ture，不调用无需指定", default=False, required=False)
    parser.add_argument("-t", "--filter", dest="filter_flag", type=bool,
                        help="是否过滤url，不调用无需指定，调用例如：-t ture", default=False, required=False)
    parser.add_argument("-w", "--waf", dest="waf_flag", type=bool,
                        help="是否检测waf，不调用无需指定，调用例如：-w ture", default=False, required=False)

    args = parser.parse_args()
    if args.file_name is not None:
        return args.file_name, args.oneforall_flag, args.cdn_flag, args.serial_flag, args.filter_flag, args.waf_flag
    else:
        sys.exit("查看帮助：python3 Ruining-Gather.py -h")


def banner():
    print()
    print()
    print('''
    ******************************************************************************************************
    红队Web打点--资产收集
    
    工具： FOFA | Hunter| OneForAll | CDN Detect | Censys | Serial IP | URL Filter | Wafw00f
    
    Author: ybdt
    ******************************************************************************************************
    ''')
    print()
    print()


def main():
    # 输出banner
    banner()

    # 获取传入信息
    filename, oneforall_flag, cdn_flag, serial_flag, filter_flag, waf_flag = usage()

    os.system("read -p '为防止程序报错，请先检查Clash是否开启全局代理，若开启会导致censys不可用，需关闭' var")

    # 获取程序开始时间，并以此构造文件名
    start = time.time()
    start_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    output_dir_name = filename.strip(".txt") + "-" + time.strftime("%Y年%m月%d日-%H时%M分%S秒", time.localtime())

    # 获取模块绝对路径，并切换目录
    root_path = os.getcwd()
    oneforall_path = os.path.join(root_path, "OneForAll", "OneForAll-master--20230417", "oneforall.py")
    oneforall_results_path = os.path.join(root_path, "OneForAll", "OneForAll-master--20230417", "results")
    oneforall_bak_results_path = os.path.join(root_path, "OneForAll", "OneForAll-master--20230417", "results_bak")
    # httpx_path = os.path.join(root_path, "Httpx", "httpx_1.3.3_windows_amd64.exe")  # windows下
    httpx_path = os.path.join(root_path, "Httpx", "httpx_1.3.3_macOS_amd64")
    wafw00f_path = os.path.join(root_path, "Wafw00f", "wafw00f-master--2023-06", "wafw00f", "main.py")
    filename_path = os.path.join(root_path, filename)
    output_dir_path = os.path.join(root_path, output_dir_name)
    os.mkdir(output_dir_path)
    os.chdir(output_dir_path)

    # 将根域名和IP分别存入对应列表中
    root_domain_list = []
    ip_list = []
    with open(filename_path, "r") as fr:
        lines = fr.readlines()
        for line in lines:
            line = line.strip("\n")
            if isIpaddress(line):  # 判断是IP地址还是域名，IP地址加入到IP列表中，域名加入到域名列表中
                ip_list.append(line)
            else:
                root_domain_list.append(line)
    print()
    root_domain_list = list(dict.fromkeys(root_domain_list))
    print(Fore.RED + "根域名去重后 {} 个".format(len(root_domain_list)) + Style.RESET_ALL)
    print(root_domain_list)
    print()
    ip_list = list(dict.fromkeys(ip_list))
    print(Fore.RED + "IP去重后 {} 个".format(len(ip_list)) + Style.RESET_ALL)
    print(ip_list)


    # 对根域名和IP进行查询
    if len(root_domain_list) == 0:
        sys.exit("目标列表中没有根域名，此工具要求目标列表必须有根域名，程序退出！！！")
    else:
        oneforall_domain_file_path = filename_path  # 为增加程序可读性，构造此参数，调用oneforall时使用
        domainGather(root_domain_list, ip_list, output_dir_name, oneforall_flag, oneforall_path,
                     oneforall_domain_file_path, oneforall_results_path, oneforall_bak_results_path, cdn_flag,
                     serial_flag, filter_flag, waf_flag, wafw00f_path)

    # 获取程序结束时间，并计算耗时
    end_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    end = time.time()
    print()
    print("开始时间：{}".format(start_time))
    print("结束时间：{}".format(end_time))
    print("执行耗时：{}秒".format(end-start))


if __name__ == "__main__":
    main()