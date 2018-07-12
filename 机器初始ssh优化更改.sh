#!/bin/sh
#
# Desc: 初始化机器
#
# Author: Kionf
#

function change_sshd_config() {
 
    sed -i 's/#*PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
    sed -i "s/#*UseDNS yes/UseDNS no/" /etc/ssh/sshd_config
    sed -i "s/#*Port .*/Port 52330/" /etc/ssh/sshd_config
    sed -i "s/#*GSSAPIAuthentication yes/GSSAPIAuthentication no/" /etc/ssh/sshd_config
    sed -i "s/#*PermitRootLogin .*/PermitRootLogin without-password/" /etc/ssh/sshd_config

    service sshd restart
    
}

function service_init() {

    service firewalld stop || service iptables stop
    chkconfig firewalld off || chkconfig iptables off
    setenforce 0
    sed -i "s/\(# *\)SELINUX=enforcing/SELINUX=disabled/" /etc/selinux/config
    
}

function add_ssh_login_info() {

    [ -d "/root/.ssh" ] || mkdir /root/.ssh
    echo "your_pub_ssh_key">/root/.ssh/authorized_keys
    useradd your_user
    echo "passwd"|passwd --stdin "your_user"
    echo "passwd"|passwd --stdin "root"
    
}

function other_init_config() {

    #审计
    echo "export HISTTIMEFORMAT=\"%F %T \`who -u am i 2>/dev/null| awk '{print \$NF}'|sed -e 's/[()]//g'\` \`whoami\` \"" >> /etc/profile
    echo "PS1='\[\e[31m\]\u@\h\[\e[m\][\A]\[\e[34m\]\W:\[\e[34m\]\$\[\e[m\] '" >> /etc/profile
    yum -y -q install epel-release && yum clean all && yum makecache

}

change_sshd_config
service_init
add_ssh_login_info
other_init_config
