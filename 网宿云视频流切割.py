#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/13 11:43
# @Author  : Kionf
# @FileName: cutVido.py
# 切割m3u8视频流并刷新CDN
#
#  ./cutVido.py 00:01:00 http://url.m3u8
#


import os
import sys
import time
import hmac
import base64
import requests
import datetime
from urllib import parse
from hashlib import sha256
from os.path import expanduser
from wcs.commons.config import Config
from wcs.services.client import Client
from wcs.commons.util import urlsafe_base64_encode




config_file = os.path.join(expanduser("~"), ".wcscfg")


class CutVideoUpload():

    def __init__(self):
        self.cfg = Config(config_file)
        self.cli = Client(self.cfg)
        self.bucket = 'buka-vod'
        self.file_prefix = os.path.splitext(argv_file_name)[0]

    @staticmethod
    def format_second(str_time):
        h, m, s = str_time.split(":")
        second = int(h) * 3600 + int(m) * 60 + int(s)

        return second

    def cut_video(self):
        saves_base64 = urlsafe_base64_encode('%s:%s.m3u8' % (self.bucket, self.file_prefix))
        second_time = self.format_second(str_time=argv_time)
        fops = 'avthumb/m3u8/preset/video_640k/ss/%s|saveas/%s' % (second_time, saves_base64)
        res = self.cli.ops_execute(fops, self.bucket, argv_file_name)
        if res[0] == 200:
            print("[INFO]  提交切割视频任务成功")
        else:
            print(res)
            print("[ERROR]  提交切割失败")
            print(res)
            sys.exit(1)
        persistent_id = res[1]['persistentId']

        return persistent_id

    def view_speed(self):
        persistentId = self.cut_video()
        print("[INFO]  等待切割完成...")
        while True:
            res = self.cli.ops_status(persistentId)
            time.sleep(20)
            if res[0] == 3:
                print("[INFO]  切割成功")
                sys.exit(0)


class OpenApiDemo:
    def getDate(self):
        GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
        date_gmt = datetime.datetime.utcnow().strftime(GMT_FORMAT)
        return date_gmt

    def getAuth(self, userName, apikey, date):
        signed_apikey = hmac.new(apikey.encode('utf-8'), date.encode('utf-8'), sha256).digest()
        signed_apikey = base64.b64encode(signed_apikey)
        signed_apikey = userName + ":" + signed_apikey.decode()
        signed_apikey = base64.b64encode(signed_apikey.encode('utf-8'))
        return signed_apikey

    def createHeader(self, userName, accept, authStr, date):
        headers = {
            'Date': date,
            'Accept': accept,
            'Content-type': accept,
            'Authorization': 'Basic ' + authStr.decode()
        }
        return headers

    def sendRequest(self, httpUrl, method, httpGetParams, httpBodyParams, headers):
        if method.upper() == 'POST':
            resp = requests.post(httpUrl, data=httpBodyParamsJSON, headers=headers)
        elif method.upper() == 'GET':
            resp = requests.get(httpUrl, params=httpBodyParamsJSON, headers=headers)
        self.printResp(resp)

    def printResp(self, resp):
        headers_post = dict(resp.headers);
        str = "{}\nServer:{}\nDate:{}\nContent-Length:{}\nConnection:{}\nx-cnc-request-id:{}\n\n{}".format(
            resp.status_code,
            headers_post['Server'],
            headers_post['Date'],
            headers_post['Content-Length'],
            headers_post['Connection'],
            headers_post['x-cnc-request-id'],
            resp.text)
        str_new_json = {'data': str, 'resultCode': 'success'}
        print(str_new_json)


def flush_cdn(url):
    '''
        输入参数部分 begin
    '''

    userName = 'your_user'  # 替换成真实账号
    apikey = 'api_key'  # 替换成真实账号的apikey
    method = 'POST'  # 填写请求方法post/get
    accept = 'application/json'  # 填写返回接收数据模式
    httpHost = "https://open.chinanetcenter.com"
    httpUri = "/ccm/purge/ItemIdReceiver"
    httpGetParams = {
        "datefrom": "2017-03-01T08:55:00+08:00",
        "dateto": "2017-03-01T09:14:59+08:00",
        "type": "fiveminutes"
    }
    httpBodyParamsXML = r'''<?xml version="1.0" encoding="utf-8"?>
    							<domain-list>
    							<domain-name>www.example1.com</domain-name>
    							<domain-name>www.example2.com</domain-name>
    							</domain-list>'''
    httpBodyParamsJSON = '{"urls":["' + url + '",]}'
    '''
        输入参数部分  end
    '''

    ##
    openApiDemo = OpenApiDemo()
    date = openApiDemo.getDate()  # 获取系统时间
    authStr = openApiDemo.getAuth(userName, apikey, date)  # 获取鉴权参数
    headers = openApiDemo.createHeader(userName, accept, authStr, date)  # 获取鉴权参数
    httpUrl = httpHost + httpUri + "?" + parse.urlencode(httpGetParams)
    openApiDemo.sendRequest(httpUrl, method, httpGetParams, httpBodyParamsJSON, headers)


if __name__ == '__main__':
    argv_time = sys.argv[1]
    url = sys.argv[2]
    argv_file_name = url.split("/")[-1]
    print("[INFO]  切割时间: %s, 切割文件: %s " % (argv_time, argv_file_name))
    obj = CutVideoUpload()
    obj.view_speed()
    print("[INFO]  刷新CDN")
    flush_cdn(url=url)
