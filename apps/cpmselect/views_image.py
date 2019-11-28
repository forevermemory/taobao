from django.shortcuts import render
from utils.login_required import LoginRequiredMixin
from django.views.generic import View

from utils.baidu_image_retrieve import BaiduImageSearch
from datetime import datetime
import os
from .models import ImageUploadModel
from cpm.settings import BASE_DIR

# 上传图片
class ImageUpload(LoginRequiredMixin, View):
    def get(self,request):
        context = {
            'msg':'上传图片',
            'upload':True
        }
        return render(request, 'select/index/image_upload.html',context=context)     

    def post(self,request):

        o = BaiduImageSearch()

        file_list = request.FILES.getlist("images")
        if not file_list:
            return render(request, 'select/index/image_upload.html',{'msg':'请上传文件','upload':True})     

        for i,f1 in enumerate(file_list):
            today = datetime.today()
            timestamp = str(today.timestamp()*1000)[0:13]#获得当前日期 13位时间戳
            file_name = timestamp +'.jpg'
            f1.name = file_name
            # 存到本地和数据库
            img = ImageUploadModel(image=f1)
            img.save()

            month = '%02d' % today.month
            day = '%02d' % today.day

            file_path = os.path.join(BASE_DIR,'front','dist','images',str(today.year),month,day,file_name)
            # 调用百度图像存储
            res = o.upload(file_path)
            print(res)
            # http://ai.baidu.com/docs#/ImageSearch-Python-SDK/99e124a4
            # 上传失败处理
            # {'log_id': 382134008565176669, 'error_code': 216101, 'error_msg': 'param brief not exist'}
            # 成功的返回{'log_id': 6465095245776441021, 'cont_sign': '4186249414,161268738'}


        context = {
            'msg':'图片上传成功',
            'upload':True
        }
        return render(request, 'select/index/image_upload_success.html',context=context)     





# 搜索图片
class ImageSearch(LoginRequiredMixin, View):
    def get(self,request):
        context = {
            'msg':'搜索图片',
            'search':True
        }

        return render(request, 'select/index/image_search.html',context=context)     


    def post(self,request):
        image = request.FILES.get('image')  # django.core.files.uploadedfile.InMemoryUploadedFile

        file_path_name = os.path.join('/tmp',image.name)
        with open(file_path_name, 'wb+') as f:
            for chunk in image.chunks():
                f.write(chunk)  

        # 调用百度图像搜索
        o = BaiduImageSearch()
        res = o.search(file_path_name)  # dict
        top10 = res['result'][0:10]  # list
        for top in top10:
            top['brief'] = top['brief'][-35:] 
            top['score'] = '%.2f' %  top['score']


        context = {
                'msg':'前十结果为:',
                'search':True,
                'top10':top10
            }
        return render(request, 'select/index/image_search_success.html',context=context)     






