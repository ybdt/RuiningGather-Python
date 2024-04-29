#!/usr/bin/env python3
# author: ybdt


import requests
import queue
import threading
import random


requests.packages.urllib3.disable_warnings()  # 关闭https提醒


def get_headers():
    user_agent = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 YaBrowser/21.6.0.615 Yowser/2.5 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Edge/91.0.864.59',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Linux; Android 11; SM-G991U Build/RP1A.200720.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        'Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.8.1) Gecko/20061010 Firefox/2.0',
        'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.6 Safari/532.0',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1 ; x64; en-US; rv:1.9.1b2pre) Gecko/20081026 Firefox/3.1b2pre',
        'Opera/10.60 (Windows NT 5.1; U; zh-cn) Presto/2.6.30 Version/10.60',
        'Opera/8.01 (J2ME/MIDP; Opera Mini/2.0.4062; en; U; ssr)',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; ; rv:1.9.0.14) Gecko/2009082707 Firefox/3.0.14',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Mozilla/5.0 (Windows; U; Windows NT 6.0; fr; rv:1.9.2.4) Gecko/20100523 Firefox/3.6.4 ( .NET CLR 3.5.30729)',
        'Mozilla/5.0 (Windows; U; Windows NT 6.0; fr-FR) AppleWebKit/528.16 (KHTML, like Gecko) Version/4.0 Safari/528.16',
        'Mozilla/5.0 (Windows; U; Windows NT 6.0; fr-FR) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 '
        'Safari/533.18.5',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5660.225 Safari/537.36'
    ]
    random_user_agent = random.choice(user_agent)
    headers = {
        'Accept': 'application/x-shockwave-flash, image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, '
                  'application/vnd.ms-excel, application/vnd.ms-powerpoint, application/msword, */*',
        'User-agent': random_user_agent,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'close'
    }
    return headers


def get_code(q, alive_url_list, dead_url_list, alive_url_with_code_200_list, alive_url_with_other_code_list):
    while True:
        if q.empty():
            return
        else:
            url = q.get()
            try:
                headers = get_headers()
                r = requests.get(url=url, headers=headers, timeout=10, verify=False, allow_redirects=False)
            except:
                print(f"{url}----------is dead")
                dead_url_list.append(url)
            else:
                alive_url_list.append(url)
                status_code = r.status_code
                if status_code == 200:
                    alive_url_with_code_200_list.append(url)
                else:
                    alive_url_with_other_code_list.append(url)
                print(f"{url}----------{status_code}")


if __name__ == "__main__":
    with open("url-26981.txt", "r") as fr:
        lines = fr.readlines()
    q = queue.Queue()
    for line in lines:
        line = line.strip("\n")
        q.put(line)
    lines = list(dict.fromkeys(lines))

    alive_url_list = []
    dead_url_list = []
    alive_url_with_code_200_list = []
    alive_url_with_other_code_list = []
    threads_num = 30
    threads = []
    for i in range(threads_num):
        t = threading.Thread(target=get_code, args=(q, alive_url_list, dead_url_list, alive_url_with_code_200_list, alive_url_with_other_code_list))
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

    print(f"Alive URL输出到文件：{alive_url_filename}")
    print(f"Dead URL输出到文件：{dead_url_filename}")
    print(f"Alive URL With Code 200输出到文件：{alive_url_with_code_200_filename}")
    print(f"Alive URL With Other Code输出到文件：{alive_url_with_other_code_filename}")