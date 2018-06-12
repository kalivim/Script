#!/bin/sh
# Author: Kionf
# description: 启动tomcat多实例.
# PATH=/opt/op/java/jdk1.8.0_172/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin
# 应用名称
app=

# war包下载地址
war_url=

soft_dir="/opt/op"
download_war_file="${soft_dir}/war_apps/${app}.war"

export CATALINA_BASE="${soft_dir}/tomcat/$app"
export CATALINA_HOME="${soft_dir}/tomcat"
export JVM_OPTIONS="-Xms128m -Xmx512m -XX:PermSize=128m -XX:MaxPermSize=412m"

check(){
    PID=`ps aux|grep java|grep -w ${CATALINA_BASE}|awk '{print $2}'`
    if [ -n "$PID" ];then
        echo -e "\033[94m $app is running PID:$PID"
        running=`netstat -ntlp|grep $PID|grep 127.0.0.1`
        if [ -n "$running" ];then
            echo -e "\033[92m $app is provide services\033[0m "
        else
            echo -e "\033[93m $app is running but not provide services\033[0m"
        fi
        return 0

    else
        echo -e "\033[91m $app is dead\033[0m "
        return 1
    fi
}

start() {
    check
    if [ $? -eq 1 ];then
        echo -e "\033[94m Start $app \033[0m"
        $CATALINA_HOME/bin/startup.sh >/dev/null 2>&1
    fi
}

stop() {
    check
    if [ $? -eq 0 ];then
        echo -e "\033[94m Stop $app\033[0m"
        $CATALINA_HOME/bin/shutdown.sh >/dev/null 2>&1
        kill -9 $PID
    fi
}

update() {
    echo "下载文件"
    wget ${war_url} -O ${download_war_file} > /dev/null 2>&1
    if [ $? -eq 0 ];then
        cd ${CATALINA_BASE}/webapps/*/; unzip -q -o ${download_war_file}
    fi
}

log() {
    tailf ${CATALINA_BASE}/logs/catalina.out
}


if [ $# != "0" ];then
    case "$1" in
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            stop
            start 
            ;;
        status)
            check
            ;;
        upgrade)
            stop
            update
            start
            ;;
        log)
            log
            ;;
        *)
            echo $"Usage: $0 {start|stop|restart|status|upgrade|log}"
            exit 1
            ;;
    esac
else
    start
    log
fi
