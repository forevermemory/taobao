from django.shortcuts import render,redirect,reverse,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.http import JsonResponse,QueryDict
from django.core import serializers
from django.contrib.auth.models import User
from django.db import transaction
from django.core.paginator import Paginator


from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import time
from utils.export_csv import export_csv
from utils.login_required import LoginRequiredMixin
from utils.page_util import get_pagination_data
from urllib import parse
from datetime import datetime
from cpm.settings import PAGE_SIZE,QINIU_BASE_DOMAIN,GOOD_MGZZ_EXPIRE_TIME
from cpm.models import Category,Good,GoodsBrand,GoodsSku,Supplier,GoodsSelectPhase,GoodsPingshenPhase,GoodsPurchasePhase,GOODS_EXCEPT_DETAIL,GoodsDianAndFenPhase,GoodsPhotoStartPhase,GoodsNotPhotoToMakingPhase,GoodsSYSXingAndFinishPhase,GOOD_MEIGONG_MK_STATE,GOOD_MEIGONG_CHECK,GoodsMGZZCheckDetail,GoodsMGZZPhase


@method_decorator(csrf_exempt, name='dispatch')
class CpmProductPhotoStart(LoginRequiredMixin,View):
    '''拍摄开始'''
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
        page = int(request.GET.get('p',1))

        items = Good.objects.select_related().filter(state_paishe__exact=7).order_by('code')
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


        users = User.objects.filter(is_superuser = False,extension__role__name__in=[2,6]).select_related().all().distinct()

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


        context = {
            'start':True,
            'users':users,
            'query_url':'/photo/start/',
            'msg':'待拍摄准备列表',
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'chargers_all': User.objects.filter(extension__role__name=0),
            'paginator': paginator,
            'total_item': len_items,
            'last_pages':len_items/PAGE_SIZE +1,
            # 查询参数
            'url_query': '&'+parse.urlencode({   
                'code': code or '',
                'name': name or '',
                'pinlei': pinlei or '',
                'chargers': chargers or '',
                'suppliers': suppliers or '',
                'suppiler_val': suppiler_val or '',
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
        return render(request,'photo/product_ps_zb.html',context=context) 

    @transaction.atomic
    def post(self,request):
        # product_ps_zb.js:42 good_id=8&good_code=19007&csrfmiddlewaretoken=&good_name=good_purchaser=1&good_photo_method=0&good_kuaidi_name=&good_kuaidi_code=&good_j_date=&good_e_date=2019-09-20&good_desc=

        good_id = request.POST.get('good_id')
        good_purchaser = request.POST.get('good_purchaser')
        good_photo_method = request.POST.get('good_photo_method')  # 0 外 1 内
        good_kuaidi_name = request.POST.get('good_kuaidi_name')
        good_kuaidi_code = request.POST.get('good_kuaidi_code')
        good_j_date = request.POST.get('good_j_date')
        good_e_date = request.POST.get('good_e_date')
        good_desc = request.POST.get('good_desc')
        # 是否需要快递寄送
        need_jisong = False
        if good_kuaidi_name:
            need_jisong = True

        # 日期转换
        now = datetime.now()
        if good_j_date:
            str_p_date = good_j_date + ' ' + str(now.hour)+':'+str(now.minute)+':00'
            good_j_date = datetime.strptime(str_p_date,'%Y-%m-%d %H:%M:%S')
        else:
            good_j_date = now
        if good_e_date:
            str_p_date = good_e_date + ' ' + str(now.hour)+':'+str(now.minute)+':00'
            good_e_date = datetime.strptime(str_p_date,'%Y-%m-%d %H:%M:%S')

        try:
            good = Good.objects.get(pk=int(good_id))
            photo_genzonger_user = User.objects.get(pk=int(good_purchaser))
        except Exception as err1:
            print(err1)
            return JsonResponse({'code':'1','msg':'unknown err'})

        try:
            save_point = transaction.savepoint()
            # 存入GoodsPhotoStartPhase
            GoodsPhotoStartPhase.objects.create(
                good = good,
                operator = request.user,
                photo_genzonger = photo_genzonger_user,
                good_photo_method = int(good_photo_method),
                kuaidi_name = good_kuaidi_name,
                kuaidi_code = good_kuaidi_code,
                kuaidi_jdate = good_j_date,
                kuaidi_edate = good_e_date,
                desc = good_desc,
                is_need_jisong = need_jisong,
            )

            # 更新 good的 state_paishe = 8 拍摄中
            good.state_paishe = 8
            good.save()
            transaction.savepoint_commit(save_point)
        except Exception as err2:
            print(err2)
            transaction.savepoint_rollback(save_point)
            return JsonResponse({'code':'2','msg':'fail,please try again'})
        return JsonResponse({'code':'0','msg':'ok','url':'/photo/start/'})
        
    def delete(self,request):
        '''不拍摄 直接进入制作阶段'''
        delete = QueryDict(request.body)
        good_id = delete.get('good_id')
        try:
            good = Good.objects.get(pk=int(good_id))
        except Exception as err1:
            print(err1)
            return JsonResponse({'code':'1','msg':'unknown err'})

        GoodsNotPhotoToMakingPhase.objects.create(
            good = good,
            operator = request.user
        )
        good.state_paishe = 9   # 待制作
        good.save()
        return JsonResponse({'code':'0','msg':'ok','url':'/photo/start/'})





class CpmProductPhotoSYSXView(LoginRequiredMixin,View):
    '''摄影摄像页面'''
    def get(self,request):
        # 查询条件
        suppiler_val = request.GET.get('suppilerVal','')

        code = request.GET.get('code','')
        name = request.GET.get('name','')
        pinlei = request.GET.get('pinlei','')
        genzonger = request.GET.get('genzonger','')
        suppliers = request.GET.get('suppliers','')
        jibie = request.GET.get('jibie','')
        start = request.GET.get('start','')
        end = request.GET.get('end','')
        page = int(request.GET.get('p',1))

        # 首页进入  拍摄超期
        paishe_exceed = request.GET.get('paishe_exceed','')

        items = Good.objects.select_related().filter(state_paishe__exact=8).order_by('code')

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

        if genzonger:
            user_genzonger = get_object_or_404(User,pk=int(genzonger))
            items = items.filter(goods_detail_good__photo_genzonger__exact=user_genzonger)
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


        if paishe_exceed:
            paishe_exceed = []
            for good in items:
                order = GoodsPhotoStartPhase.objects.filter(good = good).filter(good__state_paishe = 8).order_by('-created_at').first()
                if order:
                    if not self.compute_caigou_exceed(order.kuaidi_edate):
                        paishe_exceed.append(good)
            items = paishe_exceed

        users = User.objects.filter(is_superuser = False,extension__role__name__in=[2,6]).select_related().distinct()

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

            setattr(item,'photo',item.goods_detail_good.order_by('-created_at').first())
        # 导出csv


        context = {
            'sysx':True,
            'users':users,
            'query_url':'/photo/sysx/',
            'msg':'待摄影摄像列表',
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
                'genzonger': genzonger or '',
                'suppliers': suppliers or '',
                'jibie': jibie or '',
                'start': start or '',
                'end': end or '',
                'paishe_exceed': paishe_exceed or '',
            })
        }
        # 查询参数返回
        if genzonger:
            genzonger = int(genzonger)
        url_query_data = {
            'suppiler_val':suppiler_val,
            'genzonger':genzonger,
            'suppliers':suppliers,
            'code':code,
            'name':name,
            'pinlei':pinlei,
            'start':start,
            'end':end,
            'jibie':jibie,
            'paishe_exceed':paishe_exceed,
            'base_domain':QINIU_BASE_DOMAIN,
        }
        page_data = get_pagination_data(paginator,page_obj)
        context.update(page_data)
        context.update(url_query_data)
        return render(request,'photo/product_ps_sysx.html',context=context) 

    def post(self,request):
        '''摄影摄像提交'''
        desc = request.POST.get('desc')
        real_date = request.POST.get('real_date')
        good_id = request.POST.get('good_id')
        good_photo_id = request.POST.get('good_photo_id')
        try:
            good = Good.objects.get(pk=int(good_id))
            good_photo = GoodsPhotoStartPhase.objects.get(pk=int(good_photo_id))
        except Exception as err1:
            print(err1)
            return JsonResponse({'code':'1','msg':'unknown err'})
        now = datetime.now()
        if real_date:
            str_p_date = real_date + ' ' + str(now.hour)+':'+str(now.minute)+':00'
            real_date = datetime.strptime(str_p_date,'%Y-%m-%d %H:%M:%S')
        GoodsSYSXingAndFinishPhase.objects.create(
            good = good,
            operator = request.user,
            real_date = real_date,
            desc = desc,
            photo_start = good_photo,
        )
        good.state_paishe = 9   # 待制作
        good.save()
        
        return JsonResponse({'code':'0','msg':'ok','url':'/photo/sysx/'})

    def compute_caigou_exceed(self,expected_data):
        '''计算采购 拍摄 制作是否超期'''
        # timeArray1 = time.strptime(expected_data, "%Y-%m-%d %H:%M:%S")  # 先转换为时间数组
        # timeStamp1 = int(time.mktime(timeArray))  # 转换为时间戳
        timeStamp1 = expected_data.timestamp()
        now_timestamp = datetime.now().timestamp()
        interval = timeStamp1 - now_timestamp 
        if interval > 0:
            return True
        else:
            return False

class CpmProductMeiGongZhiZuoView(LoginRequiredMixin,View):
    '''美工制作'''
    def get(self,request):
        # 查询条件
        suppiler_val = request.GET.get('suppilerVal','')

        code = request.GET.get('code','')
        name = request.GET.get('name','')
        pinlei = request.GET.get('pinlei','')
        chargers = request.GET.get('chargers','')
        suppliers = request.GET.get('suppliers','')
        suppiler_val = request.GET.get('suppiler_val','')
        jibie = request.GET.get('jibie','')
        page = int(request.GET.get('p',1))
  
        start_fp = request.GET.get('start_fp','')
        end_fp = request.GET.get('end_fp','')
        start_tj = request.GET.get('start_tj','')
        end_tj = request.GET.get('end_tj','')
        meigong = request.GET.get('meigong','')
        mk_state = request.GET.get('mk_state','')
     
        # 首页进入 制作超期
        zhizuo_exceed = request.GET.get('zhizuo_exceed','')

        items = Good.objects.select_related().filter(state_paishe__exact=9).order_by('code')

        # 处理查询条件
        if code:
            items = items.filter(code__icontains=code)
        if name:
            items = items.filter(name__icontains=name)
        if jibie:
            items = items.filter(jibie=jibie)

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

        # 先进行for遍历查询？
        # 分配开始日期 -- 结束日期
        if start_fp or end_fp:
            if start_fp:
                start_date = datetime.strptime(start_fp,'%Y-%m-%d')
            else:
                start_date = datetime(year=2019,month=9,day=1)
            if end_fp:
                end_date = datetime.strptime(end_fp,'%Y-%m-%d')
            else:
                end_date = datetime.today()
            mgzz_items = []
            for item in items:
                if len(item.goods_mgzz_phase.all()) != 0:
                    temp = item.goods_mgzz_phase.filter(mk_date__range=(start_date,end_date)).first()
                    if temp:
                        mgzz_items.append(item)
                    items = mgzz_items
        # 提交开始日期 -- 结束日期
        if start_tj or end_tj:
            if start_tj:
                start_date = datetime.strptime(start_tj,'%Y-%m-%d')
            else:
                start_date = datetime(year=2019,month=9,day=1)
            if end_tj:
                end_date = datetime.strptime(end_tj,'%Y-%m-%d')
            else:
                end_date = datetime.today()
            mgzz_items = []
            for item in items:
                if len(item.goods_mgzz_phase.all()) != 0:
                    temp = item.goods_mgzz_phase.filter(submit_date__range=(start_date,end_date)).first()
                    if temp:
                        mgzz_items.append(item)
                    items = mgzz_items
        if meigong:
            user_meigong = User.objects.get(pk=int(meigong))
            mgzz_items = []
            for item in items:
                temp = item.goods_mgzz_phase.filter(mk_to=user_meigong).first()
                if temp:
                    mgzz_items.append(item)
            items = mgzz_items

        if mk_state:
            # 因为默认是 0 没办法操作 ==0不操作
            if int(mk_state) != 0:
                mgzz_items = []
                for item in items:
                    temp = item.goods_mgzz_phase.all().filter(mk_state=int(mk_state)).first()
                    if temp:
                        mgzz_items.append(item)
                items = mgzz_items
            else:
                mgzz_items = []
                for item in items:
                    temp = item.goods_mgzz_phase.all()
                    if len(temp) == 0:
                        mgzz_items.append(item)
                items = mgzz_items

        if zhizuo_exceed:
            zhizuo_exceed = []
            for good in items:
                order = GoodsMGZZPhase.objects.filter(good = good).order_by('-created_at').filter(good__state_paishe = 9).first()
                if order:
                    if not self.compute_zhizuo_exceed(order.mk_date):
                        zhizuo_exceed.append(good)
            items = zhizuo_exceed


        users = User.objects.filter(is_superuser = False,extension__role__name__in=[2,6]).select_related().distinct()
        users_meigong = User.objects.filter(is_superuser = False,extension__role__name=2).select_related().distinct()

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
                
            setattr(item,'photo',item.goods_detail_good.order_by('-created_at').first())
            setattr(item,'pingshen',item.goods_pingshen_phase.order_by('-created_at').first())
            setattr(item,'mgzz',item.goods_mgzz_phase.order_by('-created_at').first())
        # 导出csv


        context = {
            'mgzz':True,
            'users':users,
            'mg_check':GOOD_MEIGONG_CHECK,
            'mk_state_for':GOOD_MEIGONG_MK_STATE,
            'users_meigong':users_meigong,
            'chargers_all': User.objects.filter(extension__role__name=0),
            'query_url':'/photo/mgzz/',
            'msg':'待制作列表',
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
                'suppliers': suppliers or '',
                'suppiler_val': suppiler_val or '',
                'jibie': jibie or '',
                'zhizuo_exceed': zhizuo_exceed or '',

                'mk_state': mk_state or '',
                'end_tj': end_tj or '',
                'start_tj': start_tj or '',
                'end_fp': end_fp or '',
                'start_fp': start_fp or '',
                'meigong': meigong or '',
             
            })
        }
        # 查询参数返回
        if chargers:
            chargers = int(chargers)
        if mk_state:
            mk_state = int(mk_state)
        if meigong:
            meigong = int(meigong)
        url_query_data = {
            'suppiler_val':suppiler_val,
            'chargers':chargers,
            'suppliers':suppliers,
            'code':code,
            'name':name,
            'pinlei':pinlei,
            'jibie':jibie,
            'mk_state':mk_state,
            'end_tj':end_tj,
            'start_tj':start_tj,
            'end_fp':end_fp,
            'start_fp':start_fp,
            'meigong':meigong,
            'zhizuo_exceed':zhizuo_exceed,
            'base_domain':QINIU_BASE_DOMAIN,
        }
        page_data = get_pagination_data(paginator,page_obj)
        context.update(page_data)
        context.update(url_query_data)
        return render(request,'photo/product_ps_mgzz.html',context=context) 



    def compute_zhizuo_exceed(self,expected_data):
        '''计算制作阶段是否超期  在分配了任务后后七天内没有提交就判断为超期'''
        timeStamp1 = expected_data.timestamp()
        now_timestamp = datetime.now().timestamp()
        interval = now_timestamp -timeStamp1
        day7 = GOOD_MGZZ_EXPIRE_TIME * 24 * 3600 
        if interval < day7:
            return True
        else:
            # 超期
            return False

@method_decorator(csrf_exempt, name='dispatch')
class CpmProductMGZZFenpeiView(View):
    '''美工制作分配'''
    @transaction.atomic
    def get(self,request):
        '''分配'''
        good_id = request.GET.get('good_id')
        maker = request.GET.get('maker')
        fenpei_date = request.GET.get('fenpei_date')
        fenpei_desc = request.GET.get('fenpei_desc')

        # 处理日期格式
        now = datetime.now()
        if fenpei_date:
            str_fenpei_date= fenpei_date + ' ' + str(now.hour)+':'+str(now.minute)+':00'
            fenpei_date = datetime.strptime(str_fenpei_date,'%Y-%m-%d %H:%M:%S')
        else:
            fenpei_date = now
        try:
            good = Good.objects.get(pk=int(good_id))
            maker_user = User.objects.get(pk=int(maker))
        except Exception as err1:
            print(err1)
            return JsonResponse({'code':'2','msg':'请正确操作'})
        
        save_id = transaction.savepoint()
        try:
            GoodsMGZZPhase.objects.create(
                good = good,
                mk_operator = request.user,
                mk_to = maker_user,
                mk_date = fenpei_date,
                mk_desc = fenpei_desc,
                mk_state = 1
            )
            transaction.savepoint_commit(save_id)
        except Exception as err2:
            transaction.savepoint_rollback(save_id)
            print(err2)
            return JsonResponse({'code':'7','msg':'处理失败,请重试'})


        return JsonResponse({'code':'0','msg':'ok'})

    @transaction.atomic
    def post(self,request):
        '''提交'''
        good_id = request.POST.get('good_id')
        mgzz_id = request.POST.get('mgzz_id')
        try:
            good = Good.objects.get(pk=int(good_id))
            mgzz = GoodsMGZZPhase.objects.get(pk=int(mgzz_id))
        except Exception as err1:
            print(err1)
            return JsonResponse({'code':'2','msg':'请正确操作'})
        
        save_id = transaction.savepoint()
        try:
            mgzz.submit_operator = request.user
            mgzz.submit_date = datetime.now()
            mgzz.mk_state = 2
            mgzz.save()
            transaction.savepoint_commit(save_id)
        except Exception as err2:
            transaction.savepoint_rollback(save_id)
            print(err2)
            return JsonResponse({'code':'7','msg':'处理失败,请重试'})
        return JsonResponse({'code':'0','msg':'ok'})

    @transaction.atomic
    def put(self,request):
        '''美工制作审核'''
        put = QueryDict(request.body)
        good_id = put.get('good_id')
        mgzz_id = put.get('mgzz_id')
        check = put.get('check')
        check_desc = put.get('check_desc')
        try:
            good = Good.objects.get(pk=int(good_id))
            mgzz = GoodsMGZZPhase.objects.get(pk=int(mgzz_id))
        except Exception as err1:
            print(err1)
            return JsonResponse({'code':'2','msg':'请正确操作'})

            #   (0, '通过'),      
            # (1, '不通过'),
        save_id = transaction.savepoint()
        try:
            if check == '0':
                GoodsMGZZCheckDetail.objects.create(
                    mgzz = mgzz,
                    check_operator = request.user,
                    check_desc = check_desc,
                    check_state = int(check)
                )
                # 将 审核通过 更新产品状态到 10 待上架
                good.state_paishe = 10
                if good.state_caigou == 10:
                    good.state_sale = 10
                good.save()
                # 更新 GoodsMGZZPhase 的mk_state =3
                mgzz.mk_state =3
                mgzz.save()
            elif check == '1':
                GoodsMGZZCheckDetail.objects.create(
                    mgzz = mgzz,
                    check_operator = request.user,
                    check_desc = check_desc,
                    check_state = int(check)
                )
                mgzz.mk_state = 1
                mgzz.save()
            else:
                return JsonResponse({'code':'6','msg':'状态码异常'})
            transaction.savepoint_commit(save_id)
        except Exception as err2:
            print(err2)
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'code':'7','msg':'处理失败,请重试'})
        return JsonResponse({'code':'0','msg':'ok'})