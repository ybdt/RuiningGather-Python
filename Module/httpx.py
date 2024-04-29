#!/usr/bin/env python3
# author: ybdt


import platform
import subprocess
import sys


def alive_detect(httpx_path, final_url_name):
    if platform.system().lower() == "windows":
        subprocess.run([httpx_path, "-l", final_url_name, "-o", "url-alive.txt"], shell=True)
    elif platform.system().lower() == "darwin":
        subprocess.run([httpx_path, "-l", final_url_name, "-o", "url-alive.txt"])
    else:
        sys.exit("当前不支持linux下httpx，程序退出！！！")