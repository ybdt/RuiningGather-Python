#!/usr/bin/env python3
# author: ybdt


# 获取连续IP，例如：公网IP段202.48.45.46、202.48.45.78、202.48.45.108，会获取其中间隔的全部IP
def ipSerial(ip_list):
    # ip地址会出现ipv6的情况，所以需要处理一下
    legal_ip_list = []
    for ip in ip_list:
        if len(ip.split(".")) != 4:
            continue
        else:
            legal_ip_list.append(ip)

    d = {}
    for ip in legal_ip_list:
        ip_parts = ip.split(".")
        c_range = ip_parts[0] + "." + ip_parts[1] + "." + ip_parts[2]
        if c_range not in d.keys():
            c_range_elements = []
            d[c_range] = c_range_elements
            c_range_elements.append(ip)
        else:
            c_range_elements = d[c_range]
            c_range_elements.append(ip)
    # print()
    # print("非CDN IP按C段分类：" + str(d))

    serial_ip_list = []
    for key, value_list in d.items():
        if len(value_list) == 1:
            # print(value_list[0])
            serial_ip_list.append(value_list[0])
        else:
            # print(value_list)
            ip_parts = value_list[0].split(".")
            c_range = ip_parts[0] + "." + ip_parts[1] + "." + ip_parts[2]
            ip_last_part_list = []
            for ip_addr in value_list:
                ip_last_part_list.append(int(ip_addr.split(".")[3]))
            ip_last_part_list.sort()
            # print(ip_last_part_list)  # debug code
            # print(ip_last_part_list[0])  # debug code
            start = int(ip_last_part_list[0])
            end = int(ip_last_part_list[-1])
            for i in range(start, end + 1):
                new_ip = c_range + "." + str(i)
                # print(new_ip)
                serial_ip_list.append(new_ip)
    # print(serial_ip_list)  # debug code

    return serial_ip_list


if __name__ == "__main__":
    # 测试代码
    ip_list = []
    with open("a.txt", "r", encoding="UTF-8") as fr:
        lines = fr.readlines()
        for line in lines:
            ip_list.append( line.strip() )
    # ip_list = ['121.36.76.230', '121.36.76.235']
    serial_ip_list = ipSerial(ip_list)
    with open("b.txt", "w", encoding="UTF-8") as fw:
        for i in serial_ip_list:
            fw.write(i + "\n")
    # print(serial_ip_list)