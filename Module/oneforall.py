#!/usr/bin/env python3
# author: ybdt


import os
import shutil
import subprocess
import pandas as pd
import numpy
import chardet


def get_charset(file_path):
    with open(file_path, "rb") as fr:
        tmp = chardet.detect(fr.read())
        return tmp["encoding"]


# 调用oneforall
def oneforall_gather(oneforall_path, oneforall_domain_file_path, oneforall_results_path, oneforall_bak_results_path):
    # 有些情况下，程序执行完删除results后发生异常，也就不会生成results，导致再次执行时会报错，所以需要处理一下
    if not os.path.exists(oneforall_results_path):
        os.mkdir(oneforall_results_path)

    # 重命名结果目录并执行
    if os.path.exists(oneforall_bak_results_path):
        shutil.rmtree(oneforall_bak_results_path)
        os.rename(oneforall_results_path, oneforall_bak_results_path)
    else:
        os.rename(oneforall_results_path, oneforall_bak_results_path)
    # subprocess.run(["python3", oneforall_path, "--targets", oneforall_domain_file_path, "--alive", "False",
    #                 "--brute", "False", "--dns", "True", "run"], shell=True)  # windows下
    subprocess.run(["python3", oneforall_path, "--targets", oneforall_domain_file_path, "--alive", "False", "--brute",
                    "False", "--dns", "True", "run"])  # mac下

    # 当传入多个根域名时，oneforall结果以all_subdomain命名
    for filename in os.listdir(oneforall_results_path):
        if filename.startswith("all_subdomain") and filename[-4:] == ".csv":
            subdomain_file = filename
            break
        else:
            continue

    # 当没获取到文件名，表示传入单个根域名，oneforall结果以根域名命名
    if "subdomain_file" not in dir():
        for filename in os.listdir(oneforall_results_path):
            if filename[-4:] == ".csv":
                subdomain_file = filename
                break
            else:
                continue

    # 读取csv文件内容到列表
    url_list = []
    ip_list = []
    subdomain_file_path = os.path.join(oneforall_results_path, subdomain_file)
    encoding = get_charset(subdomain_file_path)
    df_url = pd.read_csv(subdomain_file_path, usecols=[4], encoding=encoding)
    array_df_url = numpy.array(df_url)
    for i in array_df_url.tolist():  # 返回的列表是二维列表，故需要两层for循环
        for j in i:
            url_list.append(j)
    df_ip = pd.read_csv(subdomain_file_path, usecols=[8], encoding=encoding)
    array_df_ip = numpy.array(df_ip)
    """
    print(array_df_ip.tolist())  # debug code
    [['47.108.156.80'], ['47.108.156.80'], ['47.108.156.80'], ['47.108.156.80'], ['81.71.34.61'], ['81.71.34.61'],
    ['81.71.34.61'], ['81.71.34.61'], ['47.104.78.80'], ['47.104.78.80'], ['47.108.156.80'], ['47.108.156.80'],
    ['81.71.34.61'], ['81.71.34.61'], ['81.71.34.61'], ['81.71.34.61'], ['81.71.34.61'], ['81.71.34.61'],
    ['81.71.34.61'], ['81.71.34.61'], ['49.234.245.167'], ['49.234.245.167'], ['49.234.245.167'], ['49.234.245.167'],
    ['47.97.164.186'], ['47.97.164.186'], ['47.99.135.141'], ['47.99.135.141'], ['47.114.14.86'], ['47.114.14.86'],
    ['47.114.14.86'], ['47.114.14.86'], ['47.114.14.86'], ['47.114.14.86'], ['121.40.177.106'], ['121.40.177.106'],
    ['47.99.135.141'], ['47.99.135.141'], ['47.99.135.141'], ['47.99.135.141'], ['47.114.14.86'], ['47.114.14.86'],
    ['47.114.14.86'], ['47.114.14.86'], ['47.97.164.186'], ['47.97.164.186'], ['47.97.164.186'], ['47.97.164.186'],
    ['47.97.164.186'], ['47.97.164.186'], ['47.114.14.86'], ['47.114.14.86'], ['47.97.164.186'], ['47.97.164.186'],
    ['47.97.164.186'], ['47.97.164.186'], ['47.99.135.141'], ['47.99.135.141'], ['47.99.135.141'], ['47.99.135.141'],
    ['120.26.77.250'], ['120.26.77.250'], ['47.97.164.186'], ['47.97.164.186'], ['36.112.151.155'], ['36.112.151.155'],
    ['111.40.178.76'], ['111.40.178.76'], ['47.99.135.141'], ['47.99.135.141'], ['47.97.164.186'], ['47.97.164.186'],
    ['47.99.135.141'], ['47.99.135.141'], ['47.99.135.141'], ['47.99.135.141'], ['47.97.164.186'], ['47.97.164.186'],
    ['114.215.217.186'], ['114.215.217.186'], ['47.97.164.186'], ['47.97.164.186'], ['47.246.146.253'],
    ['47.246.146.253'], ['120.26.77.250'], ['120.26.77.250'], ['118.31.232.196'], ['118.31.232.196'], ['47.114.14.86'],
    ['47.114.14.86'], ['47.97.164.186'], ['47.97.164.186'], ['47.97.164.186'], ['47.97.164.186'], ['47.99.135.141'],
    ['47.99.135.141'], ['142.132.149.97'], ['142.132.149.97'], ['47.99.135.141'], ['47.99.135.141'], ['47.114.14.86'],
    ['47.114.14.86'], ['47.99.135.141'], ['47.99.135.141'], ['47.114.14.86'], ['47.114.14.86'], ['47.114.14.86'],
    ['47.114.14.86'], ['47.99.135.141'], ['47.99.135.141'], ['47.99.135.141'], ['47.99.135.141'],
    ['113.113.97.43,113.113.97.41,113.113.97.42'], ['113.113.97.43,113.113.97.41,113.113.97.42'],
    ['113.113.97.39,113.113.97.40'], ['113.113.97.39,113.113.97.40'], ['139.215.216.7'], ['139.215.216.7'],
    ['139.215.208.13'], ['139.215.208.13'], ['139.215.208.9'], ['139.215.208.9'], ['139.215.208.13'],
    ['139.215.208.13'], ['139.215.208.12'], ['139.215.208.12'], ['139.215.208.76'], ['139.215.208.76'],
    ['122.141.177.30'], ['122.141.177.30'], ['139.215.208.13'], ['139.215.208.13'], ['139.215.216.9'],
    ['139.215.216.9'], ['139.215.208.76'], ['139.215.208.76'], ['111.26.49.204'], ['111.26.49.204'], ['139.215.208.13'],
    ['139.215.208.13'], ['139.215.216.26'], ['139.215.216.26'], ['139.215.208.77'], ['139.215.208.77'],
    ['139.215.208.52'], ['139.215.208.52'], ['139.215.208.13'], ['139.215.208.13'], ['139.215.208.13'],
    ['139.215.208.13'], ['139.215.208.13'], ['139.215.208.13'], ['139.215.208.41'], ['139.215.208.41'],
    ['139.215.208.13'], ['139.215.208.13']]
    """
    for i in array_df_ip.tolist():  # 返回的列表是二维列表，需要两层for循环
        for j in i:
            try:  # 程序报错：j为float，不能迭代
                if "," in j:
                    multi_ip = j.split(",")
                    for k in multi_ip:
                        ip_list.append(k)
                else:
                    ip_list.append(j)
            except Exception as e:
                print("{} 发生异常 {}".format(j, e))
                continue
    '''
    new_ip_list = []
    for ip in ip_list:
        if "," in ip:
            multi_ip_list = ip.split(",")
            for k in multi_ip_list:
                new_ip_list.append(k)
        else:
            new_ip_list.append(ip)
    '''
    return url_list, ip_list


if __name__ == "__main__":
    oneforall_path = ""
    oneforall_domain_file_path = ""
    oneforall_results_path = ""
    oneforall_bak_results_path = ""
    url_list, ip_list = oneforall_gather(oneforall_path, oneforall_domain_file_path, oneforall_results_path,
                                         oneforall_bak_results_path)
    print(url_list)
    print(ip_list)