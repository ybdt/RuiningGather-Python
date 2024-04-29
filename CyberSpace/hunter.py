#!/usr/bin/env python3
# author: ybdt


'''
编写自动化切换账户碰到如下坑：
01 每页查询99条时，会返回不合法，可以查询1条、10条、100条，但是99条不行
02 当前账户免费积分小于100时，会无法调用api
03 单次查询，最多1万条
04 账户切换多了，会提示：账号已封禁，请联系客服小猎手，跳过当前查询，解决办法：登录hunter的web界面，查询一次，看账户是否被禁用
'''


import base64
import datetime
from urllib.parse import quote
import sys
import requests
import json
import math
import time
from colorama import Fore, Style
import argparse


'''
'''

hunter_token_list = [

]
i = 0  # 定义账户索引，0表示第1个账户
count = len(hunter_token_list) - (i + 1)  # 剩余账户数量


# 【当前函数未进行优化】获取当前日期时间及一年前日期时间
def getLastYearDateTime():
    now_time = datetime.datetime.now()
    last_year = str(int(now_time.strftime("%Y")) - 1)
    start_time = last_year + "-" + now_time.strftime("%m-%d %H:%M:%S")
    end_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
    start_time = quote(start_time)  #将日期时间进行url编码
    end_time = quote(end_time)  #将日期时间进行url编码
    return start_time, end_time


# 获取当前日期时间及一个月前日期时间
def getLastMonthDateTime():
    now_time = datetime.datetime.now()
    current_year = now_time.strftime("%Y")
    current_month = now_time.strftime("%m")
    if int(current_month) == 1:  # 如果当前月份为1月，则上一个月份为12月，同时年份也需要减1
        last_month = "12"
        last_year = str(int(current_year) - 1)
    else:  # 如果当前月份不为1月，则上一个月份减1，年份不变
        last_month = str(int(current_month) - 1)
        last_year = current_year
    if len(last_month) == 1:  # 将6变为06，符合月份格式
        last_month = "0" + last_month
    start_time = "{}-{}-{}".format(last_year, last_month, now_time.strftime("%d %H:%M:%S"))
    end_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
    start_time = quote(start_time)  # 将日期时间进行url编码
    end_time = quote(end_time)  # 将日期时间进行url编码
    # print(start_time, end_time)  # debug code
    return start_time, end_time


def hunterGather(hunter_search_keyword):
    hunter_url_list = []  # 用于存储url
    hunter_ip_list = []  # 用于存储ip

    global i  # 定义账户索引，0表示第1个账户
    global count  # 剩余账户数量

    while True:
        print()
        print("Hunter搜索语句：{0}".format(hunter_search_keyword))
        hunter_search_keyword_base64 = base64.urlsafe_b64encode(hunter_search_keyword.encode(encoding="UTF-8"))
        hunter_search_keyword_str = hunter_search_keyword_base64.decode(encoding="UTF-8")
        first_page = 1  # 第1页
        size = 1  # 每页的数据量
        is_web = 3  # 资产类型，1代表”web资产“，2代表”非web资产“，3代表”全部“
        start_time, end_time = getLastMonthDateTime()
        hunter_api_path = "https://hunter.qianxin.com/openApi/search?api-key={}&search={}&page={}&page_size={}&" \
                          "is_web={}&start_time={}&end_time={}".format(hunter_token_list[i], hunter_search_keyword_str,
                                                                       first_page, size, is_web, start_time, end_time)
        try:
            r = requests.get(hunter_api_path, timeout=10)
        except Exception as e:
            print(f"返回异常：{e}，跳过当前查询")
            return [], [], {}
        json_content = json.loads(r.content)
        if json_content["code"] == 400:  # URLBase64转码错误
            print("返回400，当前账户 {} 提示：".format(hunter_token_list[i][:4]) + json_content["message"] + "，跳过当前查询")
            return [], [], {}
        elif json_content["code"] == 401:  # 令牌过期
            print("返回401，当前账户 {} 提示：".format(hunter_token_list[i][:4]) + json_content["message"] + "，跳过当前查询")
            return [], [], {}
        elif json_content["code"] == 40204:  # 积分没了
            print("    当前账户积分用没了，正在切换到第 {} 个账户：{}".format(str(i+1+1), hunter_token_list[i+1][:4]))
            i += 1
            count -= 1
            continue
        elif json_content["code"] == 40205:  # 免费积分不足100
            print("    当前账户今日免费积分不足100，正在切换到第 {} 个账户：{}".format(str(i+1+1), hunter_token_list[i+1][:4]))
            i += 1
            count -= 1
            continue
        elif json_content["code"] == 200:
            total = int(json_content["data"]["total"])  # 查询到的总条数
            consume_quota = json_content["data"]["consume_quota"]  # 消耗积分描述
            rest_quota = json_content["data"]["rest_quota"]  # 今日剩余积分描述
            rest_int = int(rest_quota.split("：")[1])  # 剩余积分
            page = 1
            page_size = 100
            if (total < 100) or (rest_int == 500) or (rest_int == 400) or (rest_int == 300) or (rest_int == 200) or (rest_int == 100):
                pages = math.ceil(total / page_size)
            else:
                pages = math.ceil(total / page_size)
            print("当前为第 {} 个账户：{}，{}，{}".format(i+1, hunter_token_list[i][:4], consume_quota, rest_quota))
            print("查询到 {} 条，每页查询100条，需查询 {} 页".format(str(total), str(pages)))
            while True:
                time.sleep(5)  # 不间隔的话，会返回代码429，提示请求太多，经测试间隔3秒不够，增加为5秒
                start_time, end_time = getLastMonthDateTime()
                hunter_api_path = "https://hunter.qianxin.com/openApi/search?api-key={}&search={}&page={}&" \
                                  "page_size={}&is_web={}&start_time={}&end_time={}".format(hunter_token_list[i],
                                  hunter_search_keyword_str, str(page), str(page_size), is_web, start_time, end_time)
                try:
                    r = requests.get(hunter_api_path, timeout=10)
                except Exception as e:
                    print(f"    正在获取第 {page} 页数据，请求返回异常：{e}，跳过当页查询")
                    if count == 0:
                        print(f"    正在获取第 {page} 页数据，内置账号使用完毕，退出查询")
                        break
                    else:
                        i += 1
                        count -= 1
                        print(f"    正在获取第 {page} 页数据，当前查询出现异常，正在切换到第{i + 1}个账户：{hunter_token_list[i][:4]}")
                        continue
                json_content = json.loads(r.text)
                if json_content["code"] == 40204:  # 积分没了
                    if count == 0:
                        print(f"    正在获取第 {page} 页数据，内置账号使用完毕，退出查询")
                        break
                    else:
                        i += 1
                        count -= 1
                        print(f"    正在获取第 {page} 页数据，当前账户积分用没了，正在切换到第{i+1}个账户：{hunter_token_list[i][:4]}")
                        continue
                elif json_content["code"] == 40205:  # 积分不足100
                    if count == 0:
                        print(f"    正在获取第 {page} 页数据，内置账号使用完毕，退出查询")
                        break
                    else:
                        i += 1
                        count -= 1
                        print(f"    正在获取第 {page} 页数据，当前账户今日免费积分不足100，正在切换到第{i+1}个账户：{hunter_token_list[i][:4]}")
                        continue
                elif json_content["code"] == 400:  # 支持最大查看10000条资产
                    print("    支持最大查看10000条资产，退出当前查询")
                    break
                elif json_content["code"] == 200:
                    arr = json_content["data"]["arr"]
                    if arr == None:
                        print("    正在获取第 {} 页数据，状态码是200，但内容为空，跳过当前查询".format(page))
                        return [], [], {}
                    for each in arr:  # 共计22个字段，只取2个字段
                        hunter_url_list.append(each["url"])
                        hunter_ip_list.append(each["ip"])
                    print("    正在获取第 {} 页数据，查询到{}条".format(page, len(arr)))
                    if page == pages:
                        break
                    else:
                        page += 1
                else:
                    print("    正在获取第 {} 页数据，发生错误：{}，{}跳过当页查询".format(page, json_content["code"], json_content["message"]))
                    if page == pages:
                        break
                    else:
                        page += 1
            break
        else:
            print("发生错误：" + str(json_content["code"]) + "，" + json_content["message"] + "，跳过当前查询")
            return [], [], {}

    # 对收集到的结果进行去重并统计
    hunter_url_list_ = list(dict.fromkeys(hunter_url_list))
    hunter_ip_list_ = list(dict.fromkeys(hunter_ip_list))
    print(Fore.RED + "Hunter收集到URL：{0}条，去重后：{1}条".format(len(hunter_url_list), len(hunter_url_list_)) + Style.RESET_ALL)
    print(Fore.RED + "Hunter收集到IP：{0}条，去重后：{1}条".format(len(hunter_ip_list), len(hunter_ip_list_)) + Style.RESET_ALL)

    return hunter_url_list_, hunter_ip_list_, {}


def usage():
    parser = argparse.ArgumentParser()
    parser.add_argument("-domain", dest="root_domain", type=str,
                        help="要查询的根域名，例如：python3 hunter.py -domain jiachengnet.com", required=False)
    parser.add_argument("-syntax", dest="search_syntax", type=str,
                        help='要搜索的语法，例如：python3 hunter.py -syntax \'ip.city="双鸭山市" && header.status_code=="200"\'',
                        required=False)
    args = parser.parse_args()
    if args.root_domain is not None:
        return args.root_domain, "domain"
    if args.search_syntax is not None:
        return args.search_syntax, "syntax"
    else:
        sys.exit("查看用法：python3 hunter.py -h")


if __name__ == "__main__":
    search_keyword, flag = usage()
    if flag == "domain":
        hunter_search_keyword = 'domain.suffix="{0}"'.format(search_keyword)
    elif flag == "syntax":
        hunter_search_keyword = search_keyword
    # print(f"搜索关键字为：{hunter_search_keyword}")
    hunter_filename = time.strftime("hunter-%Y年%m月%d日-%H时%M分%S秒", time.localtime())
    hunter_url_list_, hunter_ip_list_, hunter_csv_data = hunterGather(hunter_search_keyword)

    # url写入txt
    count = str(len(hunter_url_list_))
    url_filename = "{0}-url-{1}.txt".format(hunter_filename, count)
    with open(url_filename, "w", encoding="UTF-8") as fw_url:
        for url in hunter_url_list_:
            fw_url.write(url + "\n")

    # ip写入txt
    count = str(len(hunter_ip_list_))
    ip_filename = "{0}-ip-{1}.txt".format(hunter_filename, count)
    with open(ip_filename, "w", encoding="UTF-8") as fw_ip:
        for ip in hunter_ip_list_:
            fw_ip.write(ip + "\n")