from django.shortcuts import render,get_object_or_404,reverse,redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.http import JsonResponse,QueryDict,FileResponse,HttpResponse,Http404
from cpm.settings import PAGE_SIZE,BASE_DIR
from django.core.paginator import Paginator
from django.core import serializers

from django.utils.http import urlquote
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_redis import get_redis_connection

from django.db import transaction
from cpm.models import Supplier,TagChangjing,TagDingwei,GoodsBrand,Good,Avenue,Shop,GoodsSku,Category,SonCategory
from cpmauth.models import UserExtension,Role

from utils.login_required import LoginRequiredMixin
from utils.page_util import get_pagination_data
from utils.baidu_image_retrieve import BaiduImageSearch
import json,os,pickle
from datetime import datetime
import pandas as pd
import pickle
# import jwt


class BasicIndexView(LoginRequiredMixin,View):
    '''工具的首页－－－'''
    def get(self,request):
        return render(request,'basic/index.html',{'index':True,'msg':'index'})


##################供应商start#################################
@method_decorator(csrf_exempt, name='dispatch')
class SupplierView(LoginRequiredMixin,View):
    '''供应商 首页 查询一个 删除一个 查询是否关联'''
    def get(self,request):
        # 查询一个
        supplier_id = request.GET.get('supplier_id')
        if supplier_id:
            try:
                supplier = Supplier.objects.get(pk=supplier_id)
                # {'brand':serializers.serialize('json',brand)} 只能序列化多个　queryset
                temp_supplier= {
                    'code' : supplier.code,
                    'name' : supplier.name,
                    'concat' : supplier.concat,
                    'phone' : supplier.phone,
                    'telephone' : supplier.telephone,
                    'email' : supplier.email,
                    'address' : supplier.address,
                    'note' : supplier.note,
                    'id': supplier.id,
                }
                return JsonResponse({'code':'0','supplier':json.dumps(temp_supplier)})
            except Exception as err:
                return JsonResponse({'code':'1','msg':'err'})

        page = int(request.GET.get('p',1))
        items = Supplier.objects.all().order_by('code')
        # 分页相关
        len_items = len(items)  # 总的记录数
        paginator = Paginator(items,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1

        page_obj = paginator.page(page)
        items = page_obj.object_list
        context = {
            'supplier':True,
            'msg':'供应商管理',
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'last_pages':len_items/PAGE_SIZE +1,
        }
        context_data = get_pagination_data(paginator,page_obj)
        context.update(context_data)
        return render(request,'basic/supplier.html',context=context)

    def post(self,request):
        '''删除供应商'''
        supplier_id = request.POST.get('id')
        try:
            supplier = Supplier.objects.get(pk=int(supplier_id))
            supplier.delete()
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'操作失败,请重试'})
        return JsonResponse({'code':'0','msg':'ok'})

    def put(self,request):
        '''判断供应商是否被商品关联'''
        put = QueryDict(request.body)
        supplier_id = put.get('id')
        good = Good.objects.filter(suppiler__id__exact=int(supplier_id)).first()
        if not good:
            return JsonResponse({'code':'0','msg':'ok','id':supplier_id})
        return JsonResponse({'code':'1','msg':'该品牌已经被产品引用, 无法删除!'})


class GoodsAddSupplierView(LoginRequiredMixin,View):
    '''供应商添加 更新'''
    def get(self,request):
        '''添加供应商'''
        code = request.GET.get('code','')
        name = request.GET.get('name','')
        concat = request.GET.get('concat','')
        phone = request.GET.get('phone','')
        telephone = request.GET.get('telephone','')
        email = request.GET.get('email','')
        address = request.GET.get('address','')
        note = request.GET.get('note','')

        if Supplier.objects.filter(code=code).first():
            return JsonResponse({'code':'1','msg':'编码已存在'})


        item = Supplier.objects.create(
            code = code,
            name = name,
            concat = concat,
            phone = phone,
            telephone = telephone,
            email = email,
            address = address,
            note = note,
        )
        # ,content={'brand':True,'msg':'品牌管理'}
        return JsonResponse({'code':'0','msg':'ok'})


    def post(self,request):
        '''更新供应商'''
        s_id = request.POST.get('id','')
        code = request.POST.get('code','')
        name = request.POST.get('name','')
        concat = request.POST.get('concat','')
        phone = request.POST.get('phone','')
        telephone = request.POST.get('telephone','')
        email = request.POST.get('email','')
        address = request.POST.get('address','')
        note = request.POST.get('note','')

        if Supplier.objects.filter(code=code).first().id != int(s_id):
            return JsonResponse({'code':'2','msg':'编码已存在'})
        try:
            supplier = Supplier.objects.get(pk=s_id)
            supplier.code = code
            supplier.name = name
            supplier.concat = concat
            supplier.phone = phone
            supplier.telephone = telephone
            supplier.email = email
            supplier.address = address
            supplier.note = note
            supplier.save()
        except Exception as err:
            return JsonResponse({'code':'1','msg':'操作失败，请重试'})
        return JsonResponse({'code':'0','msg':'ok'})

        
####################供应商end#########################################
####################品牌start#########################################
@method_decorator(csrf_exempt, name='dispatch')
class GoodsBrandView(LoginRequiredMixin,View):
    '''查询品牌'''
    def get(self,request):
        # 查询一个
        brand_id = request.GET.get('brand_id')
        if brand_id:
            try:
                brand = GoodsBrand.objects.get(pk=brand_id)
                # {'brand':serializers.serialize('json',brand)} 只能序列化　queryset
                temp_brand = {
                    'name':brand.name,
                    'code':brand.code,
                    'id':brand.id,
                }
                return JsonResponse({'code':'0','brand':json.dumps(temp_brand)})
            except Exception as err:
                return JsonResponse({'code':'1','msg':'err'})
        page = int(request.GET.get('p',1))
        items = GoodsBrand.objects.all().order_by('created_at')
        # 分页相关
        len_items = len(items)  # 总的记录数
        paginator = Paginator(items,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1

        page_obj = paginator.page(page)
        items = page_obj.object_list
        context = {
            'brand':True,
            'msg':'品牌管理',
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'last_pages':len_items/PAGE_SIZE +1,
        }
        context_data = get_pagination_data(paginator,page_obj)
        context.update(context_data)
        return render(request,'basic/brand.html',context=context)

    def post(self,request):
        '''判断品牌是否被商品关联'''
        brand_id = request.POST.get('id')
        good = Good.objects.filter(brand__id__exact=int(brand_id)).first()
        if not good:
            return JsonResponse({'code':'0','msg':'ok','id':brand_id})
        return JsonResponse({'code':'1','msg':'已经被产品引用, 无法删除!'})

    def delete(self,request):
        '''删除品牌'''
        delete = QueryDict(request.body)
        brand_id = delete.get('id')
        print(brand_id)
        print(brand_id)
        # brand_id = request.GET.get('id')
        try:
            brand = GoodsBrand.objects.get(pk=int(brand_id))
            brand.delete()
        except Exception as err:
            return JsonResponse({'code':'1','msg':'操作失败,请重试'})
        return JsonResponse({'code':'0','msg':'ok'})


class GoodsAddBrandView(LoginRequiredMixin,View):
    '''添加或者更新品牌'''
    def get(self,request):
        '''添加品牌'''
        brand = request.GET.get('brand','')
        try:
            item = GoodsBrand.objects.create(name=brand)
            code = self.get_brand_code(item)
            item.code = code
            item.save()
        except Exception as err:
            return JsonResponse({'code':'1','msg':'操作失败,请重试'})
        return JsonResponse({'code':'0','msg':'ok'})

    def get_brand_code(self,item):
        # 00001 -99999　我生成
        int_id = item.id
        s = '%05d' % int_id
        return s

    def post(self,request):
        '''更新品牌'''
        brand_id = request.POST.get('brand_id')
        name = request.POST.get('name')
        try:
            brand = GoodsBrand.objects.get(pk=int(brand_id))
            brand.name = name
            brand.save()
        except Exception as err:
            return JsonResponse({'code':'1','msg':'操作失败,请重试'})
        return JsonResponse({'code':'0','msg':'ok'})




#######################品牌end#####################################

#######################场景start#####################################
@method_decorator(csrf_exempt, name='dispatch')
class TagChangjingView(LoginRequiredMixin,View):
    '''标签-- 场景 列表  查询一个 判断定位是否被商品关联 删除(暂时)'''
    def get(self,request):
        # 查询一个
        changjing_id = request.GET.get('changjing_id')
        if changjing_id:
            try:
                changjing = TagChangjing.objects.get(pk=changjing_id)
                # {'brand':serializers.serialize('json',brand)} 只能序列化多个　queryset
                temp_changjing= {
                    'name' : changjing.name,
                    'id': changjing.id,
                }
                return JsonResponse({'code':'0','changjing':json.dumps(temp_changjing)})
            except Exception as err:
                return JsonResponse({'code':'1','msg':'err'})

        page = int(request.GET.get('p',1))
        items = TagChangjing.objects.all().order_by('created_at')
        # 分页相关
        len_items = len(items)  # 总的记录数
        paginator = Paginator(items,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1

        page_obj = paginator.page(page)
        items = page_obj.object_list
        context = {
            'changjing':True,
            'msg':'标签场景管理',
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'last_pages':len_items/PAGE_SIZE +1,
        }
        context_data = get_pagination_data(paginator,page_obj)
        context.update(context_data)
        return render(request,'basic/changjing.html',context=context)

    def post(self,request):
        '''判断定位是否被商品关联'''
        changjing_id = request.POST.get('id')
        good = Good.objects.filter(changjing__id__exact=int(changjing_id)).first()
        if not good:
            return JsonResponse({'code':'0','msg':'可以删除','id':changjing_id})
        return JsonResponse({'code':'1','msg':'已经被产品引用, 无法删除!'})

    def delete(self,request):
        '''删除场景'''
        put = QueryDict(request.body)
        changjing_id = put.get('id')
        try:
            changjing = TagChangjing.objects.get(pk=int(changjing_id))
            changjing.delete()
        except Exception as err:
            return JsonResponse({'code':'1','msg':'操作失败,请刷新重试'})
        return JsonResponse({'code':'0','msg':'ok'})


class GoodsAddTagChangjingView(LoginRequiredMixin,View):
    '''添加场景'''
    def get(self,request):
        try:
            changjing = request.GET.get('changjing','')
            TagChangjing.objects.create(name=changjing)
        except Exception as err:
            return JsonResponse({'code':'1','msg':'操作失败,请刷新重试'})
        return JsonResponse({'code':'0','msg':'ok'})

    def post(self,request):
        '''更新场景名称'''
        changjing_id = request.POST.get('changjing_id')
        name = request.POST.get('name')
        try:
            changjing = TagChangjing.objects.get(pk=int(changjing_id))
            changjing.name = name
            changjing.save()
        except Exception as err:
            return JsonResponse({'code':'1','msg':'操作失败,请刷新重试'})
        return JsonResponse({'code':'0','msg':'ok'})
#######################场景end#####################################
#######################定位start#####################################

@method_decorator(csrf_exempt, name='dispatch')
class TagDingweiView(LoginRequiredMixin,View):
    '''标签-- 定位'''
    def get(self,request):
        # 查询一个
        dingwei_id = request.GET.get('dingwei_id')
        if dingwei_id:
            try:
                dingwei = TagDingwei.objects.get(pk=dingwei_id)
                temp_dingwei= {
                    'name' : dingwei.name,
                    'id': dingwei.id,
                }
                return JsonResponse({'code':'0','dingwei':json.dumps(temp_dingwei)})
            except Exception as err:
                return JsonResponse({'code':'1','msg':'err'})

        page = int(request.GET.get('p',1))
        items = TagDingwei.objects.all().order_by('created_at')
        # 分页相关
        len_items = len(items)  # 总的记录数
        paginator = Paginator(items,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1

        page_obj = paginator.page(page)
        items = page_obj.object_list
        context = {
            'dingwei':True,
            'msg':'标签定位管理',
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'last_pages':len_items/PAGE_SIZE +1,
        }
        context_data = get_pagination_data(paginator,page_obj)
        context.update(context_data)
        return render(request,'basic/dingwei.html',context=context)

    def post(self,request):
        '''判断定位是否被商品关联'''
        dingwei_id = request.POST.get('id')
        good = Good.objects.filter(dingwei__id__exact=int(dingwei_id)).first()
        if not good:
            return JsonResponse({'code':'0','msg':'可以删除','id':dingwei_id})
        return JsonResponse({'code':'1','msg':'已经被产品引用, 无法删除!'})

    def delete(self,request):
        '''删除一个标签的定位'''
        put = QueryDict(request.body)
        dingwei_id = put.get('id')
        try:
            dingwei = TagDingwei.objects.get(pk=int(dingwei_id))
            dingwei.delete()
        except Exception as err:
            return JsonResponse({'code':'1','msg':'操作失败，请重试'})
        return JsonResponse({'code':'0','msg':'ok'})

class GoodsAddTagDingweiView(LoginRequiredMixin,View):
    '''添加定位'''
    def get(self,request):
        try:
            dingwei = request.GET.get('dingwei','')
            TagDingwei.objects.create(name=dingwei)
        except Exception as err:
            return JsonResponse({'code':'1','msg':'操作失败,请刷新重试'})
        return JsonResponse({'code':'0','msg':'ok'})

    def post(self,request):
        '''更新定位'''
        dingwei_id = request.POST.get('dingwei_id')
        name = request.POST.get('name')
        try:
            dingwei = TagDingwei.objects.get(pk=int(dingwei_id))
            dingwei.name = name
            dingwei.save()
        except Exception as err:
            return JsonResponse({'code':'1','msg':'操作失败,请刷新重试'})
        return JsonResponse({'code':'0','msg':'ok'})

#######################定位end#####################################
#######################员工start#####################################

@method_decorator(csrf_exempt, name='dispatch')
class AdminCpmuserView(LoginRequiredMixin,View):
    '''员工'''
    def get(self,request):
        # 查询一个
        user_id = request.GET.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                ext = user.extension
                roles = ext.role.all()
                temp = {}
                temp['id'] = user_id
                temp['username'] = user.username
                temp['email'] = user.email
                temp['name'] = ext.name
                temp['code'] = ext.code
                temp['telephone'] = ext.telephone
                temp['address'] = ext.address
                temp['address_now'] = ext.address_now
                temp['xueli'] = ext.xueli

                role_arr = []
                for role in roles:
                    role_dict = {}
                    role_dict['id'] = role.id
                    role_dict['desc'] = role.desc
                    role_arr.append(role_dict)
                
                temp['roles'] = role_arr
                # {'brand':serializers.serialize('json',brand)} 只能序列化多个　queryset
                return JsonResponse({'code':'0','user':temp})
            except Exception as err:
                return JsonResponse({'code':'1','msg':'操作失败,请刷新重试'})

        page = int(request.GET.get('p',1))
        items = User.objects.all().order_by('id')
        for item in items:
            roles = item.extension.role.all()
            setattr(item,'roles',roles)
        # 分页相关
        len_items = len(items)  # 总的记录数
        paginator = Paginator(items,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1

        page_obj = paginator.page(page)
        items = page_obj.object_list
        context = {
            'user':True,
            'msg':'员工管理',
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'last_pages':len_items/PAGE_SIZE +1,
        }
        context_data = get_pagination_data(paginator,page_obj)
        context.update(context_data)
        return render(request,'basic/user.html',context=context)

    def post(self,request):
        '''管理员重置密码'''
        user_id = request.POST.get('user_id','')
        new_password = request.POST.get('new_password','')
        try:
            user = User.objects.get(pk=int(user_id))
            user.set_password(new_password)
            user.save()
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'update fail,please try again'})
        return JsonResponse({'code':'0','msg':'ok'})

    def delete(self,request):
        '''删除员工  检查是否可以删除  暂时不用这个接口'''
        delete = QueryDict(request.body)
        user_id = delete.get('id')
        try:
            user = User.objects.get(pk=int(user_id))
            # user.delete()
        except Exception as err:
            return JsonResponse({'code':'1','msg':'delete fail,please try again'})
        return JsonResponse({'code':'0','msg':'ok'})



class AdminAddCpmuserView(LoginRequiredMixin,View):
    '''添加员工'''
    # | id | password| last_login| is_superuser | username | first_name | last_name | email
    # 
    @transaction.atomic
    def get(self,request):
        username = request.GET.get('username','')
        password = request.GET.get('password','')
        email = request.GET.get('email','')
        name = request.GET.get('name','')
        role_ids = request.GET.get('role_ids','') # 1,2,3,
        telephone = request.GET.get('telephone','')
        code = request.GET.get('code','')
        address = request.GET.get('address','')
        address_now = request.GET.get('address_now','')
        xueli = request.GET.get('xueli','')
        # 查询 code是否存在
        exist = User.objects.filter(extension__code = code).first()
        if exist:
            return JsonResponse({'code':'6','msg':'编码已存在'})

        # 设置事务保存点
        save_id = transaction.savepoint()
        user = User.objects.create_user(
            username = username,
            password = password,
            is_staff = 1,
            email = email,
        )
        # 用户扩展信息
        try:
            ext = user.extension
            ext.telephone = telephone
            ext.name = name
            ext.code = code
            ext.address = address
            ext.address_now = address_now
            ext.xueli = xueli
            # 设置员工和角色多对多关系
            role_arr = role_ids.split(',')
            for role_id in role_arr:
                if role_id != '':
                    role = Role.objects.get(pk=int(role_id))
                    ext.role.add(role)
                
            user.save()
            transaction.savepoint_commit(save_id)
            return JsonResponse({'code':'0','msg':'ok'})
        except Exception as err:
            transaction.savepoint_rollback(save_id)
            print(err)
            return JsonResponse({'code':'3','msg':'请重试'})

    def post(self,request):
        '''更新员工'''
        user_id = request.POST.get('user_id','')
        email = request.POST.get('email','')
        name = request.POST.get('name','')
        role_ids = request.POST.get('role_ids','') # 1,2,3
        telephone = request.POST.get('telephone','')
        code = request.POST.get('code','')
        address = request.POST.get('address','')
        address_now = request.POST.get('address_now','')
        xueli = request.POST.get('xueli','')
        is_change_role = request.POST.get('is_change_role')
        # 查询 code是否存在
        exist = User.objects.filter(extension__code = code).first()
        if exist:
            if exist.id != int(user_id):
                return JsonResponse({'code':'6','msg':'编码已存在'})
        # 用户扩展信息
        try:
            user = User.objects.get(pk=int(user_id))
            user.email = email
            ext = user.extension
            ext.telephone = telephone
            ext.name = name
            ext.code = code
            ext.address = address
            ext.address_now = address_now
            ext.xueli = xueli
            # 判断是否变更了员工的角色
            if is_change_role == 'true':
                # 先移除所有的关联关系
                ext.role.clear()
                role_arr = role_ids.split(',')
                for role_id in role_arr:
                    if role_id != '':
                        role = Role.objects.get(pk=int(role_id))
                        ext.role.add(role)

            user.save()
        except Exception as err:
            return JsonResponse({'code':'2','msg':'err,please try again!'})
        return JsonResponse({'code':'0','msg':'ok'})



#######################员工end#####################################
#######################七牛start#####################################
@method_decorator(csrf_exempt, name='dispatch')
class QiniuPicView(View):
    '''上传图片工具'''
    def get(self,request):
        try:
            from qiniu import Auth
            from qiniu import BucketManager
            # QN_ACCESS_KEY = 'mXf5Xw2YYUkZsmdka9vxlIvwFFPDM-PvL_dTPr8o'
            # QN_SECRET_KEY = 'VRBujTd_a-oz21pZSuQt6NM2a3bd-ctrH1g963fJ'
            # #初始化Auth状态
            # q = Auth(QN_ACCESS_KEY, QN_SECRET_KEY)
            # #初始化BucketManager
            # bucket = BucketManager(q)
            # #你要测试的空间， 并且这个key在你空间中存在
            # bucket_name = 'taobao'
            # key = 'test1.png'
            # #获取文件的状态信息
            # ret, info = bucket.stat(bucket_name, key)
            # print(info)
            # # _ResponseInfo__response:<Response [200]>, exception:None, status_code:200, text_body:{"fsize":14572,"hash":"Fi_xn-yyz2nBrh0xK1K6J4e5jhQr","md5":"50420c1cf94e96675a0e63912ab0d229","mimeType":"image/png","putTime":15674322554585648,"type":0}, 
            # print(info)
            # print(info)
            from utils.qiniu_util import QiniuStorage
            q = QiniuStorage().get_qiniu_auth('d.jpg')
   
            return JsonResponse({'msg':'ok'})
        except Exception as identifier:
            return JsonResponse({'msg':'err'})
    def post(self,request):
        print('post--------------')
        filename1 = request.GET.get('filename')
        filesize1 = request.GET.get('filesize')
        filename = request.POST.get('filename')
        filesize = request.POST.get('filesize')
        print(request.GET)
        print(filename1)
        print(filesize1)
        print(filename)
        print(filesize)
        return JsonResponse({'filename':filename,'filesize':filesize})
#######################七牛end#####################################
#######################avenue渠道start#############################

@method_decorator(csrf_exempt, name='dispatch')
class AvenueAddView(LoginRequiredMixin,View):
    '''渠道管理'''
    def get(self,request):
        '''渠道首页 '''
        page = int(request.GET.get('p',1))
        items = Avenue.objects.all().order_by('code')
        # 分页相关
        len_items = len(items)  # 总的记录数
        paginator = Paginator(items,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1
        page_obj = paginator.page(page)
        items = page_obj.object_list
        context = {
            'avenue':True,
            'msg':'渠道管理',
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'last_pages':len_items/PAGE_SIZE +1,
        }
        context_data = get_pagination_data(paginator,page_obj)
        context.update(context_data)
        return render(request,'basic/avenue.html',context=context)
    def post(self,request):
        '''新增渠道'''
        code = request.POST.get('code')
        name = request.POST.get('name')
        exist = Avenue.objects.filter(code = int(code)).first()
        if exist:
            return JsonResponse({'code':'2','msg':'编码已存在'})
        try:
            Avenue.objects.create(
                code = int(code),
                name = name
            )
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'操作失败'})
        return JsonResponse({'code':'0','msg':'ok'})

    def put(self,request):
        '''编辑渠道'''
        put = QueryDict(request.body)
        a_id = put.get('a_id')
        code = put.get('code')
        name = put.get('name')
        exist = Avenue.objects.filter(code = int(code)).first()
        if exist:
            if exist.id !=int(a_id):
                return JsonResponse({'code':'2','msg':'编码已存在'})
        try:
            avenue = Avenue.objects.get(pk=int(a_id))
            avenue.code = int(code)
            avenue.name = name
            avenue.save()
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'操作失败'})
        return JsonResponse({'code':'0','msg':'ok'})



#######################avenue渠道end###############################
#######################shop店铺start#############################
@method_decorator(csrf_exempt, name='dispatch')
class ShopCrudView(LoginRequiredMixin,View):
    '''店铺的crud'''
    def get(self,request):
        '''店铺首页'''
        page = int(request.GET.get('p',1))
        items = Shop.objects.all().order_by('code')
        # 分页相关
        len_items = len(items)  # 总的记录数
        paginator = Paginator(items,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1
        page_obj = paginator.page(page)
        items = page_obj.object_list
        context = {
            'shop':True,
            'avenues':Avenue.objects.all(),
            'msg':'店铺管理',
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'last_pages':len_items/PAGE_SIZE +1,
        }
        context_data = get_pagination_data(paginator,page_obj)
        context.update(context_data)
        return render(request,'basic/shop.html',context=context)

    def post(self,request):
        '''新增店铺'''
        avenue_id = request.POST.get('avenue_id')
        code = request.POST.get('code')
        name = request.POST.get('name')
        sub_name = request.POST.get('sub_name')
        link = request.POST.get('link')
        exist = Shop.objects.filter(code = int(code)).first()
        if exist:
            return JsonResponse({'code':'2','msg':'编码已存在'})
        try:
            avenue = Avenue.objects.get(pk=int(avenue_id))
            Shop.objects.create(
                code = int(code),
                name = name,
                sub_name = sub_name,
                link = link,
                avenue = avenue,
            )
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'操作失败'})
        return JsonResponse({'code':'0','msg':'ok'})

    def put(self,request):
        '''编辑店铺'''
        put = QueryDict(request.body)
        shop_id = put.get('shop_id')
        avenue_id = put.get('avenue_id')
        code = put.get('code')
        name = put.get('name')
        sub_name = put.get('sub_name')
        link = put.get('link')
        exist = Shop.objects.filter(code = int(code)).first()
        if exist:
            if exist.id !=int(shop_id):
                return JsonResponse({'code':'2','msg':'编码已存在'})
        try:
            shop = Shop.objects.get(pk=int(shop_id))
            avenue = Avenue.objects.get(pk=int(avenue_id))
            shop.avenue = avenue
            shop.code = int(code)
            shop.name = name
            shop.sub_name = sub_name
            shop.link = link
            shop.save()
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'操作失败'})
        return JsonResponse({'code':'0','msg':'ok'})



#######################shop店铺end###############################
#######################cate start  ###############################
@method_decorator(csrf_exempt, name='dispatch')
class CpmCategory(LoginRequiredMixin,View):
    def get(self,request):
        page = int(request.GET.get('p',1))
        is_export = request.GET.get('is_export')
        if is_export == '1':
            # 导出当前的csv所有数据
            from django.db import connection
            sql ='select cid,name,path from t_category where is_parent = 0;'
            my_son_cate = pd.read_sql_query(sql,connection)
            filename = '品类列表.csv'
            file_path = os.path.join(BASE_DIR, 'media', 'download', filename)
            my_son_cate.to_csv(file_path,index=False)
            # 生成csv 返回
            files = open(file_path ,'rb')  
            response = FileResponse(files) 
            response['Content-Type']=' application/octet-stream'  
            response['Content-Disposition'] = 'attachment;filename="%s"'%(urlquote(filename))
            return response 
        items_first = SonCategory.objects.filter(level=1).order_by('cid')

        # 分页相关
        len_items = len(items_first)  # 总的记录数
        paginator = Paginator(items_first,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1
        page_obj = paginator.page(page)
        items_first = page_obj.object_list
        for item in items_first:
            seconds = SonCategory.objects.filter(level=2,parent_id=int(item.cid))
            setattr(item,'second',seconds)

            for second in seconds:
                thirds = SonCategory.objects.filter(level=3,parent_id=int(second.cid))
                setattr(second,'third',thirds)
                for third in thirds:
                    forths = SonCategory.objects.filter(level=4,parent_id=int(third.cid))
                    setattr(third,'forth',forths)
                    
                
        

        context = {
            'cate':True,
            'msg':'品类管理',
            'items_first': items_first,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'last_pages':len_items/PAGE_SIZE +1,
        }
        context_data = get_pagination_data(paginator,page_obj)
        context.update(context_data)
        return render(request,'basic/category.html',context=context)

    def delete(self,request):
        '''删除某个品类'''
        # cid = request.POST.get('cate_id')
        delete_ = QueryDict(request.body)
        cid = delete_.get('cate_id')
        try:
            cate = SonCategory.objects.get(pk=int(cid))
            cate.delete()
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'操作失败'})
        return JsonResponse({'code':'0','msg':'ok'})

    def put(self,request):
        '''新增某个品类'''
        put = QueryDict(request.body)
        cate_id = put.get('final_id')
        path_id = put.get('path_id')
        for path in path_id.split('-'):
            try:   
                cate = Category.objects.get(pk=int(path))
                SonCategory.objects.create(
                    cid = cate.cid,
                    name = cate.name,
                    is_parent = cate.is_parent,
                    parent_id = cate.parent_id,
                    level = cate.level,
                    pathid = cate.pathid,
                    path = cate.path,
                )
            except Exception as err:
                print(err)
                pass
            # return JsonResponse({'code':'1','msg':'操作失败'})
        return JsonResponse({'code':'0','msg':'ok'})


# from cpm.models import SonCategory,Category
# class CateUtil(View):
#     def get(self,request):
#         cates = SonCategory.objects.all()
#         print(len(cates))
#         paths = []
#         # for cate in cates:
#         #     paths += cate.pathid.split(',')
#         # new_ids = list(set(paths))
#         # for new_id in new_ids:
#         #     ca = Category.objects.get(pk=int(new_id))
#         #     try:
                
#         #         SonCategory.objects.create(
#         #             cid = int(new_id),
#         #             name = ca.name,
#         #             is_parent =ca.is_parent,
#         #             parent_id = ca.parent_id,
#         #             level = ca.level,
#         #             pathid = ca.pathid,
#         #             path =ca.path,
#         #         )
#         #     except Exception as err:
#         #         print(err)
#         return JsonResponse({'cates':'0'})
########################################批量导入
# 
class CpmMultiAddProduct(LoginRequiredMixin, View):
    '''批量导入候选商品+sku/供应商'''
    def get(self,request):
        template = request.GET.get('template')
        step = request.GET.get('step')
        ajax_upload_to_baidu = request.GET.get('ajax_upload_to_baidu')
        conn = get_redis_connection()
        # 异步上传图片到百度 用于图像识别
        if ajax_upload_to_baidu == '1':
            print('ajax-------------------------------')
            res_raw = conn.get('ajax_upload_skus_to_baidu')
            if res_raw:
                ress = str(res_raw.decode())
                conn.delete('ajax_upload_skus_to_baidu')
                ajax_lists = json.loads(ress)
                for item in ajax_lists:
                    BaiduImageSearch().upload_remote_url(item['sku_image'],item['good_id'],item['sku_id'])

        if template:
            filename = ''
            if template == '1':
                filename = '供应商信息模板.xlsx'
            if template == '2':
                filename = '商品信息模板.xlsx'
            if template == '3':
                filename = '店铺和产品关系模板.xlsx'

            files = open(os.path.join(BASE_DIR, 'media', 'download', filename) ,'rb')  
            response = FileResponse(files) 
            response['Content-Type']=' application/octet-stream'  
            response['Content-Disposition'] = 'attachment;filename="%s"'%(urlquote(filename))
            return response 
        if step:
            if step == '3':
                import os
                context = {'msg':'批量导入','multi_add':True}
                try:
                    # post完成之后设置的key 直接读取 
                    file_path = str(conn.get('file_path').decode())
                    # 正在读取文件中。。。
                    is_read_file_ = conn.get('is_read_file')
                    if is_read_file_:
                        context['error'] = '正在读取文件内容。。。'
                        return render(request,'basic/madd_product3.html',context=context)

                    # command = 'python /root/django/cpm/manage.py async_import_good_supplier >> /root/require.txt'
                    command = '/home/deploy/.local/share/virtualenvs/cpm-NXD7Laz8/bin/python3.8 /home/deploy/apps/cpm/manage.py async_import_good_supplier >>/home/deploy/apps/log/import.log 2>&1'
                    os.popen(command)
                    context['error'] = '导入任务已创建成功,后台开始执行导入,请稍后。。'
                    return render(request,'basic/madd_product3.html',context=context)
                except Exception as err:
                    all_length_ = conn.get('all_length')
                    progress_ = conn.get('progress')
                    pass_time_ = conn.get('pass_time')
                    success_length_ = conn.get('success_length')
                    
                    if all_length_ or pass_time_:
                        all_length = str(all_length_.decode())
                        # 重复刷新结果页面 数据清洗也需要时间 

                        # 已经成功读取文件正在进行数据清洗
                        if not progress_ and not pass_time_:
                            context['success'] = '成功读取了 %s 条数据,正在预处理。。。' % all_length
                            return render(request,'basic/madd_product3.html',context=context)
                        
                        if not pass_time_:
                            # 数据清洗完成,正在导入中 显示进度 
                            progress = str(progress_.decode())
                            context['success'] = '后台正在导入中,当前进度为 %s ,请稍后。。。' % progress
                            return render(request,'basic/madd_product3.html',context=context)


                        # 导入完成了
                        pass_time = str(pass_time_.decode())
                        all_length = str(all_length_.decode())
                        success_length = str(success_length_.decode())
                        print(pass_time) # 0 
                        print(all_length) # 2146
                        print(success_length)
                        success_msg = '导入完成,本次累计处理了%s条数据,成功导入了%s条,花费%s秒' % \
                            (all_length,success_length,pass_time)
                        context['success'] = success_msg
                        return render(request,'basic/madd_product3.html',context=context)

                    # 上面的几个时间 过期时间为1h 已经过期
                    import_step_ = conn.get('import_step')
                    if import_step_:
                        import_step = str(import_step_.decode())
                        if import_step == '2':
                            # 已经导入完成,页面等待超过1h,key已经删除
                            context['error'] = '当前操作已完成,不要重复刷新页面'
                            return render(request,'basic/madd_product3.html',context=context)
                    print(err)

        # 导入的第一阶段 判断是否后台存在正在导入的进程

        import_step_ = conn.get('import_step')
        context = {'msg':'批量导入','multi_add':True}
        if import_step_:
            import_step = str(import_step_.decode())
            if import_step == '1':
                context['error'] ='当前存在正在导入的进程,请勿继续执行导入!'
        return render(request,'basic/madd_product1.html',context=context)

    def post(self,request):
        template = request.FILES.get('template')
        if not template:
            context = {'msg':'批量导入','multi_add':True,'error':'请上传模板!'}
            return render(request,'basic/madd_product1.html',context=context)

        myfile_name = template.name
        template_names = ['供应商信息模板.xlsx','商品信息模板.xlsx']
        if myfile_name not in template_names:
            context = {'msg':'批量导入','multi_add':True,'error':'模板名不匹配,请正确上传模板!'}
            return render(request,'basic/madd_product1.html',context=context)
        # 保存上传文件
        myfile_name_upload =  str(datetime.now())+'__' + myfile_name
        path = os.path.join(BASE_DIR, 'media','upload', myfile_name_upload)
        f = open(path, 'wb')
        for chunk in template.chunks():
            f.write(chunk)
        f.close()

        conn = get_redis_connection()

        # 读取excel内容 pandas读
        print(myfile_name)
        if myfile_name == '供应商信息模板.xlsx':
            conn.set('_type','supplier')
        if myfile_name == '商品信息模板.xlsx':
            conn.set('_type','good')

        # 保存上传文件的路径
        conn.set('file_path',path)
        conn.set('import_step','1')
        conn.set('user_id',request.user.id)


        # type_dict = self.parse_suppiler_goods(path)
        # conn.set('_bytes',type_dict['_bytes'])
        # conn.expire('_bytes',60*30)
        # conn.expire('_type',60*30)
        # can_import = type_dict['_length']
        # cant_import = 0
        # 存入path redis  过期时间30min
        context = {
            'msg':'批量导入',
            'multi_add':True,
        }
        return render(request,'basic/madd_product2.html',context=context)

    '''下面的全部移到后台脚本执行''' 


############### import end #############################################
############### 重写R语言脚本 #############################################



class CpmRewriteR(LoginRequiredMixin,View):
    '''python 重写R语言的统计脚本'''
    def get(self,request):
        context = {
            'msg':'采购决策',
            'r':True,
        }
        return render(request,'basic/rewrite_r.html',context=context)

@method_decorator(csrf_exempt, name='dispatch')
class CpmExportCsvResult(LoginRequiredMixin,View):
    '''导出csv结果页面 所有的请求都post这个地址 然后统一处理'''
    def get(self,request):
        conn = get_redis_connection()
        download_url = request.GET.get('url')
        index = request.GET.get('index')
        if download_url:
            if not conn.hget('export_csv_result',index):
                raise Http404('当前导出的文件已经下载')
            conn.lrem('csv_lists',0,index)
            conn.hdel('export_csv_result',index)
            conn.hdel('export_csv_result',index + '__index')
            conn.hdel('export_csv_result',index + '__now_str')
            conn.hdel('export_csv_result',index + '__path')
            # aaa = jwt.decode(download_url, 'secret')
            file_name = download_url.split('csv/')[1]
            download_file = open(download_url,'rb')  
            response = HttpResponse(download_file)
            response['Content-Type']=' application/octet-stream'  
            response['Content-Disposition'] = 'attachment;filename="%s"'%(urlquote(file_name))
            # 删除这个csv文件
            os.remove(download_url)
            return response
        
        # LINDEX aa 0  
        length = conn.llen('csv_lists')
        export_csv_result_ = conn.hgetall('export_csv_result') # b'' 真的烦
        export_csv_result = {}
        for key in export_csv_result_:
            export_csv_result[str(key.decode())] = str(export_csv_result_[key].decode())

        item_result = [] # 当前所有导出任务的key
        for key in export_csv_result:
            if len(key.split('__')) == 1:
                item_result.append(key)
        
        # url 和汉字替换
        context_url = {
            '/query/': '通用查询',
            '/sale/shangjia/': '销售-上架',
            '/sale/fengcun/': '销售-封存',
            '/sale/taotai/': '销售-淘汰',
            '/photo/start/': '拍摄准备',
            '/photo/sysx/': '摄影摄像',
            '/photo/mgzz/': '美工制作',
            '/purchase/purchase/': '新品采购',
            '/purchase/fen_dian/': '分货点货',
            '/purchase/yanhuo/': '验货',
            '/purchase/ruku/': '入库阶段',
            '/select/p_list/': '候选品管理',
            '/select/pingshen/': '评审管理',
            '/select/add_sku/': '新品管理',
        }
        html_results = []
        print(item_result)
        for item in item_result:
            temp_dict = {}
            temp_dict['raw_name'] = item
            temp_dict['state'] = export_csv_result[item] 
            temp_dict['index'] = export_csv_result[item + '__index'] # 用于下载后删除
            temp_dict['time'] = export_csv_result[item + '__now_str'] # 
            temp_dict['name'] =  item.split('**')[0]
            temp_dict['name'] = context_url[temp_dict['name']]
            try:
                temp_dict['path'] = export_csv_result[item + '__path'] 
                # temp_dict['path'] = jwt.encode({'path':temp_dict['path']}, 'secret')
            except Exception as err:
                temp_dict['path'] = ''
                print(err)
            html_results.append(temp_dict)
        


        context = {
            'msg':'导出管理',
            'csv':True,
            'length':length,
            'html_results':html_results,

        }
        return render(request,'basic/export_result.html',context=context)

    def post(self,request):
        conn = get_redis_connection()

        conn.set('csv_path',pickle.dumps(request.POST.get('urlPath')))
        conn.set('request_get',pickle.dumps(request.GET))
        # 执行python脚本创建后台导出任务

        # command = 'python /root/django/cpm/manage.py export_csv >> /root/csv.txt'
        command = '/home/deploy/.local/share/virtualenvs/cpm-NXD7Laz8/bin/python3.8 /home/deploy/apps/cpm/manage.py export_csv >>/home/deploy/apps/log/export_csv.log 2>&1'
        os.popen(command)
        return JsonResponse({'code':'0','msg':'ok'})