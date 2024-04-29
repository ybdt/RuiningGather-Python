#!/usr/bin/env python3
# author: ybdt


import requests
import json
import math
import time
import pandas as pd
import os
from colorama import Fore, Style
import configparser
import argparse
import sys


'''
cf = configparser.ConfigParser()
cf.read("config.ini", encoding="UTF-8")
quake_items = cf.items("quake")
quake_items = dict(quake_items)
quake_token = quake_items["quake_token"]
'''
quake_token = ""


def domainGather(quake_search_keyword, quake_filename):
    # 构造api，查询用户信息
    headers = {
        "X-QuakeToken": quake_token
    }
    try:
        response = requests.get(url="https://quake.360.cn/api/v3/user/info", headers=headers, timeout=5)
    except:
        print("请求返回异常，跳过当前查询")
        [], [], {}
    free_query_api_count = response.json()["data"]["free_query_api_count"]
    month_remaining_credit = response.json()["data"]["month_remaining_credit"]
    persistent_credit = response.json()["data"]["persistent_credit"]
    print()
    print("Quake搜索语句：{0}".format(quake_search_keyword))
    print("每月免费api查询5次（剩余{}次），月度积分剩余{}，长效积分剩余{}".format(free_query_api_count, month_remaining_credit,
    persistent_credit))

    # 构造api，查询一共多少条，并计算需要查询几页
    headers = {
        "X-QuakeToken": quake_token,
        "Content-Type": "application/json"
    }
    data = {
        "query": quake_search_keyword,
        "ignore_cache": False,
        "latest": "true"
    }
    try:
        r = requests.post(url="https://quake.360.cn/api/v3/search/quake_service", headers=headers, json=data, timeout=5)
    except:
        print("请求返回异常，跳过当前查询")
        return [], [], {}
    quake_json_filename = quake_filename + "-page1-tmp.json"
    with open(quake_json_filename, "wb") as fw:
        fw.write(r.content)
    with open(quake_json_filename, "r", encoding="UTF-8") as fr:
        json_content = json.loads(fr.read())
    os.remove(quake_json_filename)
    total_count = json_content["meta"]["pagination"]["total"]
    pages = total_count / 100
    pages = math.ceil(pages)  #计算查询页数
    print("共查询到{0}条，（每页100条）需查询{1}页".format(total_count, pages))

    # 依次获取每页数据，共计13个字段
    quake_url_list = []  #存储url字段
    quake_ip_list = []  #存储ip字段
    port_list = []
    hostname_list = []
    transport_list = []
    asn_list = []
    org_list = []
    protocol_list = []
    country_list = []
    province_list = []
    city_list = []
    subdomain_list = []
    title_list = []
    server_list = []
    for page in range(1, pages+1):
        start = (page - 1) * 100
        data = {
            "query": quake_search_keyword,
            "start": start,
            "size": 100,
            "ignore_cache": True,
            "latest": "true"
        }
        print("    正在获取quake第{0}页数据...".format(page))
        try:
            r = requests.post(url="https://quake.360.cn/api/v3/search/quake_service", headers=headers, json=data, timeout=5)
            json_content = r.json()
        except:
            print("        当前页查询返回异常，查询下一页")
            continue

        # 查询失败
        if json_content["code"] != 0:
            if json_content["message"] == "网页查询最大允许查询500条数据。":
                print("        达到api查询最大数据量500条，退出查询")
                break
            else:
                print("        " + json_content["message"])
                continue

        # 查询成功
        else:
            data = json_content["data"]
            # print(data)
            for each in data:
                ip = each["ip"]
                port = each["port"]
                port_list.append(port)
                hostname_list.append(each["hostname"])
                transport_list.append(each["transport"])
                asn_list.append(each["asn"])
                org_list.append(each["org"])
                country_list.append(each["location"]["country_cn"])
                province_list.append(each["location"]["province_cn"])
                city_list.append(each["location"]["city_cn"])
                protocol = each["service"]["name"]
                protocol_list.append(protocol)
                subdomain = each["service"]["http"]["host"]
                subdomain_list.append(subdomain)
                title = each["service"]["http"]["title"]
                title_list.append(title)
                server = each["service"]["http"]["server"]
                server_list.append(server)
                if protocol == "http":
                    url = "http://" + subdomain + ":" + str(port)
                elif protocol == "http/ssl":
                    url = "https://" + subdomain
                quake_url_list.append(url)
                quake_ip_list.append(ip)
            time.sleep(5)  #不睡眠的话可能会报错 "调用API过于频繁"

    # 写入csv
    quake_csv_filename = quake_filename + ".csv"
    # 此处会将字段选择性写入csv文件，不写入csv文件的字段会放到后面
    quake_csv_data = {"URL": quake_url_list, "IP": quake_ip_list, "Web Server": server_list, "Title": title_list,
                      "Country": country_list, "Province": province_list, "City": city_list, "Organization": org_list}
    df = pd.DataFrame(quake_csv_data)
    df.to_csv(quake_csv_filename, index=False)

    # 对收集到的结果进行去重并统计
    quake_url_list_ = list(dict.fromkeys(quake_url_list))
    quake_ip_list_ = list(dict.fromkeys(quake_ip_list))
    print(Fore.RED + "Quake收集到URL：{0}条，去重后：{1}条".format(len(quake_url_list), len(quake_url_list_)) + Style.RESET_ALL)
    print(Fore.RED + "Quake收集到IP：{0}条，去重后：{1}条".format(len(quake_ip_list), len(quake_ip_list_)) + Style.RESET_ALL)

    # 清理临时文件csv
    os.remove(quake_csv_filename)

    return quake_url_list_, quake_ip_list_, quake_csv_data


def usage():
    parser = argparse.ArgumentParser()
    parser.add_argument("-domain", dest="root_domain", type=str,
                        help="要查询的根域名，例如：python3 quake.py -domain jiachengnet.com", required=False)
    args = parser.parse_args()
    if args.root_domain is not None:
        return args.root_domain
    else:
        sys.exit("查看用法：python3 quake.py -h")


if __name__ == "__main__":
    root_domain = usage()
    quake_search_keyword = 'domain:"{0}"'.format(root_domain)
    quake_filename = time.strftime("quake-%Y年%m月%d日-%H时%M分%S秒", time.localtime())
    quake_url_list_, quake_ip_list_, quake_csv_data = domainGather(quake_search_keyword, quake_filename)

    # url写入txt
    count = str(len(quake_url_list_))
    url_filename = "{0}-url-{1}.txt".format(quake_filename, count)
    with open(url_filename, "w", encoding="UTF-8") as fw_url:
        for url in quake_url_list_:
            fw_url.write(url + "\n")

    # ip写入txt
    count = str(len(quake_ip_list_))
    ip_filename = "{0}-ip-{1}.txt".format(quake_filename, count)
    with open(ip_filename, "w", encoding="UTF-8") as fw_ip:
        for ip in quake_ip_list_:
            fw_ip.write(ip + "\n")

    # 多个字段写入csv
    count = str(len(quake_url_list_))
    csv_filename = "{0}-all-{1}.csv".format(quake_filename, count)
    df = pd.DataFrame(quake_csv_data)
    df.to_csv(csv_filename, index=False)