from django.shortcuts import render
from .models import GoodsInfo
import openpyxl,json
from django.http import HttpResponse,JsonResponse
from django.views.generic import View
from django.db import connection
from django.db.models import Count
from django.views.decorators.http import require_POST
from urllib import parse
from . import models

from django_redis import get_redis_connection

# 上传excel文件
class UploadExcelView(View):
    def get(self,request):
        return render(request, 'upload.html')

    def post(self,request): 
        obj = request.FILES.get('myfile')
        if obj:
            import os
            print(obj.name)   
            obj_name = obj.name
            extension_name = obj_name.split('.')[-1]
            if extension_name not in ['xlsx']:
                return HttpResponse('文件类型不正确')
            path = os.path.join(BASE_DIR, 'media', obj.name)
            print(path)   
            f = open(path, 'wb')
            for chunk in obj.chunks():
                f.write(chunk)
            open_excel_save_to_db(path)
            f.close()
            return HttpResponse('上传成功')
        return HttpResponse('请上传文件')
        



