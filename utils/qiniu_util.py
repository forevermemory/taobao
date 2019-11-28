from qiniu import Auth, put_file, etag,BucketManager,PersistentFop, build_op, op_save, urlsafe_base64_encode

import qiniu.config
# FFmpeg
# https://www.linuxidc.com/Linux/2011-10/45125.htm
# chorme 只支持avc的 H264格式,
# ffmpeg -i test_video_test4.mp4  -vcodec h264 test_video_ffmpeg.mp4

class QiniuStorage(object):
    # 七牛存储
    QN_ACCESS_KEY = 'mXf5Xw2YYUkZsmdka9vxlIvwFFPDM-PvL_dTPr8o'
    QN_SECRET_KEY = 'VRBujTd_a-oz21pZSuQt6NM2a3bd-ctrH1g963fJ'
    QN_BUCKET = 'taobao'

    def del_raw_pic(self,key):
        '''删除图片'''
        q = Auth(self.QN_ACCESS_KEY,self.QN_SECRET_KEY)
        bucket = BucketManager(q)
        ret, info = bucket.delete(self.QN_BUCKET, key)
        print(info)

    # def encode_video_asyn(self,key):
    def encode_video_asyn(self):
        '''#对已经上传到七牛的视频发起异步转码操作,好像并没什么用'''

        q = Auth(self.QN_ACCESS_KEY,self.QN_SECRET_KEY)
        key = 'test_video_test.mp4'
        # 是使用的队列名称,不设置代表不使用私有队列，使用公有队列。
        # pipeline = 'your_pipeline'
        # 要进行转码的转码操作。
        # fops = 'avthumb/mp4/s/640x360/vb/1.25m'
        fops = 'avthumb/mp4/vcodec/libx264|saveas/'
        # 可以对转码后的文件进行使用saveas参数自定义命名，当然也可以不指定文件会默认命名并保存在当前空间
        saveas_key = urlsafe_base64_encode(self.QN_BUCKET+':n'+key)
        fops = fops+'|saveas/'+saveas_key
        pfop = PersistentFop(q, self.QN_BUCKET)
        ops = []
        ops.append(fops)
        ret, info = pfop.execute(key, ops, 1)
        print(info)
        print('-------------')
        print(ret)

    def upload_video_and_encode(self,key):
        '''上传视频同时将视频转成h264格式'''
        q = Auth(self.QN_ACCESS_KEY,self.QN_SECRET_KEY)
        # key = 'test_video_test8.mp4'
        # 设置转码参数
        fops = 'avthumb/mp4/vcodec/h264'
        # 通过添加'|saveas'参数，指定处理后的文件保存的bucket和key，不指定默认保存在当前空间，bucket_saved为目标bucket，bucket_saved为目标key
        # saveas_key = urlsafe_base64_encode('bucket_saved:bucket_saved')
        saveas_key = urlsafe_base64_encode(self.QN_BUCKET+':'+key)
        fops = fops+'|saveas/'+saveas_key
        # 在上传策略中指定fobs和pipeline
        policy={
        'persistentOps':fops,
        # 'persistentPipeline':pipeline
        }
        token = q.upload_token(self.QN_BUCKET, key, 3600, policy)
        # 视频所在的本地路径
        localfile = '/tmp/' + key
        ret, info = put_file(token, key, localfile)
        print(info)

    def get_qiniu_auth(self,key):
        '''上传图片'''
        # http://tbcdn.tajansoft.com/+key    访问地址 在七牛控制台配置
      
        q = Auth(self.QN_ACCESS_KEY,self.QN_SECRET_KEY)
        token = q.upload_token(self.QN_BUCKET, key, 3600)
        # 要上传文件的本地路径
        localfile = '/tmp/'+key
        ret, info = put_file(token, key, localfile)
        return ret
        '''
        print(info)
        _ResponseInfo__response:<Response [200]>, exception:None, status_code:200, text_body:{"hash":"FmAHFeFk0y79QPP1X2q-KlG6NltR","key":"d.jpg"}, req_id:CeUAAABBKmq6xsEV, x_log:X-Log

        print(ret) # {'hash': 'FmAHFeFk0y79QPP1X2q-KlG6NltR', 'key': 'd.jpg'}
        print('utils---------')
        '''
# if __name__ == "__main__":
#     q = QiniuStorage()
#     # q.encode_video_asyn()
#     # q.del_raw_pic('test_video_test2.mp4')
#     # q.upload_video_and_encode()
#     q.upload_video_and_encode()
#     # q.get_qiniu_auth('test_video_test4.mp4')
#     print('上传ok')


# if __name__ == "__main__":
#     q = QiniuStorage()
#     for i in range(0,10):
#         if i >1:
#             q.get_qiniu_auth('wm_pic_2_'+str(i)+'.jpeg')
#             print('上床第 %d ok',i)