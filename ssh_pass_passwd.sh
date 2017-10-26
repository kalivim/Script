#!/bin/sh

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

done < /script/hosts
