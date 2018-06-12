#!/bin/sh
#
#初始化 SSH 添加免密 root关闭密码登录
#


sed -i 's/#*PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config

sed -i "s/#*UseDNS yes/UseDNS no/" /etc/ssh/sshd_config

sed -i "s/#*Port .*/Port 52330/" /etc/ssh/sshd_config

sed -i "s/#*GSSAPIAuthentication yes/GSSAPIAuthentication no/" /etc/ssh/sshd_config

sed -i "s/#*PermitRootLogin .*/PermitRootLogin without-password/" /etc/ssh/sshd_config

useradd general_user
echo "passwd"|passwd --stdin "general_user"
echo "passwd"|passwd --stdin "root"

service sshd restart

service firewalld stop || service iptables stop
chkconfig firewalld off || chkconfig iptables off

setenforce 0
sed -i "s/\(# *\)SELINUX=enforcing/SELINUX=disabled/" /etc/selinux/config


echo "your_ssh_pub_key">/root/.ssh/authorized_keys
