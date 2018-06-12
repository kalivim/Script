#!/bin/sh
#
#  Author: Kionf
#
#  Usage: 创建需要免密的机器 写入hosts文件
#  hosts文件格式:
#  1.1.1.1
#  2.2.2.2
#  3.3.3.3
#

yum -y install expect

[ ! -f /root/.ssh/id_rsa.pub ] && ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa

while read line;do
	ip=`echo $line`
	expect <<EOF
	spawn ssh-copy-id -i /root/.ssh/id_rsa.pub root@$ip
	expect {
		"*yes/no" { send "yes\r";exp_continue }
		"*password" { send "password\r" }	
	}
	expect eof
EOF

done < hosts
