# !/usr/local/python
# -*- coding: UTF-8 -*-
import os
import time
import socket
import traceback
import threading
import socketserver
import configparser
from pymongo import MongoClient


class UnionServer(socketserver.BaseRequestHandler):
    def handle(self):
        print(self.client_address)
        conn = self.request
        conn.sendall(bytes("你好，我是机器人", encoding="utf-8"))
        while True:
            ret_bytes = conn.recv(1024)
            ret_str = str(ret_bytes, encoding="utf-8")
            if ret_str == "q":
                break
            conn.sendall(bytes(ret_str+"你好我好大家好", encoding="utf-8"))


class Rollcall(object):
    def __init__(self):
        conf = configparser.ConfigParser()
        configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        conf.read(configfile)
        mongi_conn = MongoClient(conf.get('mongodb', 'ip'), int(conf.get('mongodb', 'prot')))
        db = mongi_conn['autotest']
        self.collection = db['sys_clientinfo']

    def rollcall(self):
        while True:
            ip_list = self.collection.find({}, {'ip': 1})
            for i in ip_list:
                cli_ip = i['ip']
                print(cli_ip)
                self.checkonline(cli_ip)
            time.sleep(5)

    @staticmethod
    def checkonline(ip):
        a = socket.socket()
        try:
            a.connect((str(ip), 60002))
        except ConnectionRefusedError:
            print(traceback.format_exc())


if __name__ == "__main__":
    rollcall_thread = threading.Thread(target=Rollcall().rollcall)
    rollcall_thread.start()
    server = socketserver.ThreadingTCPServer(("127.0.0.1", 60001), UnionServer)
    server.serve_forever()
