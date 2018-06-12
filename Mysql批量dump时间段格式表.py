#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: kionf
#

import os
import sys
import datetime


#需要加时间的日期表
Change_Tables = ['expadd', 'test', 'user_lock']
Dump_Tables = ''


def strtodatetime(datestr, format):
    return datetime.datetime.strptime(datestr, format)


def datediff(beginDate, endDate):
    format = "%Y_%m_%d";
    bd = strtodatetime(beginDate, format)
    ed = strtodatetime(endDate, format)
    oneday = datetime.timedelta(days=1)
    count = 0
    while bd != ed:
        ed = ed - oneday
        count += 1
    return count


def datetostr(date):
    return str(date)[0:10]


def GenerateTables(beginDate, endDate):
    format = "%Y_%m_%d"
    bd = strtodatetime(beginDate, format)
    ed = strtodatetime(endDate, format)
    oneday = datetime.timedelta(days=1)
    num = datediff(beginDate, endDate) + 1
    li = []
    fuck = []
    for i in range(0, num):
        li.append(datetostr(ed.strftime("%Y_%m_%d")))
        ed = ed - oneday
    for table in Change_Tables:
        for date in li:
            fuck.append(table + date)
    fuck = ' '.join(fuck)
    
    return fuck

def main():
    bdate = raw_input('开始时间： ')
    edate = raw_input('结束时间： ')
    Date_Tables = GenerateTables(bdate, edate)
    Dump_Tables = Date_Tables
    print('开始备份数据。。。')
    DumpCommand = 'mysqldump --force -uroot -p -h172.16.0.13 --skip-lock-tables your_database ' + Dump_Tables + ' |gzip > dump.sql.gz'
    print DumpCommand
    os.system(DumpCommand)
    print('文件大小为：\n')
    os.system('ls -alh /root/script/dump.sql.gz')

if __name__ == '__main__':
    main()
