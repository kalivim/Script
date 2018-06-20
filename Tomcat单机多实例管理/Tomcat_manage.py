#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/23 15:18
# @Author  : Kionf
# @FileName: bitch_project.py
#
#   初始配置并管理单例tomcat多应用
#

import os
import subprocess
import sys

# PATH = os.getcwd()
PATH = "/opt/op/tomcat"

shell_script = "manage.sh"
bucket = "https://pkg.com/tomcat_app/"

config_data = {
    # 应用名: [ServerPort, ConnectPort, AJPPort, RedirectPort, ]
    'Application': ['8201', '8101', '8301', '8401', 'BaseApplication.war'],
    'BaseNotify_Service': ['8202', '8102', '8302', '8402', 'BaseNotify_Service.war'],
    'BaseUserCenter_Service': ['8203', '8103', '8303', '8403', 'BaseUserCenter_Service.war'],
}


def customize_print(msg, stat=0):
    if stat == 1:
        print("\033[91m [ERROR]:  %s \033[0m" % msg)
    elif stat == 0:
        print("\033[92m [INFO]:  %s \033[0m" % msg)
    elif stat == 2:
        print("\033[93m [DEBUG]:  %s \033[0m" % msg)


class TomcatAppsManage:

    def __init__(self, webapp):
        self.name = webapp
        self.app_config = config_data[self.name]
        self.manage_shell_file = os.path.join(PATH, self.name, self.name)
        self.server_port, self.conn_port, self.ajp_port, self.redirect_port, self.app_war_name = self.app_config
        self.app_download_url = bucket + self.app_war_name
        self.config_file = os.path.join(PATH, self.name, 'conf/server.xml')
        self.webapp_config_dir = os.path.join(PATH, self.name)

    def config_app_port(self):
        customize_print("正在修改APP：%s 配置" % self.name)
        change_port = {
            'ServerPort': "sed -i s'#Server port=\"[0-9]*\"#Server port=\"" + self.server_port + "\"#'g " + self.config_file,
            'ConnPort': "sed -i s'#Connector port=\"[0-9]*\" protocol=\"HTTP/1.1\"#Connector port=\"" + self.conn_port + "\" protocol=\"HTTP/1.1\"#'g " + self.config_file,
            'RedirectPort': "sed -i s'#redirectPort=\"[0-9]*\"#redirectPort=\"" + self.redirect_port + "\"#'g " + self.config_file,
            'AjpPort': "sed -i s'#Connector port=\"[0-9]*\" protocol=\"AJP/1.3\"#Connector port=\"" + self.ajp_port + "\" protocol=\"AJP/1.3\"#'g " + self.config_file,
        }

        for port in change_port.keys():
            # customize_print("修改 %s 端口" % port)
            os.system(change_port[port])

    def config_app_manage_shell(self):
        customize_print("添加管理脚本")
        copy_shell_script = 'cp -f ' + os.path.join(PATH, shell_script) + ' ' + self.manage_shell_file
        os.system(copy_shell_script)
        config_script_app_name = "sed -i 's/app=/app=\"" + self.name + "\"/' " + self.manage_shell_file
        os.system(config_script_app_name)
        config_script_war_url = "sed -i 's#war_url=#war_url=\"" + self.app_download_url + "\"#' " + self.manage_shell_file
        os.system(config_script_war_url)

    def status_app(self):
        """
        :return: 0提供服务，1停止，2未提供服务
        """
        try:
            result = subprocess.check_output(['sh', self.manage_shell_file, 'status'])
        except subprocess.CalledProcessError as e:
            result = e.output
        if 'run' in result:
            if 'is provide services' in result:
                customize_print("应用 %s 成功启动并提供服务" % self.name)
                return 0
            elif 'but' in result:
                customize_print("应用 %s 进程存在但未提供服务" % self.name, 2)
                return 2
        else:
            customize_print("应用 %s 以停止" % self.name, 1)
            return 1

    def manage(self, operate):
        os.system('sh %s %s' % (self.manage_shell_file, operate))

    def restart(self):
        self.manage("stop")
        self.manage("start")

    def start(self):
        self.manage("start")

    def stop(self):
        self.manage("stop")

    def log(self):
        self.manage("log")

    def upgrade(self):
        self.lock_config_file()
        self.manage("upgrade")

    def lock_config_file(self):
        cmd = 'find ' + self.webapp_config_dir + ' -name db*properties -o -name config_base_*|xargs chattr +i >/dev/null 2>&1'
        customize_print("锁配置文件", 2)
        os.system(cmd)

    def unlock_config_file(self):
        cmd = 'find ' + self.webapp_config_dir + ' -name db*properties -o -name config_base_*|xargs chattr -i >/dev/null 2>&1'
        customize_print("解锁配置文件", 2)
        os.system(cmd)


def dash_board(apps, operate):
    """
    主管理程序，调用
    :param operate: 应用操作
    :param apps: apps 为list
    """
    for app in apps:
        app_obj = TomcatAppsManage(app)
        main_dict = {
            "init": app_obj.config_app_port,
            "shell": app_obj.config_app_manage_shell,
            "status": app_obj.status_app,
            "start": app_obj.start,
            "stop": app_obj.stop,
            "restart": app_obj.restart,
            "upgrade": app_obj.upgrade,
            "log": app_obj.log,
            "lock": app_obj.lock_config_file,
            "unlock": app_obj.unlock_config_file,
        }
        try:
            main_dict[operate]()
        except KeyError as e:
            customize_print(help_msg)


help_msg = """
使用方法：
    1 log
    all status
    管理应用编号 操作
操作：
    lock        锁配置文件
    unlock      解锁配置文件
    init        配置tomcat监听端口
    shell       配置webapp控制脚本
    status，start，restart, log，upgrade，stop 应用操作
"""


def main():
    app_list = []
    for index, app_name in enumerate(config_data, 1):
        print "\033[94m %s:  %s \033[0m" % (index, app_name)
        app_list.append(app_name)
    choice = raw_input("输入要管理的服务:  ")
    try:
        app_index = choice.split()[0]
        operate = choice.split()[1]
        if app_index.isdigit():
            app_index = int(app_index)
            if len(app_list) >= app_index > 0:
                app_name = app_list[app_index - 1]
                dash_board(app_name.split(), operate)
        elif app_index == "all":
            dash_board(app_list, operate)
    except ValueError and IndexError:
        customize_print("参数输入错误", 1)
        customize_print(help_msg)


if __name__ == '__main__':
    try:
        dash_board(sys.argv[1].split(), sys.argv[2])
    except IndexError:
        try:
            while True:
                main()
        except KeyboardInterrupt:
            customize_print("Bye!")
