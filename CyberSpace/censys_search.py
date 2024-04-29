#!/usr/bin/env python3
# author: ybdt


from censys.search import CensysHosts
import argparse
import sys
import subprocess
import json
import os
import time


'''
censys需要在命令行初始化
'''


censys_account_index = 0  # 定义账户索引
remain_queries = 0  # 定义剩余查询数


def ipGather(ip):

    global censys_account_index
    global remain_queries

    censys_api_list = [

    ]

    # 检查当前censys账户信息
    try:
        # cp = subprocess.run(["censys", "account", "--json"], shell=True, capture_output=True)  # windows下
        cp = subprocess.run(["censys", "account", "--json"], capture_output=True)
        return_str = cp.stdout.decode("utf-8")  # 将bytes转化为str
        if return_str == "":
            print("请求返回空，跳过当前查询")
            return "", []
        else:
            return_json = json.loads(return_str)  # 将str转化为json
            allowance = return_json["quota"]["allowance"]  # 获取当前账户可用查询次数
            used = return_json["quota"]["used"]  # 获取当前账户已用查询次数
            email = return_json["email"]  # 获取当前账户邮箱
            remain_queries = allowance - used  # 获取当前账户剩余查询次数
            print("当前账户 {}，剩余查询 {} 次".format(email, remain_queries))

        # 如果剩余查询次数为0，则切换账户
        while remain_queries <= 0:
            censys_account_index += 1
            '''
            # windows下
            subprocess.run(["set", "CENSYS_API_ID={}".format((censys_api_dict[censys_account_index])[0])])
            subprocess.run(["set", "CENSYS_API_SECRET={}".format(censys_api_dict[censys_account_index][0])])
            cp = subprocess.run(["censys", "account", "--json"], shell=True, capture_output=True)
            '''
            os.environ["CENSYS_API_ID"] = censys_api_list[censys_account_index][0]
            os.environ["CENSYS_API_SECRET"] = censys_api_list[censys_account_index][1]
            cp = subprocess.run(["censys", "account", "--json"], capture_output=True)
            return_str = cp.stdout.decode("utf-8")  # 将bytes转化为str
            return_json = json.loads(return_str)  # 将str转化为json
            allowance = return_json["quota"]["allowance"]  # 获取当前可用查询次数
            used = return_json["quota"]["used"]  # 获取已用查询次数
            email = return_json["email"]  # 获取当前账户邮箱地址
            remain_queries = allowance - used
            print("正在切换账户... 当前账户 {}，剩余查询 {} 次".format(email, remain_queries))
            time.sleep(1)

        # 查询ip开放端口
        h = CensysHosts()
        host = h.view(ip)
        port_count = len(host["services"])
        port_list = []
        for i in range(port_count):
            port_list.append(host["services"][i]["port"])
        return ip, port_list

    except:
        print("请求返回异常，跳过当前查询")
        return "", []


def usage():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", dest="ip_address", type=str,
                        help="要查询的IP地址，例如：python3 censys_search.py -ip 1.1.1.1", required=False)
    parser.add_argument("-file", dest="ip_filename", type=str,
                        help="要查询的IP地址，例如：python3 censys_search.py -file ip.txt", required=False)
    args = parser.parse_args()
    if args.ip_address is not None:
        return args.ip_address, "ip_address"
    elif args.ip_filename is not None:
        return args.ip_filename, "ip_filename"
    else:
        sys.exit("查看用法：python3 censys_search.py -h")


if __name__ == "__main__":
    ip, flag = usage()
    if flag == "ip_address":
        ip_address = ip
        censys_ip, censys_port_list = ipGather(ip_address)
        print(censys_ip + "：" + str(censys_port_list) + "，端口数：{}".format(len(censys_port_list)))
    elif flag == "ip_filename":
        ip_filename = ip
        with open(ip_filename, "r") as fr:
            lines = fr.readlines()
            for line in lines:
                line = line.strip()
                censys_ip, censys_port_list = ipGather(line)
                print(censys_ip + "：" + str(censys_port_list) + "，端口数：{}".format(len(censys_port_list)))