# coding=utf-8
"""
目录扫描程序：
1. 需要读取对应的字典
2. 将字典和域名/ip信息进行结合，然后进行请求
3. 判断响应码 来判断是否存在这个目录或者文件
4. 进度信息一定要写好
"""
import os
import sys
from queue import Queue
from config import *
import threading
import requests
from fake_useragent import UserAgent
import sys


class Dir_scan(object):
    def __init__(self, url, dict_name, thread_count):
        self._url = url
        self._dict_name = dict_name
        self._queue = Queue()
        self._thread_count = thread_count
        self._threads = []
        self._total_count = 0

    def _init(self):
        """
        初始化：
        1. 判断字典是否存在
        2. 将字典读取出来
        3. 拼接url 然后放入队列
        :return:
        """
        # 判断字典是否存在
        if not os.path.exists(dict_base_path + self._dict_name):
            print("字典不存在！")
            sys.exit(-1)
        # 打开字典
        with open(dict_base_path + self._dict_name, "r") as f:
            for d in f:
                # 去掉字典前面是否有斜杠
                temp_d = self._check_dict(d)
                # 将拼接好的地址，添加进入队列
                # 判断传递的url是否包含协议
                if "://" in self._url:
                    self._queue.put(self._url + "/" + temp_d)
                else:
                    self._queue.put("http://" + self._url + "/" + temp_d)
                    self._queue.put("https://" + self._url + "/" + temp_d)
            # 保存总数
            self._total_count = self._queue.qsize()

    def _check_dict(self, path):
        """
        去掉path 开头的斜杠
        :param path: 字典内容
        :return:
        """
        return path.lstrip("/")

    def start(self):
        # 先初始化
        self._init()
        # 准备线程
        for i in range(self._thread_count):
            self._threads.append(self.Dir_scan_run(self._queue, self._total_count))
        # 启动线程
        for t in self._threads:
            t.start()
        # 等待子线程结束
        for t in self._threads:
            t.join()

    class Dir_scan_run(threading.Thread):
        def __init__(self, queue, total_count):
            super().__init__()
            self._queue = queue
            self._ua = UserAgent()
            self._total_count = total_count

        def run(self):
            while not self._queue.empty():
                scan_url = self._queue.get()
                # 放提示信息
                self._msg(self._queue.qsize())
                headers = {
                    "User-Agent": self._ua.random,
                    "Referer": "http://www.pikachu.com"
                }
                try:
                    response = requests.get(scan_url.rstrip(), headers=headers)
                    if response.status_code == 200:
                        print(f"\n[*]{scan_url.rstrip()}")
                except Exception as e:
                    pass

        def _msg(self, last_count):
            """
            提示信息：
                还剩多少 ： (队列剩余数量/总数)*100
                已跑： 100-(队列剩余数量/总数)*100
            :return:
            """
            last = round((last_count/self._total_count)*100,3)
            already_do = round(100-last, 3)
            sys.stdout.write(f"\r已跑:{already_do}%,还剩:{last}%")


# 准备一个域名
url = "http://www.pikachu.com"
dict_name = "php.txt"

scan = Dir_scan(url, dict_name, 100)
scan.start()
