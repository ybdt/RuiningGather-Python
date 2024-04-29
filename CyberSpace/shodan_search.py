#!/usr/bin/env python3
# author: ybdt


import shodan
from colorama import Fore, Style
import configparser
import argparse
import sys


'''
cf = configparser.ConfigParser()
cf.read("config.ini", encoding="UTF-8")
shodan_items = cf.items("shodan")
shodan_items = dict(shodan_items)
SHODAN_API_KEY = shodan_items["shodan_api_key"]
'''
SHODAN_API_KEY = ""


def domainGather(shodan_search_keyword):
    print()
    print("Shodan搜索语句：{0}".format(shodan_search_keyword))

    try:
        api = shodan.Shodan(SHODAN_API_KEY)
        results = api.search(shodan_search_keyword)
        shodan_url_list = []
        shodan_ip_list = []
        total = results["total"]
        for i in range(total):
            hostnames = results["matches"][i]["hostnames"]
            for j in hostnames:
                shodan_url_list.append(j)
            ip = results["matches"][i]["ip_str"]
            shodan_ip_list.append(ip)
    except:
        print("获取数据返回异常，跳过当前查询")
        return [], []

    # 对收集到的结果进行去重并统计
    shodan_url_list_ = list(dict.fromkeys(shodan_url_list))
    shodan_ip_list_ = list(dict.fromkeys(shodan_ip_list))
    print(Fore.RED + "Shodan收集到URL：{0}条，去重后：{1}条".format(len(shodan_url_list), len(shodan_url_list_)) + Style.RESET_ALL)
    print(Fore.RED + "Shodan收集到IP：{0}条，去重后：{1}条".format(len(shodan_ip_list), len(shodan_ip_list_)) + Style.RESET_ALL)

    return shodan_url_list_, shodan_ip_list_


def usage():
    parser = argparse.ArgumentParser()
    parser.add_argument("-domain", dest="root_domain", type=str,
                        help="要查询的根域名，例如：python3 shodan_search.py -domain jiachengnet.com", required=False)
    args = parser.parse_args()
    if args.root_domain is not None:
        return args.root_domain
    else:
        sys.exit("查看用法：python3 shodan_search.py -h")


if __name__ == "__main__":
    root_domain = usage()
    shodan_search_keyword = 'hostname:{}'.format(root_domain)
    shodan_url_list_, shodan_ip_list_ = domainGather(shodan_search_keyword)
    print(shodan_url_list_)
    print(shodan_ip_list_)