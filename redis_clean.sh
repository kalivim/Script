#!/bin/sh
#
# redis批量删除匹配keys
#

redis_ip=
redis_db=
redis_passwd=


redis_host="redis-cli -h $redis_ip -n $redis_db -p $redis_passwd"

if [ -n "$1" ];then
	keys=`$redis_host keys $1*|awk -F\" '{print $1}'`
	keys_num=`echo $keys|awk '{print NF}'`
	echo "$keys"
	echo ""
	if [ "$keys_num" != "-1" ];then

		echo "Found keys in total  [$keys_num]"
		echo ""
		read -p "Are you sure clean [y/n]   :" result
		
		if [ "$result" == "y" ];then
			echo ""
			echo "$keys"|xargs $redis_host del {}
		else
			echo ""
			echo "EXIT..."
		fi
	else
		echo "No Found keys !"
		exit 1;
	fi

else
	echo "Please gave argv keynames [ clean-redis keyname ]"

fi
