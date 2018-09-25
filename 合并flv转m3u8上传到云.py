#!/usr/bin/env python
# -*- coding:utf8 -*-
#
#       合并Flv文件，转m3u8格式上传到七牛，阿里oss
#       Kionf
#

import os
import sys
import oss2
import time
import json
import resquest
import qiniu
import shutil
import commands
import requests
import subprocess
import qiniu.config
from qiniu import Auth, put_file, etag, urlsafe_base64_encode, BucketManager

output_dir = 'result'


def check_status_code(task, msg, exp_code, ret_code):
    """
    检测任务
    """
    if exp_code == ret_code:
        print "\033[92m [INFO]>> %s %s  成功\033[0m" % (task, msg)
    else:
        print "\033[91m [ERROR]>> %s %s  失败\033[0m" % (task, msg)
        exit(1)


class UploadQiniu:
    """
    获取替换文件，合成本地视频文件并上传文件到七牛云进行替换
    """

    def __init__(self, upload_file_name):
        self._access_key = 'key'
        self._secret_key = 'key'
        self._bucket_name = 'name'
        self.handle_file_name = '需要处理的文件名.txt'
        self.upload_file_name = upload_file_name
        self.syn_file = os.path.join(output_dir, self.upload_file_name)

    def get_handler_file(self):
        """
        获取需要合成文件
        :return:合成文件总大小
        """
        all_size = 0
        name_list = []
        list_dir = os.listdir(os.getcwd())
        for name in list_dir:
            suffix_name = os.path.splitext(name)[1]
            if suffix_name == '.flv':
                print "\033[96m [INFO]>> 获取需要合成文件: \033[0m", name
                name_list.append(name)
                all_size += os.stat(name).st_size
                with open(self.handle_file_name, 'ab+') as f:
                    f.write("file '%s'\n" % name)
        if not name_list: print "\033[93m [WARNING]>> 需要合成的文件不存在"

        return name_list, all_size

    def progress_bar(self, size):
        """
        文件合成进度展示
        :param size: 分片文件大小
        """
        rate = 1
        while rate < 99:
            res_size = os.stat(self.syn_file).st_size
            rate = int(100 * (float(res_size) / float(size)))
            sys.stdout.write("\r完成： {0}%\r".format(rate))
            sys.stdout.flush()

    def video_synthesis(self):
        """
        进行文件合成操作
        """
        if not os.path.exists(output_dir): os.mkdir(output_dir)
        if os.path.exists(self.syn_file):
            print "\033[93m [WARNING]>> 合成文件已存在，直接上传\033[0m"
        else:
            file_info = self.get_handler_file()
            name_list = file_info[0]
            comm = "ffmpeg -f concat -i " + self.handle_file_name + " -c copy " + self.syn_file + " >/dev/null 2>&1"
            result = subprocess.Popen(comm, shell=True)
            time.sleep(3)
            size = file_info[1]
            self.progress_bar(size)
            result.wait()
            check_status_code('合成', self.upload_file_name, result.returncode, 0)
            os.remove(self.handle_file_name)
            if remove:
                for tmp_file in name_list:
                    os.remove(tmp_file)

        return self.upload_file_name

    def refresh_url(self):
        """
        刷新CDN链接
        """
        cmd = 'echo "/v2/tune/refresh" |openssl dgst -binary -hmac "' + self._secret_key + '" -sha1 |base64 | tr + - | tr / _'
        token = commands.getoutput(cmd)
        auth = 'QBox %s:%s' % (self._access_key, token)
        headers = {
            'Authorization': auth,
            'Content-Type': 'application/json',
        }
        data = {
            "urls": ["http://f.dddd.tv/%s" % self.upload_file_name]
        }
        api_url = " http://fusion.qiniuapi.com/v2/tune/refresh"
        r = requests.post(api_url, data=json.dumps(data), headers=headers)
        res = r.json()['code']
        check_status_code('刷新CDN', self.upload_file_name, res, 200)

    def upload_qiniu_oss(self):
        """
        上传合成后文件及相关操作
        :return:
        """
        print "\033[96m [INFO]>> 上传%s到七牛\033[0m" % self.upload_file_name
        q = Auth(self._access_key, self._secret_key)
        token = q.upload_token(self._bucket_name, self.upload_file_name, 3600)
        # print "[INFO]>> 删除%s文件碎片" % self.upload_file_name
        # try:
        #     bucket = BucketManager(q)
        #     bucket.delete(self._bucket_name, self.upload_file_name)
        # except Exception as e:
        #     pass
        print "\033[96m [INFO]>> 开始上传...\033[0m"
        ret, info = put_file(token, self.upload_file_name, self.syn_file)
        assert ret['key'] == self.upload_file_name
        assert ret['hash'] == etag(self.syn_file)
        check_status_code('上传', self.upload_file_name, info.status_code, 200)


class UploadAli:
    """
    转换文件格式并上传到阿里oss
    """

    def __init__(self, flv_file_name, upload_abspath_file):
        self._access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', 'id')
        self._access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', 'key')
        self.bucket_name = os.getenv('OSS_TEST_BUCKET', 'name')
        self.endpoint = os.getenv('OSS_TEST_ENDPOINT', 'oss-cn-beijing-internal.aliyuncs.com')
        self.upload_abspath_file = upload_abspath_file
        self.dir_name, self.file_name = os.path.split(self.upload_abspath_file)
        self.flv_file = os.path.join(output_dir, flv_file_name)

    def format_factory(self):
        """
        转换flv格式到m3u8
        """
        if not os.path.exists(self.dir_name): os.mkdir(self.dir_name)
        prefix_name = os.path.splitext(self.file_name)[0]
        ts_name = prefix_name + '.ts'
        comm1 = 'ffmpeg -i ' + self.flv_file \
                + ' -codec copy -bsf h264_mp4toannexb ' \
                + self.dir_name + '/' + ts_name + ' >/dev/null 2>&1'

        comm2 = 'ffmpeg -analyzeduration 30000000 -i ' + self.dir_name \
                + '/' + ts_name + ' -c copy -map 0 -f segment -segment_list ' \
                + self.upload_abspath_file + ' -segment_time 10 ' \
                + self.dir_name + '/%03d.ts >/dev/null 2>&1'

        ts_file = os.path.join(self.dir_name, ts_name)
        m3u8_file = os.path.join(self.upload_abspath_file)
        if not os.path.exists(m3u8_file):
            if not os.path.exists(ts_file):
                result1 = subprocess.Popen(comm1, shell=True)
                print "\033[96m [INFO]>> 转换到ts\033[0m"
                result1.wait()
                check_status_code('转换到ts', ts_file, result1.returncode, 0)
            result2 = subprocess.Popen(comm2, shell=True)
            print "\033[96m [INFO]>> 转换到m3u8\033[0m"
            result2.wait()
            check_status_code('转换到m3u8', m3u8_file, result2.returncode, 0)
            if remove:
                os.remove(ts_file)
                os.remove(self.flv_file)
        else:
            print "\033[93m [WARNING]>> 转换完成，直接传输文件\033[0m"

    def upload_ali_oss(self):
        """
        上传
        """
        bucket = oss2.Bucket(oss2.Auth(self._access_key_id, self._access_key_secret), self.endpoint, self.bucket_name)
        upload_file_name = os.listdir(self.dir_name)

        for index, file_name in enumerate(upload_file_name):
            file_ext = os.path.splitext(file_name)[1]
            file_num = len(upload_file_name)
            if file_ext == '.ts' or file_ext == 'm3u8':
                local_abspath_file = os.path.join(self.dir_name, file_name)
                remote_abspath_file = os.path.join('buka', self.dir_name, file_name)
                # oss2.resumable_upload(bucket, remote_abspath_file, local_abspath_file,
                #                      multipart_threshold=200 * 1024,
                #                      part_size=100 * 1024,
                #                      num_threads=4,
                #                      )  # progress_callback=percentage
                bucket.put_object_from_file(remote_abspath_file, local_abspath_file)
                rate = int(100 * (float(index) / float(file_num)))
                sys.stdout.write("\r上传： {0}%\r".format(rate))
                sys.stdout.flush()
        if remove:
            shutil.rmtree(self.dir_name)
        print "\033[92m [INFO]>> 上传到阿里云完成 \033[0m"


#class Get_URL:
#    """
#    获取需要替换URL
#    """
#    def __init__(self, url):
#        self.url = url





def program_main(upload_file_name, client_url):
    upload_qiniu_obj = UploadQiniu(upload_file_name)
    flv_file_name = upload_qiniu_obj.video_synthesis()
    upload_qiniu_obj.upload_qiniu_oss()
    upload_qiniu_obj.refresh_url()
    if client_url:
        upload_ali_obj = UploadAli(flv_file_name, client_url)
        upload_ali_obj.format_factory()
        upload_ali_obj.upload_ali_oss()


if __name__ == "__main__":

    given_file_name = sys.argv[1]
    ali_file_url = sys.argv[2]
    try:
        remove = sys.argv[3]
    except IndexError as e:
        remove = False
    finally:
        program_main(given_file_name, ali_file_url)
