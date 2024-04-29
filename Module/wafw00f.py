#!/usr/bin/env python3
# author: ybdt


import subprocess
import queue
import threading
import os
from colorama import Fore, Style


def waf_detect(q, no_waf_list, other_list, wafw00f_path):
    while True:
        if q.empty():
            return
        else:
            url = q.get()
        # cp = subprocess.Popen(["python3", wafw00f_path, url], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # windows下
        cp = subprocess.run(["python3", wafw00f_path, url], capture_output=True)  # Mac下
        waf_detect_result_str = cp.stdout.decode("utf-8")  # 将bytes转化为str
        if "No WAF detected by the generic detection" in waf_detect_result_str:
            print("[+] URL: {} Without WAF".format(url))
            no_waf_list.append(url)
        else:
            print("[-] URL: {} With WAF or Connection Failed".format(url))
            other_list.append(url)


if __name__ == "__main__":
    wafw00f_path = ""
    url_path = ""
    q = queue.Queue()
    with open(url_path, "r", encoding="UTF-8") as fr:
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
                    t = threading.Thread(target=waf_detect, args=(q, no_waf_list, other_list, wafw00f_path))
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
    print(Fore.YELLOW + "Alive WAF URL输出到文件：{}".format(alive_waf_name) + Style.RESET_ALL)
    print(Fore.YELLOW + "Alive Non WAF URL输出到文件：{}".format(alive_non_waf_name) + Style.RESET_ALL)