from django.shortcuts import render,redirect,reverse,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.http import JsonResponse,QueryDict
from django.core import serializers
from django.contrib.auth.models import User
from django.db import transaction
from django.core.paginator import Paginator


import time
import os
from utils.export_csv import export_csv
from utils.qiniu_util import QiniuStorage
from utils.login_required import LoginRequiredMixin
from utils.page_util import get_pagination_data
from urllib import parse
from datetime import datetime
from cpm.settings import PAGE_SIZE,QINIU_BASE_DOMAIN,GOOD_RUKU_EXPIRE_TIME
from cpm.models import Category,Good,GoodsBrand,GoodsSku,Supplier,GoodsSelectPhase,GoodsPingshenPhase,GoodsPurchasePhase,GOODS_EXCEPT_DETAIL,GoodsDianAndFenPhase,GOODS_YANHUO_RESULT,GoodsYanhuoPhase,GOODS_STORAGE_STATE,GoodRukuPhase



class CpmProductPurchaseIndex(LoginRequiredMixin,View):
    '''采购页面'''
    def get(self,request):
        # print(request.META.get('HTTP_USER_AGENT'))
        # 查询条件
        suppiler_val = request.GET.get('suppilerVal','')

        code = request.GET.get('code','')
        name = request.GET.get('name','')
        pinlei = request.GET.get('pinlei','')
        chargers = request.GET.get('chargers','')
        suppliers = request.GET.get('suppliers','')
        jibie = request.GET.get('jibie','')
        start = request.GET.get('start','')
        end = request.GET.get('end','')
        page = int(request.GET.get('p',1))

        items = Good.objects.select_related().filter(state_caigou__exact=3).order_by('code')
        # items = Good.objects.select_related().filter(state_raw__gte=3).order_by('id')
        # 处理查询条件
        if code:
            items = items.filter(code__icontains=code)
        if name:
            items = items.filter(name__icontains=name)
        if jibie:
            items = items.filter(jibie=jibie)
        if start or end:
            if start:
                start_date = datetime.strptime(start,'%Y-%m-%d')
            else:
                start_date = datetime(year=2019,month=9,day=1)
            if end:
                end_date = datetime.strptime(end,'%Y-%m-%d')
            else:
                end_date = datetime.today()
            items = items.filter(created_at__range=(start_date,end_date))

        if chargers:
            # '1,'  --> ['1','']
            charger_ids = chargers.split(',')
            int_charger_ids = []
            for tem in charger_ids:
                if tem!= '':
                    int_charger_ids.append(int(tem))
            items = items.filter(charger__in=int_charger_ids).distinct()
        if suppliers:
            supplier_ids = suppliers.split(',')
            int_supplier_ids = []
            for tem in supplier_ids:
                if tem!= '':
                    int_supplier_ids.append(int(tem))
            items = items.filter(suppiler__in=int_supplier_ids).distinct()
        if pinlei:
            cates = Category.objects.filter(name__icontains=pinlei)
            items = items.filter(cate__in=cates).distinct()


        users = User.objects.filter(is_superuser = False,extension__role__name__in=[0,6]).select_related().distinct()
        # 分页
        len_items = len(items)  # 总的记录数
        paginator = Paginator(items,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1
        page_obj = paginator.page(page)
        items = page_obj.object_list
        if not items:
            items = []
        for item in items:
            # 供应商 
            setattr(item,'suppliers',item.suppiler.all())
            setattr(item,'chargers',item.charger.all())
            
            first_sku = item.goods_skus.first()
            setattr(item,'images', first_sku.sku_image)
            if not first_sku.sku_image.startswith('http'):
                setattr(item,'images',QINIU_BASE_DOMAIN + first_sku.sku_image)

            setattr(item,'pingshen_date',GoodsPingshenPhase.objects.filter(good=item).first())

        # 导出csv

        context = {
            'purchase':True,
            'users':users,
            'query_url':'/purchase/purchase/',
            'msg':'待采购列表',
            'chargers_all': User.objects.filter(extension__role__name=0),
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'last_pages':len_items/PAGE_SIZE +1,
            # 查询参数
            'url_query': '&'+parse.urlencode({   
                # 'p': page or '',
                'code': code or '',
                'name': name or '',
                'pinlei': pinlei or '',
                'chargers': chargers or '',
                'suppliers': suppliers or '',
                'jibie': jibie or '',
                'start': start or '',
                'end': end or '',
            })
        }
        # 查询参数返回
        if chargers:
            chargers = int(chargers)
        url_query_data = {
            'suppiler_val':suppiler_val,
            'chargers':chargers,
            'suppliers':suppliers,
            'code':code,
            'name':name,
            'pinlei':pinlei,
            'start':start,
            'end':end,
            'jibie':jibie,
            'base_domain':QINIU_BASE_DOMAIN,
        }
        page_data = get_pagination_data(paginator,page_obj)
        context.update(page_data)
        context.update(url_query_data)
        return render(request,'purchase/product_purchase.html',context=context)

    @transaction.atomic
    def post(self,request):
        '''创建采购订单'''
        good_id = request.POST.get('good_id')
        p_date = request.POST.get('p_date')
        e_date = request.POST.get('e_date')
        puser_id = request.POST.get('puser_id')
        desc = request.POST.get('desc')

        # 处理数据
        # datetime.strptime(str_p,'%Y-%m-%d %H:%M:%S')
        now = datetime.now()
        str_e_date = e_date + ' ' + str(now.hour)+':'+str(now.minute)+':00'
        e_date = datetime.strptime(str_e_date,'%Y-%m-%d %H:%M:%S')
        if p_date:
            str_p_date = p_date + ' ' + str(now.hour)+':'+str(now.minute)+':00'
            p_date = datetime.strptime(str_p_date,'%Y-%m-%d %H:%M:%S')
        else:
            p_date = now
        try:
            good = Good.objects.get(pk=int(good_id))
            puser = User.objects.get(pk=int(puser_id))
        except Exception as err1:
            print(err1)
            return JsonResponse({'code':'2','msg':'请正确操作'})
        try:
            # 保存记录
            save_id = transaction.savepoint()
            GoodsPurchasePhase.objects.create(
                good = good,
                operator = request.user,
                buyer = puser,
                purchase_date = p_date,
                expected_data = e_date,
                desc = desc,
            )
            # 改变该good的状态
            good.state_caigou = 4   # 采购订单创建完成,待分货点货
            good.save()
            transaction.savepoint_commit(save_id)
        except Exception as err:
            print(err)
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'code':'1','msg':'操作失败,请重试!'})
        return JsonResponse({'code':'0','msg':'ok'})




class CpmProductFenAndDian(LoginRequiredMixin,View):
    '''分货点货'''
    def get(self,request):
        # 查询条件
        suppiler_val = request.GET.get('suppilerVal','')


        code = request.GET.get('code','')
        name = request.GET.get('name','')
        pinlei = request.GET.get('pinlei','')
        chargers = request.GET.get('chargers','')
        suppliers = request.GET.get('suppliers','')
        jibie = request.GET.get('jibie','')
        start = request.GET.get('start','')
        end = request.GET.get('end','')
        state = request.GET.get('state','')

        # 首页点进来查看超期的产品
        caigou_exceed = request.GET.get('caigou_exceed','')
        page = int(request.GET.get('p',1))

        items = Good.objects.select_related().filter(state_caigou=4).order_by('code')
        # 处理查询条件
        if code:
            items = items.filter(code__icontains=code)
        if name:
            items = items.filter(name__icontains=name)
        if jibie:
            items = items.filter(jibie=jibie)
        if start or end:
            if start:
                start_date = datetime.strptime(start,'%Y-%m-%d')
            else:
                start_date = datetime(year=2019,month=9,day=1)
            if end:
                end_date = datetime.strptime(end,'%Y-%m-%d')
            else:
                end_date = datetime.today()
            items = items.filter(goods_buy_good__purchase_date__range=(start_date,end_date)).distinct()

        if chargers:
            # '1,'  --> ['1','']
            charger_ids = chargers.split(',')
            int_charger_ids = []
            for tem in charger_ids:
                if tem!= '':
                    int_charger_ids.append(int(tem))
            items = items.filter(charger__in=int_charger_ids).distinct()
        if suppliers:
            supplier_ids = suppliers.split(',')
            int_supplier_ids = []
            for tem in supplier_ids:
                if tem!= '':
                    int_supplier_ids.append(int(tem))
            items = items.filter(suppiler__in=int_supplier_ids).distinct()
        if pinlei:
            cates = Category.objects.filter(name__icontains=pinlei)
            items = items.filter(cate__in=cates).distinct()
       # 到货状态
        if state:
            if state == '0':
                items = self.compute_good_is_expected(items,'0')
            elif state == '1':
                items = self.compute_good_is_expected(items,'1')
            else:
                items = self.compute_good_is_expected(items,'2')
        

        if caigou_exceed:
            item1 = self.compute_good_is_expected(items,'1')
            item2 = self.compute_good_is_expected(items,'2')
            items = item1 + item2

        users = User.objects.filter(is_superuser = False,extension__role__name__in=[3,4,5]).select_related().all().distinct()

        # 分页
        len_items = len(items)  # 总的记录数
        paginator = Paginator(items,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1
        page_obj = paginator.page(page)
        items = page_obj.object_list
        if not items:
            items = []
        for item in items:
            order = GoodsPurchasePhase.objects.filter(good=item).first()
            # 供应商 
            setattr(item,'suppliers',item.suppiler.all())
            setattr(item,'chargers',item.charger.all())
            # 处理sku图片
            first_sku = item.goods_skus.first()
            setattr(item,'images', first_sku.sku_image)
            if not first_sku.sku_image.startswith('http'):
                setattr(item,'images',QINIU_BASE_DOMAIN + first_sku.sku_image)

            setattr(item,'order',order)
            setattr(item,'good_e_state',self.compute_good_state(order.expected_data))


        # 导出csv


        context = {
            'fen_dian':True,
            'users':users,
            'details':GOODS_EXCEPT_DETAIL,
            'query_url':'/purchase/fen_dian/',
            'msg':'待分货点货列表',
            'chargers_all': User.objects.filter(extension__role__name=0),
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'last_pages':len_items/PAGE_SIZE +1,
            # 查询参数
            'url_query': '&'+parse.urlencode({   
                # 'p': page or '',
                'code': code or '',
                'name': name or '',
                'pinlei': pinlei or '',
                'chargers': chargers or '',
                'suppliers': suppliers or '',
                'jibie': jibie or '',
                'start': start or '',
                'end': end or '',
                'caigou_exceed': caigou_exceed or '',
                'state': state or '',
            })
        }
        # 查询参数返回
        if chargers:
            chargers = int(chargers)
        url_query_data = {
            'suppiler_val':suppiler_val,
            'chargers':chargers,
            'suppliers':suppliers,
            'code':code,
            'name':name,
            'state':state,
            'pinlei':pinlei,
            'start':start,
            'end':end,
            'jibie':jibie,
            'caigou_exceed':caigou_exceed,
            'base_domain':QINIU_BASE_DOMAIN,
        }
        page_data = get_pagination_data(paginator,page_obj)
        context.update(page_data)
        context.update(url_query_data)
        return render(request,'purchase/product_fen_dian.html',context=context)

    def compute_good_is_expected(self,items,state):
        new_items = []
        if state == '0':
            # 正常的
            for item in items:
                timeStamp1 = item.goods_buy_good.all().order_by('-created_at').first().expected_data.timestamp()
                now_timestamp = datetime.now().timestamp()
                if timeStamp1 - now_timestamp  > 0:
                    new_items.append(item)
        elif state == '1':
            # 超期 1-3
            for item in items:
                timeStamp1 = item.goods_buy_good.all().order_by('-created_at').first().expected_data.timestamp()
                now_timestamp = datetime.now().timestamp()
                if timeStamp1 - now_timestamp   > (-3600*24*3) and timeStamp1 - now_timestamp  < 0:
                    new_items.append(item)
                  
        elif state == '2':
            # 严重超期
            for item in items:
                timeStamp1 = item.goods_buy_good.all().order_by('-created_at').first().expected_data.timestamp()
                now_timestamp = datetime.now().timestamp()
                if timeStamp1 - now_timestamp   < -3600*24*3 :
                    new_items.append(item)
        return new_items

    def compute_good_state(self,expected_data):
        # timeArray1 = time.strptime(expected_data, "%Y-%m-%d %H:%M:%S")  # 先转换为时间数组
        # timeStamp1 = int(time.mktime(timeArray))  # 转换为时间戳

        timeStamp1 = expected_data.timestamp()
        now_timestamp = datetime.now().timestamp()

        interval = timeStamp1 - now_timestamp 

        if interval > 0:
            return '正常'
        elif interval > -3600*24*3:
            return '超期'
        else:
            return '严重超期'

    @transaction.atomic
    def post(self,request):
        '''点击点货分货,返回处理结果'''
        good_id = request.POST.get('good_id')
        puser_id = request.POST.get('puser_id')
        state = request.POST.get('state')
        is_checked = request.POST.get('is_checked')
        desc = request.POST.get('desc')
        real_arrival_date = request.POST.get('real_arrival_date')

        now = datetime.now()
        if real_arrival_date:
            str_p_date = real_arrival_date + ' ' + str(now.hour)+':'+str(now.minute)+':00'
            real_arrival_date = datetime.strptime(str_p_date,'%Y-%m-%d %H:%M:%S')

        try:
            good = Good.objects.get(pk=int(good_id))
            charger = User.objects.get(pk=int(puser_id))
            save_id = transaction.savepoint()

            try:
                GoodsDianAndFenPhase.objects.create(
                    good = good,
                    operator = request.user,
                    charger = charger,
                    state = state,
                    desc = desc,
                    real_arrival_date = real_arrival_date,
                )
                # 判断是否级联到下一个阶段 
                if is_checked == 'true':
                    good.state_caigou = 6
                else:
                    good.state_caigou = 5
                good.save()
            except Exception as err1:
                print(err1)
                transaction.savepoint_rollback(save_id)
                return JsonResponse({'code':'2','msg':'操作失败,请刷新重试'})
            transaction.savepoint_commit(save_id)
        except Exception as err:
            print(err)
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'code':'1','msg':'请正确操作'})
        return JsonResponse({'code':'0','msg':'ok'})




class CpmProductYanhuoView(LoginRequiredMixin,View):
    '''验货阶段'''
    def get(self,request):
        # 查询条件
        suppiler_val = request.GET.get('suppilerVal','')

        code = request.GET.get('code','')
        name = request.GET.get('name','')
        pinlei = request.GET.get('pinlei','')
        chargers = request.GET.get('chargers','')
        suppliers = request.GET.get('suppliers','')
        jibie = request.GET.get('jibie','')
        start = request.GET.get('start','')
        end = request.GET.get('end','')
        state = request.GET.get('state','')
        page = int(request.GET.get('p',1))

        items = Good.objects.select_related().filter(state_caigou__in=[4,5]).order_by('code')
        # 处理查询条件
        if code:
            items = items.filter(code__icontains=code)
        if name:
            items = items.filter(name__icontains=name)
        if jibie:
            items = items.filter(jibie=jibie)
        if start or end:
            if start:
                start_date = datetime.strptime(start,'%Y-%m-%d')
            else:
                start_date = datetime(year=2019,month=9,day=1)
            if end:
                end_date = datetime.strptime(end,'%Y-%m-%d')
            else:
                end_date = datetime.today()
            items = items.filter(goods_buy_good__purchase_date__range=(start_date,end_date)).distinct()

        if chargers:
            # '1,'  --> ['1','']
            charger_ids = chargers.split(',')
            int_charger_ids = []
            for tem in charger_ids:
                if tem!= '':
                    int_charger_ids.append(int(tem))
            items = items.filter(charger__in=int_charger_ids).distinct()
        if suppliers:
            supplier_ids = suppliers.split(',')
            int_supplier_ids = []
            for tem in supplier_ids:
                if tem!= '':
                    int_supplier_ids.append(int(tem))
            items = items.filter(suppiler__in=int_supplier_ids).distinct()
        if pinlei:
            cates = Category.objects.filter(name__icontains=pinlei)
            items = items.filter(cate__in=cates).distinct()
       # 到货状态
        if state:
            items = items.filter(goods_dian_fen__state__exact=int(state)).distinct()

                

        users = User.objects.filter(is_superuser = False,extension__role__name__in=[3,4,5]).select_related().all().distinct()
        # 分页
        len_items = len(items)  # 总的记录数
        paginator = Paginator(items,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1
        page_obj = paginator.page(page)
        items = page_obj.object_list
        if not items:
            items = []
        for item in items:
            order = GoodsPurchasePhase.objects.filter(good=item).first()
            goods_dianfen = GoodsDianAndFenPhase.objects.filter(good=item).order_by('-created_at').first()
            # 供应商 
            setattr(item,'suppliers',item.suppiler.all())
            setattr(item,'chargers',item.charger.all())

            first_sku = item.goods_skus.first()
            setattr(item,'images', first_sku.sku_image)
            if not first_sku.sku_image.startswith('http'):
                setattr(item,'images',QINIU_BASE_DOMAIN + first_sku.sku_image)

            setattr(item,'order',order)
            setattr(item,'goods_dianfen',goods_dianfen)

        # 导出csv

        context = {
            'yanhuo_url':True,
            'users':users,
            'yanhuos':GOODS_YANHUO_RESULT,
            'query_url':'/purchase/yanhuo/',
            'msg':'待验货列表',
            'chargers_all': User.objects.filter(extension__role__name=0),
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'last_pages':len_items/PAGE_SIZE +1,
            # 查询参数
            'url_query': '&'+parse.urlencode({   
                # 'p': page or '',
                'code': code or '',
                'name': name or '',
                'pinlei': pinlei or '',
                'chargers': chargers or '',
                'suppliers': suppliers or '',
                'jibie': jibie or '',
                'start': start or '',
                'end': end or '',
                'state': end or 'state',
            })
        }
        if chargers:
            chargers = int(chargers)
        # 查询参数返回
        url_query_data = {
            'suppiler_val':suppiler_val,
            'chargers':chargers,
            'suppliers':suppliers,
            'code':code,
            'name':name,
            'state':state,
            'pinlei':pinlei,
            'start':start,
            'end':end,
            'jibie':jibie,
            'base_domain':QINIU_BASE_DOMAIN,
        }
        page_data = get_pagination_data(paginator,page_obj)
        context.update(page_data)
        context.update(url_query_data)
        return render(request,'purchase/product_yanhuo.html',context=context)

    @transaction.atomic
    def post(self,request):
        good_id = request.POST.get('good_id')
        charger_id = request.POST.get('charger')
        desc = request.POST.get('desc')
        result = request.POST.get('yanhuo_result')
        # 先查询出来good的相关信息
        try:
            good = Good.objects.get(pk=int(good_id))
            charger = User.objects.get(pk=int(charger_id))
        except Exception as err1:
            print(err1)
            return JsonResponse({'code':'9','msg':'请正确操作'})

        video = request.FILES.get('video')
        images = request.FILES.getlist('images')
        # 重新构造视频的名称
        try:
            save_id = transaction.savepoint()
            yanhuo = GoodsYanhuoPhase.objects.create(
                good = good,
                operator = request.user,
                charger = charger,
                desc = desc,
                result = int(result)
            )
            qiniu = QiniuStorage()

            video_key = ''
            if video:
                video_key = self.get_video_key_name(video,good)
                qiniu.upload_video_and_encode(video_key)
            # 处理图片

            db_images = ''
            if images:
                image_keys = self.get_image_keys(images,good)
                for item in image_keys:
                    qiniu.get_qiniu_auth(item['image_key'])
                    db_images += item['image_key'] + ','

            yanhuo.video = video_key
            yanhuo.images = db_images

            yanhuo.save()
            good.state_caigou = 6
            good.save()
            transaction.savepoint_commit(save_id)
        except Exception as err2:
            transaction.savepoint_rollback(save_id)
            print(err2)
            return JsonResponse({'code':'8','msg':'操作失败,请重试'})
        return JsonResponse({'code':'0','msg':'ok','url':'/purchase/yanhuo/'})

    def get_image_keys(self,images,good):
        '''重新构造images的key'''
        image_keys = []
        for index,image in enumerate(images):
            temp = {}
            image_ext_name = image.name.split('.')[-1]
            now = str(datetime.now().timestamp()).replace('.','')
            image_key = 'yanhuo_image_'+str(good.id)+'_'+str(index)+'_'+now+'.'+image_ext_name
            file_path_name = os.path.join('/tmp',image_key)
            with open(file_path_name, 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)  
            temp['good_id'] = good.id
            temp['image_key'] = image_key
            image_keys.append(temp)
        return image_keys
    
    def get_video_key_name(self,video,good):
        '''重新构造video的key'''
        video_ext_name = video.name.split('.')[-1]
        now = str(datetime.now().timestamp()).replace('.','')
        video_key = 'video_'+str(good.id)+'_'+now+'_yanhuo.'+video_ext_name
        file_path_name = os.path.join('/tmp',video_key)
        with open(file_path_name, 'wb+') as f:
            for chunk in video.chunks():
                f.write(chunk)  
        return video_key



class CpmProductRukuView(LoginRequiredMixin,View):
    '''入库阶段'''
    def get(self,request):
        # 查询条件
        suppiler_val = request.GET.get('suppilerVal','')

        code = request.GET.get('code','')
        name = request.GET.get('name','')
        pinlei = request.GET.get('pinlei','')
        chargers = request.GET.get('chargers','')
        suppliers = request.GET.get('suppliers','')
        jibie = request.GET.get('jibie','')
        start = request.GET.get('start','')
        end = request.GET.get('end','')
        dianhuo = request.GET.get('dianhuo','')
        yanhuo = request.GET.get('yanhuo','')
        page = int(request.GET.get('p',1))

        # 首页进入 入库超期
        ruku_exceed = request.GET.get('ruku_exceed','')


        items = Good.objects.select_related().filter(state_caigou=6).order_by('code')
        # 处理查询条件
        if code:
            items = items.filter(code__icontains=code)
        if name:
            items = items.filter(name__icontains=name)
        if jibie:
            items = items.filter(jibie=jibie)
        if start or end:
            if start:
                start_date = datetime.strptime(start,'%Y-%m-%d')
            else:
                start_date = datetime(year=2019,month=9,day=1)
            if end:
                end_date = datetime.strptime(end,'%Y-%m-%d')
            else:
                end_date = datetime.today()
            items = items.filter(goods_buy_good__purchase_date__range=(start_date,end_date)).distinct()

        if chargers:
            # '1,'  --> ['1','']
            charger_ids = chargers.split(',')
            int_charger_ids = []
            for tem in charger_ids:
                if tem!= '':
                    int_charger_ids.append(int(tem))
            items = items.filter(charger__in=int_charger_ids).distinct()
        if suppliers:
            supplier_ids = suppliers.split(',')
            int_supplier_ids = []
            for tem in supplier_ids:
                if tem!= '':
                    int_supplier_ids.append(int(tem))
            items = items.filter(suppiler__in=int_supplier_ids).distinct()
        if pinlei:
            cates = Category.objects.filter(name__icontains=pinlei)
            items = items.filter(cate__in=cates).distinct()
       # 到货状态
        if dianhuo:
            items = items.filter(goods_dian_fen__state__exact=dianhuo).distinct()
        if yanhuo:
            items = items.filter(goods_yanhuo_good__result__exact=yanhuo).distinct()

        if ruku_exceed:
            ruku_exceed = []
            for good in items:
                order = GoodsYanhuoPhase.objects.filter(good=good).filter(good__state_caigou=6).order_by('-created_at').first()
                if order:
                    if not self.compute_ruku_exceed(order.created_at):
                        ruku_exceed.append(good)
            items = ruku_exceed


        users = User.objects.filter(is_superuser = False,extension__role__name__in=[3,4,5]).select_related().all().distinct()
        # 分页
        len_items = len(items)  # 总的记录数
        paginator = Paginator(items,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1
        page_obj = paginator.page(page)
        items = page_obj.object_list
        if not items:
            items = []
        for item in items:
            order = GoodsPurchasePhase.objects.filter(good=item).first()
            dianhuo_obj = GoodsDianAndFenPhase.objects.filter(good=item).order_by('-created_at').first()
            yanhuo_obj = GoodsYanhuoPhase.objects.filter(good=item).order_by('-created_at').first()
            # 供应商 
            setattr(item,'suppliers',item.suppiler.all())
            setattr(item,'chargers',item.charger.all())
            first_sku = item.goods_skus.first()
            setattr(item,'images', first_sku.sku_image)
            if not first_sku.sku_image.startswith('http'):
                setattr(item,'images',QINIU_BASE_DOMAIN + first_sku.sku_image)

            setattr(item,'order',order)
            setattr(item,'dianhuo',dianhuo_obj)
            setattr(item,'yanhuo',yanhuo_obj)

        # 导出csv

        context = {
            'ruku':True,
            'users':users,
            'details':GOODS_EXCEPT_DETAIL,
            'query_url':'/purchase/ruku/',
            'chargers_all': User.objects.filter(extension__role__name=0),
            'msg':'待入库列表',
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'last_pages':len_items/PAGE_SIZE +1,
            # 查询参数
            'url_query': '&'+parse.urlencode({   
                # 'p': page or '',
                'code': code or '',
                'name': name or '',
                'pinlei': pinlei or '',
                'chargers': chargers or '',
                'suppliers': suppliers or '',
                'jibie': jibie or '',
                'start': start or '',
                'end': end or '',
                'yanhuo': yanhuo or '',
                'dianhuo': dianhuo or '',
                'ruku_exceed': ruku_exceed or '',
            })
        }
        # 查询参数返回
        if chargers:
            chargers = int(chargers)
        url_query_data = {
            'suppiler_val':suppiler_val,
            'chargers':chargers,
            'suppliers':suppliers,
            'code':code,
            'name':name,
            'yanhuo':yanhuo,
            'dianhuo':dianhuo,
            'pinlei':pinlei,
            'start':start,
            'end':end,
            'jibie':jibie,
            'ruku_exceed':ruku_exceed,
            'rukus':GOODS_STORAGE_STATE,
            'base_domain':QINIU_BASE_DOMAIN,
        }
        page_data = get_pagination_data(paginator,page_obj)
        context.update(page_data)
        context.update(url_query_data)
        return render(request,'purchase/product_ruku.html',context=context)

    def compute_ruku_exceed(self,expected_data):
        '''计算入库是否超期  在验货完成后七天内不点入库就判断为超期'''
        timeStamp1 = expected_data.timestamp()
        now_timestamp = datetime.now().timestamp()
        interval = now_timestamp -timeStamp1
        day7 = GOOD_RUKU_EXPIRE_TIME * 24 * 3600 
        if interval < day7:
            return True
        else:
            # 超期
            return False


    @transaction.atomic
    def post(self,request):
        '''入库确认'''
        good_id = request.POST.get('good_id')
        charger_id = request.POST.get('charger')
        desc = request.POST.get('desc')
        result = request.POST.get('result')
        print(result)
        print(type(result))
        print(result=='0')
        # 先查询出来good的相关信息
        try:
            good = Good.objects.get(pk=int(good_id))
            charger = User.objects.get(pk=int(charger_id))
        except Exception as err1:
            print(err1)
            return JsonResponse({'code':'9','msg':'请正确操作'})

        try:
            save_id = transaction.savepoint()
            ruku = GoodRukuPhase.objects.create(
                good = good,
                operator = request.user,
                charger = charger,
                desc = desc,
                result = int(result)
            )
            # 根据result处理good的状态
            if result == '0':
                # 同时查询 在美工阶段是否已经完成
                good.state_caigou = 10
                if good.state_paishe == 10:
                    good.state_sale = 10
            elif result == '1':
                good.state_caigou = 2
            elif result == '2':
                good.state_caigou = 4
            good.save()
            transaction.savepoint_commit(save_id)
        except Exception as err2:
            transaction.savepoint_rollback(save_id)
            print(err2)
            return JsonResponse({'code':'8','msg':'操作失败,请重试'})
        return JsonResponse({'code':'0','msg':'ok','url':'/purchase/ruku/'})
 


class CpmProductRukuGetOneDetail(LoginRequiredMixin,View):
    '''点击入库显示一个产品的所有阶段详情信息 api'''
    def get(self,request):
        good_id = request.GET.get('good_id')
        try:
            good = Good.objects.filter(id=int(good_id)).first()
        except Exception as err1:
            print(err1)
            return JsonResponse({'code':'8','msg':'请正确操作'})
        # 级联操作
        res_good = {}
        res_good['code'] = good.code
        res_good['name'] = good.name
        res_good['created_at'] = good.created_at.strftime('%Y-%m-%d')
        res_good['supplier'] = self.deal_suppiler(good.suppiler.all())
        res_good['charger'] = self.deal_charger(good.charger.all())
        res_good['jibie'] = good.get_jibie_display()

        # 采购
        res_caigou = {}
        caigou = good.goods_buy_good.all().order_by('-created_at').first()
        if  caigou.buyer.extension.name:
            res_caigou['charger'] = caigou.buyer.extension.name
        else:
            res_caigou['charger'] = caigou.buyer.username

        res_caigou['purchase_date'] = caigou.purchase_date.strftime('%Y-%m-%d')
        res_caigou['expected_data'] = caigou.expected_data.strftime('%Y-%m-%d')
        res_caigou['desc'] = caigou.desc
        # 点货
        res_dian = {'real_arrival_date':'','charger':'','desc':'','state':''}
        dian = good.goods_dian_fen.all().order_by('-created_at').first()
        if dian:
            res_dian['real_arrival_date'] = dian.real_arrival_date.strftime('%Y-%m-%d')
            res_dian['charger'] = dian.charger.username
            if dian.charger.extension.name:
                res_dian['charger'] = dian.charger.extension.name

            res_dian['desc'] = dian.desc
            res_dian['state'] = dian.get_state_display()
        # 验货
        res_yanhuo = {}
        yanhuo = good.goods_yanhuo_good.all().order_by('-created_at').first()
        if yanhuo:
            if yanhuo.charger.extension.name:
                res_yanhuo['charger'] = yanhuo.charger.extension.name
            else:
                res_yanhuo['charger'] = yanhuo.charger.username

            res_yanhuo['desc'] = yanhuo.desc
            res_yanhuo['result'] = yanhuo.get_result_display()
            res_yanhuo['video'] = QINIU_BASE_DOMAIN + yanhuo.video
            res_yanhuo['images'] = self.get_yanhuo_images(yanhuo.images)

        context = {
            'code':'0',
            'good':res_good,
            'caigou':res_caigou,
            'yanhuo':res_yanhuo,
            'dianhuo':res_dian,
        }
        return JsonResponse(context)

    def get_yanhuo_images(self,images):
        '''将a,a,a->[a,a,a]'''
        img_arr = images.split(',')
        res_arr = []
        for img in img_arr:
            if img!='':
                res_arr.append(QINIU_BASE_DOMAIN+img)
        return res_arr

    def deal_suppiler(self,suppiler):
        res_name = ''
        for q in suppiler:
            res_name += q.name + ','
        return res_name

    def deal_charger(self,charger):
        res_name = ''
        for c in charger:
            res_name += c.extension.name + ','
        return res_name




