#!/bin/bash

sf_dir=/data/software

jdk_name=jdk-8u112-linux-x64.tar.gz
jdk_url=http://mirrors.linuxeye.com/jdk/${jdk_name}

echo -e "\033[32;1m [+] 软件包安装下载目录：${sf_dir} \033[0m"

Check() {

	if [ $? != 0 ];then
		echo -e "\033[31;1m [!] $1 Failed! \033[0m"
	else
		echo -e "\033[32;1m [+] $1 Success! \033[0m"
	fi
}

JDK() {
	
	wget $jdk_url -P ${sf_dir}/ --no-check-certificate > /dev/null 2>&1
	Check "下载JDK-1.8.112"
	tar xvf ${sf_dir}/${jdk_name} -C ${sf_dir}/ > /dev/null 2>&1
	cat >>/etc/profile <<-EOF
	export JAVA_HOME=/data/software/jdk1.8.0_112
	export PATH=\$JAVA_HOME/bin:\$PATH
	export CLASSPATH=.:\$JAVA_HOME/lib/dt.jar:\$JAVA_HOME/lib/tools.jar
	EOF
	
	source /etc/profile
	java -version> /dev/null 2>&1
	Check "安装JDK-1.8.112"
}

JDK
