#!/usr/bin/env python3
# author: ybdt


import requests
import json
from colorama import Fore, Style
import configparser
import argparse
import sys


'''
cf = configparser.ConfigParser()
cf.read("config.ini", encoding="UTF-8")
zoomeye_items = cf.items("zoomeye")
zoomeye_items = dict(zoomeye_items)
zoomeye_username = zoomeye_items["username"]
zoomeye_password = zoomeye_items["password"]
'''
zoomeye_username = ""
zoomeye_password = ""


def domainGather(zoomeye_search_keyword):
    print()
    print("Zoomeye搜索语句：{0}".format(zoomeye_search_keyword))

    # 验证用户
    data = {"username": zoomeye_username, "password": zoomeye_password}
    try:
        r1 = requests.post("https://api.zoomeye.org/user/login", data=json.dumps(data), timeout=5)
    except:
        print("请求返回异常，跳过当前查询")

    # 获取数据
    dict_r1 = eval(r1.text)
    token = dict_r1["access_token"]
    headers = {"Authorization": "JWT " + token}
    try:
        r2 = requests.get("https://api.zoomeye.org/domain/search?{0}&type=1&page=1".format(zoomeye_search_keyword),
                          headers=headers, timeout=5)
    except:
        print("请求返回异常，跳过当前查询")

    # 处理数据
    dict_r2 = eval(r2.text)
    total = dict_r2["total"]
    a = total // 30
    b = total % 30
    if b == 0:
        page = a
    else:
        page = a + 1
    print("共计：{0}条，每页30条，共计：{1}页".format(total, page))
    zoomeye_url_list = []
    zoomeye_ip_list = []
    for i in range(page):
        for j in range(len(dict_r2["list"])):
            subdomain = dict_r2["list"][j]["name"]
            ip_list_tmp = dict_r2["list"][j]["ip"]
            zoomeye_url_list.append(subdomain)
            for k in ip_list_tmp:
                zoomeye_ip_list.append(k)

    # 对收集到的结果进行去重并统计
    zoomeye_url_list_ = list(dict.fromkeys(zoomeye_url_list))
    zoomeye_ip_list_ = list(dict.fromkeys(zoomeye_ip_list))
    print(Fore.RED + "Zoomeye收集到URL：{0}条，去重后：{1}条".format(len(zoomeye_url_list), len(zoomeye_url_list_)) + Style.RESET_ALL)
    print(Fore.RED + "Zoomeye收集到IP：{0}条，去重后：{1}条".format(len(zoomeye_ip_list), len(zoomeye_ip_list_)) + Style.RESET_ALL)

    return zoomeye_url_list_, zoomeye_ip_list_


def usage():
    parser = argparse.ArgumentParser()
    parser.add_argument("-domain", dest="root_domain", type=str,
                        help="要查询的根域名，例如：python3 zoomeye.py -domain jiachengnet.com", required=False)
    args = parser.parse_args()
    if args.root_domain is not None:
        return args.root_domain
    else:
        sys.exit("查看用法：python3 zoomeye.py -h")


if __name__ == "__main__":
    root_domain = usage()
    zoomeye_search_keyword = 'q={}'.format(root_domain)
    zoomeye_url_list_, zoomeye_ip_list_ = domainGather(zoomeye_search_keyword)
    print(zoomeye_url_list_)
    print(zoomeye_ip_list_)