from django.shortcuts import render,redirect,reverse,get_object_or_404
from django.views.generic import View
from django.http import JsonResponse
from django.core import serializers
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login,logout,authenticate
from cpm.settings import QINIU_BASE_DOMAIN

import os
import json
from utils.compress_image import compress_image
from utils.baidu_image_retrieve import BaiduImageSearch
from cpm.models import Good,GoodsSku




class MobileIndexView(View):
    '''显示首页'''
    def get(self,request):
        return render(request,'index_mobile.html')


@method_decorator(csrf_exempt, name='dispatch')
class MobileLoginView(View):
    '''登录接口'''
    def post(self,request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if not user:
            return JsonResponse({'code':'1','msg':'用户名或密码错误'})
        login(request,user)
        return JsonResponse({'code':'0','msg':'ok'})


class MobileQueryView(View):
    '''编码查询产品'''
    def get(self,request):
        good_code = request.GET.get('good_code')
        good_sku_code = request.GET.get('good_sku_code')

        # 先是根据产品编码查询
        if good_code:
            try:
                good = Good.objects.filter(code=int(good_code)).first()
                if not good:
                    return JsonResponse({'code':'2','msg':'不存在该产品,请重试'})
                skus = good.goods_skus.all()
                if not skus:
                    skus = []
            except Exception as err1:
                print(err1)
                return JsonResponse({'code':'3','msg':'fail'})

            skus_arr = []
            for sku in skus:
                temp = {}
                temp['sku_id'] = sku.id
                temp['sku_code'] = sku.sku_code
                temp['sku_name'] = sku.sku_name
                temp['sku_image'] = QINIU_BASE_DOMAIN+sku.sku_image
                skus_arr.append(temp)
            context = {
                'code':'0',
                'good_name':good.name,
                'skus':skus_arr,
            }
            return JsonResponse(context)

        if good_sku_code:
            # 19001-001
            temp_arr = good_sku_code.split('-')
            try:
                good = Good.objects.filter(code=int(temp_arr[0])).first()
                if not good:
                    return JsonResponse({'code':'5','msg':'good is not exist'})
                sku = GoodsSku.objects.filter(sku_good=good,sku_code=temp_arr[1]).first()
                if not sku:
                    return JsonResponse({'code':'7','msg':'sku is not exist'})
            except Exception as err2:
                print(err2)
                return JsonResponse({'code':'3','msg':'fail'})
            temp = {}
            temp['sku_id'] = sku.id
            temp['sku_name'] = sku.sku_name
            temp['sku_image'] = QINIU_BASE_DOMAIN+'/'+sku.sku_image
            context = {
                'code':'0',
                'good_name':good.name,
                'skus':temp,
            }
            return JsonResponse(context)
                


@method_decorator(csrf_exempt, name='dispatch')
class MobileImageSearchView(View):
    def get(self,request):
        '''根据sku_id查询sku和对应的good'''
        sku_id = request.GET.get('sku_id')
        try:
            sku = GoodsSku.objects.get(pk=int(sku_id))
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'fail'})
        context = {
            'sku_code':sku.sku_code,
            'sku_name':sku.sku_name,
            'good_code':sku.sku_good.code,
            'good_name':sku.sku_good.name,
        }
        return JsonResponse({'code':'0','res':context})

    def post(self,request):
        '''图像搜索功能'''
        image = request.FILES.get('image')
        if not image:
            return JsonResponse({'code':'1','msg':'please upload file'})
        # 暂存到本地
        # big_path = '/tmp/'+'big_'+image.name
        path = '/tmp/'+image.name
        with open(path, 'wb+') as f:
            for chunk in image.chunks():
                f.write(chunk)  
        # 超过3M压缩图片 
        if image.size/1024/1024 > 3:
            compress_image(path)
        # # 调用百度图像搜索
        baidu = BaiduImageSearch()
        res = baidu.search(path)
        try:
            # {'log_id': 1410600654088225875, 'error_code': 216202, 'error_msg': 'image size error'}
            result = res['result'][0:10]  
            length = res['result_num']
        except Exception as err:
            result = []
            return JsonResponse({'code':'8','msg':'图片过大,或者类型错误,请重试'})


        new_result = []
        for r in result:
            temp_dict = {}
            temp_dict['score'] = '%.2f' % float(r['score']) 
            brief = json.loads(r['brief'])
            good = Good.objects.get(pk=int(brief['good_id']))
            temp_dict['url'] = QINIU_BASE_DOMAIN +'/'+ brief['key'].split('/')[-1]
            temp_dict['good_id'] = brief['good_id']
            temp_dict['sku_id'] = brief['sku_id']
            temp_dict['code'] = good.code
            temp_dict['name'] = good.name
            sku = GoodsSku.objects.get(pk=int(brief['sku_id']))
            temp_dict['sku_name'] = sku.sku_name
            temp_dict['sku_code'] = sku.sku_code
            new_result.append(temp_dict)
        return JsonResponse({'code':'0','msg':'ok','res':new_result})


