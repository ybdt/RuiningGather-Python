#!/usr/bin/env python3
# author: ybdt


"""
碰到如下坑：
01 有时会提示账号无效，想登录web界面发现还没有登录按钮
"""


import base64
import time
import requests
import json
import pandas as pd
import os
from colorama import Fore, Style
import argparse
import sys
import configparser


# 关闭https提醒
requests.packages.urllib3.disable_warnings()


'''
cf = configparser.ConfigParser()
cf.read("config.ini", encoding="UTF-8")
fofa_items = cf.items("fofa")
fofa_items = dict(fofa_items)
fofa_email = fofa_items["fofa_email"]
fofa_key = fofa_items["fofa_key"]
'''
fofa_email = ""
fofa_key = ""


def domainGather(fofa_search_keyword, fofa_filename):
    # 构造fofa api
    print()
    print("FOFA搜索语句：{0}".format(fofa_search_keyword))
    fofa_search_keyword_base64 = base64.b64encode(fofa_search_keyword.encode(encoding="UTF-8"))
    fofa_search_keyword_str = fofa_search_keyword_base64.decode(encoding="UTF-8")

    # 字段说明参考：https://fofa.info/api
    # 共计24个字段，去掉3个字段是企业会员，剩余21个字段
    # 当查询包含字段cert、banner时，单次最多查询2000条，为了能够一次查询10000条数据，去掉字段cert、banner，剩余19个字段
    fields = "ip,port,protocol,country,country_name,region,city,longitude,latitude,as_number,as_organization,host," \
             "domain,os,server,icp,title,jarm,header"
    fofa_api_path = "https://fofa.info/api/v1/search/all?email={0}&key={1}&qbase64={2}&fields={3}page=1&size=10000&" \
                    "full=false".format(fofa_email, fofa_key, fofa_search_keyword_str, fields)

    # 向fofa api发起请求，并将返回内容写入json文件
    fofa_json_filename = fofa_filename + ".json"
    try:
        r = requests.get(fofa_api_path, timeout=10)
    except:
        print("请求返回异常，跳过当前查询")
        return [], [], {}
    with open(fofa_json_filename, "wb") as fw:
        fw.write(r.content)

    # 处理json文件，共计19个字段
    ip_list, port_list, protocol_list, country_list, country_name_list, region_list,  = [[] for x in range(6)]
    city_list, longitude_list, latitude_list, as_number_list, as_organization_list,  = [[] for x in range(5)]
    host_list, domain_list, os_list, server_list, icp_list, title_list, jarm_list = [[] for x in range(7)]
    header_list = [[] for x in range(1)]
    url_list = []
    with open(fofa_json_filename, "r", encoding="UTF-8") as fr:
        dict_obj = json.loads(fr.read())
        if dict_obj["error"]:
            print(dict_obj["errmsg"])
            return [], [], {}
        else:
            results = dict_obj["results"]
            count = len(results)
            url = ""  #先将url赋值为空，若下面未对url赋值，则判定当前根域名无子域名，对应于下面的url是否为空的判断
            for i in range(count):
                ip, port, protocol, country = results[i][0], results[i][1], results[i][2], results[i][3]
                country_name, region, city, longitude = results[i][4], results[i][5], results[i][6], results[i][7]
                latitude, as_number, as_organization = results[i][8], results[i][9], results[i][10]
                host, domain, os_name, server,  =  results[i][11], results[i][12], results[i][13], results[i][14]
                icp, title, jarm, header = results[i][15], results[i][16], results[i][17], results[i][18]
                if protocol == "https":
                    url = host
                elif protocol == "http":
                    url = "http://" + host
                else:
                    url = "http://" + host
                # 批量查询根域名的时候，有些根域名无子域名，不加此判断，会报错
                # UnboundLocalError: local variable 'url' referenced before assignment
                if url == "":
                    print("当前根域名经FOFA查询后，无子域名")
                    return [], [], {}
                url_list.append(url)
                ip_list.append(ip)
                port_list.append(port)
                protocol_list.append(protocol)
                country_list.append(country)
                country_name_list.append(country_name)
                region_list.append(region)
                city_list.append(city)
                longitude_list.append(longitude)
                latitude_list.append(latitude)
                as_number_list.append(as_number)
                as_organization_list.append(as_organization)
                host_list.append(host)
                domain_list.append(domain)
                os_list.append(os_name)
                server_list.append(server)
                icp_list.append(icp)
                title_list.append(title)
                jarm_list.append(jarm)
                header_list.append(header)

    # 此处会将字段选择性写入csv文件，不写入csv文件的字段会放到后面
    fofa_csv_filename = fofa_filename + ".csv"
    fofa_csv_data = {"URL": url_list, "IP": ip_list, "Web Server": server_list, "Title": title_list,
                     "Country": country_name_list, "Province": region_list, "City": city_list, "Organization": as_organization_list}
    df = pd.DataFrame(fofa_csv_data)
    df.to_csv(fofa_csv_filename, index=False)

    # 对收集到的结果进行去重并统计
    fofa_url_list_ = list(dict.fromkeys(url_list))
    fofa_ip_list_ = list(dict.fromkeys(ip_list))
    print(Fore.RED + "FOFA收集到URL：{0}条，去重后：{1}条".format(len(url_list), len(fofa_url_list_)) + Style.RESET_ALL)
    print(Fore.RED + "FOFA收集到IP：{0}条，去重后：{1}条".format(len(ip_list), len(fofa_ip_list_)) + Style.RESET_ALL)

    # 清理临时的json文件和csv文件，并返回
    os.remove(fofa_json_filename)
    os.remove(fofa_csv_filename)
    return fofa_url_list_, fofa_ip_list_, fofa_csv_data


def ipGather(fofa_search_keyword, fofa_filename):
    # 构造fofa api
    print()
    print("FOFA搜索语句：{0}".format(fofa_search_keyword))
    fofa_search_keyword_base64 = base64.b64encode(fofa_search_keyword.encode(encoding="UTF-8"))
    fofa_search_keyword_str = fofa_search_keyword_base64.decode(encoding="UTF-8")
    fofa_api_path = "https://fofa.info/api/v1/search/all?email={0}&key={1}&qbase64={2}&page=1&size=10000&full=true".\
                    format(fofa_email, fofa_key, fofa_search_keyword_str)

    # 向fofa api发起请求，并将返回内容写入json文件
    fofa_json_filename = fofa_filename + ".json"
    try:
        r = requests.get(fofa_api_path)
    except:
        print("请求返回异常，跳过当前查询")
        return "", []
    with open(fofa_json_filename, "wb") as fw:
        fw.write(r.content)

    # 处理json文件
    port_list = []
    with open(fofa_json_filename, "r", encoding="UTF-8") as fr:
        dict_obj = json.loads(fr.read())
        if dict_obj["error"]:
            print(dict_obj["errmsg"])
            return "", []
        else:
            results = dict_obj["results"]
            if results == []:
                print("results为空列表")
                return "", []
            else:
                count = len(results)
                for i in range(count):
                    ip = results[i][1]
                    port = results[i][2]
                    port_list.append(port)

    # 清理临时的json文件
    os.remove(fofa_json_filename)

    return ip, port_list


def usage():
    parser = argparse.ArgumentParser()
    parser.add_argument("-domain", dest="root_domain", type=str,
                        help="要查询的根域名，例如：python3 fofa.py -domain jiachengnet.com", required=False)
    parser.add_argument("-syntax", dest="search_syntax", type=str,
                        help='要搜索的语法，例如：python3 fofa.py -syntax \'ip_city="Shuangyashan"\'', required=False)
    args = parser.parse_args()
    if args.root_domain is not None:
        return args.root_domain, "domain"
    elif args.search_syntax is not None:
        return args.search_syntax, "syntax"
    else:
        sys.exit("查看用法：python3 fofa.py -h")


if __name__ == "__main__":
    search_keyword, flag = usage()
    if flag == "domain":
        root_domain = search_keyword
        fofa_search_keyword = 'domain="{0}"'.format(root_domain)
    elif flag == "syntax":
        search_syntax = search_keyword
        fofa_search_keyword = search_syntax
    print(f"搜索关键字：{fofa_search_keyword}")

    fofa_filename = time.strftime("fofa-%Y年%m月%d日-%H时%M分%S秒", time.localtime())
    fofa_url_list_, fofa_ip_list_, fofa_csv_data = domainGather(fofa_search_keyword, fofa_filename)

    # url写入txt
    count = str(len(fofa_url_list_))
    url_filename = "{0}-url-{1}.txt".format(fofa_filename, count)
    with open(url_filename, "w", encoding="UTF-8") as fw_url:
        for url in fofa_url_list_:
            fw_url.write(url + "\n")

    # ip写入txt
    count = str(len(fofa_ip_list_))
    ip_filename = "{0}-ip-{1}.txt".format(fofa_filename, count)
    with open(ip_filename, "w", encoding="UTF-8") as fw_ip:
        for ip in fofa_ip_list_:
            fw_ip.write(ip + "\n")

    '''
    # 多个字段写入csv
    count = str(len(fofa_url_list_))
    csv_filename = "{0}-all-{1}.csv".format(fofa_filename, count)
    df = pd.DataFrame(fofa_csv_data)
    df.to_csv(csv_filename, index=False)
    '''

    '''
    # 调用fofa收集ip和端口
    ip_address = search_keyword
    fofa_ip_search_keyword = 'ip="{0}"'.format(ip_address)
    fofa_filename = time.strftime("fofa-%Y年%m月%d日-%H时%M分%S秒", time.localtime())
    ip, port_list = ipGather(fofa_ip_search_keyword, fofa_filename)
    port_list = list(dict.fromkeys(port_list))
    print(ip + "：" + str(port_list))
    '''