#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	python upload.py  要上传的文件名
#	
#	description：上传文件到阿里云
#
#	author：kionf

import oss2
import os
import string
import sys
import time

access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', 'your_id')
access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', 'your_keys')
bucket_name = os.getenv('OSS_TEST_BUCKET', 'your_bucket_name')
endpoint = os.getenv('OSS_TEST_ENDPOINT', 'oss-cn-beijing-internal.aliyuncs.com')

bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)


def percentage(consumed_bytes, total_bytes):
    """进度条回调函数，计算当前完成的百分比
    
    :param consumed_bytes: 已经上传/下载的数据量
    :param total_bytes: 总数据量
    """
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        sys.stdout.write('\r{0}% '.format(rate))
        sys.stdout.flush()


def uploadFile(file):
    fileRemote = os.path.split(file)[1]
    print("=====上传 %s 到阿里云 =====" % fileRemote)
    # 带进度条的断点续传
    oss2.resumable_upload(bucket, fileRemote, file, 
                          multipart_threshold=200*1024,
                          part_size=100*1024,
                          num_threads=4,
                          progress_callback=percentage)


if __name__ == '__main__':
    
    def main():
        file=sys.argv[1]
        if file == 'all':
            fileList = os.listdir(os.getcwd())
            for file in fileList:
                uploadFile(file)
        else:
            uploadFile(file)
    
    main()
