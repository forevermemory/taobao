from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.http import HttpResponse,JsonResponse,QueryDict
from django.core import serializers
from django.contrib.auth.models import User
from django.db import transaction
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q,F
from django_redis import get_redis_connection


from utils.export_csv import export_csv
from utils.login_required import LoginRequiredMixin
from utils.page_util import get_pagination_data
from utils.baidu_image_retrieve import BaiduImageSearch
import json

from datetime import datetime
from urllib import parse
from cpm.settings import PAGE_SIZE,QINIU_BASE_DOMAIN
from cpm.models import Category,Good,GoodsSku,Supplier,GoodsSelectPhase,SupplierChange,ChargerChange,Shop,SkuToShop,GoodsShangjiaPhase,GOODS_STORAGE_STATE,GOOD_MEIGONG_CHECK,GOOD_MEIGONG_MK_STATE,GOOD_FENGCUN_STATE,GoodsFengcunPhase,GoodsQifenPhase,GOOD_TAOTAI_STATE,GoodsTaotaiPhase,GoodsTuishiPhase


@method_decorator(csrf_exempt, name='dispatch')
class CpmProductShangjiaView(LoginRequiredMixin,View):
    '''上架阶段'''
    def get(self,request):
        # 查询条件
        code = request.GET.get('code','')
        name = request.GET.get('name','')
        pinlei = request.GET.get('pinlei','')
        jibie = request.GET.get('jibie','')
        chargers = request.GET.get('chargers','')
        suppliers = request.GET.get('suppliers','')
        suppiler_val = request.GET.get('suppiler_val','')
        # 新的查询条件
        ruku_start = request.GET.get('ruku_start','')
        ruku_end = request.GET.get('ruku_end','')
        ruku_state = request.GET.get('ruku_state','')
        zhizuo_start = request.GET.get('zhizuo_start','')
        zhizuo_end = request.GET.get('zhizuo_end','')
        zhizuo_state = request.GET.get('zhizuo_state','')

        un_shop = request.GET.get('un_shop','')
        do_shop = request.GET.get('do_shop','')
        never_shangjia = request.GET.get('never_shangjia','')

        # 上过架的产品
        shangjia_done = request.GET.get('shangjia_done','')
        to_shangjia = request.GET.get('to_shangjia','')

        page = int(request.GET.get('p',1))
        items = Good.objects.select_related().filter(Q(state_caigou=10) | Q(state_paishe=10)| Q(state_sale__in = [10,11])).exclude(state_sale__in = [15,]).order_by('code')
        # 处理查询条件
        if code:
            items = items.filter(code__icontains=code)
        if name:
            items = items.filter(name__icontains=name)
        if jibie:
            items = items.filter(jibie=jibie)
        if pinlei:
            cates = Category.objects.filter(name__icontains=pinlei)
            items = items.filter(cate__in=cates).distinct()

        # 多对多条件查询 https://docs.djangoproject.com/en/2.2/topics/db/examples/many_to_many/
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


        # 入库查询
        if ruku_state:
            temp_items = []
            for item in items:
                if len(item.goods_ruku_good.all()) != 0:
                    if item.goods_ruku_good.filter(result=int(ruku_state))[0]:
                        temp_items.append(item)
            items = temp_items

        if ruku_start or ruku_end:
            if ruku_start:
                start_date = datetime.strptime(ruku_start,'%Y-%m-%d')
            else:
                start_date = datetime(year=2019,month=9,day=1)
            if ruku_end:
                end_date = datetime.strptime(ruku_end,'%Y-%m-%d')
            else:
                end_date = datetime.today()
            temp_items = []
            for item in items:
                if len(item.goods_ruku_good.all()) != 0:
                    temp = item.goods_ruku_good.filter(created_at__range=(start_date,end_date)).first()
                    if temp:
                        temp_items.append(item)
                    items = temp_items
        # 制作查询
        if zhizuo_start or zhizuo_end:
            if zhizuo_start:
                start_date = datetime.strptime(zhizuo_start,'%Y-%m-%d')
            else:
                start_date = datetime(year=2019,month=9,day=1)
            if zhizuo_end:
                end_date = datetime.strptime(zhizuo_end,'%Y-%m-%d')
            else:
                end_date = datetime.today()
            temp_items = []
            for item in items:
                if len(item.goods_mgzz_phase.all()) != 0:
                    temp = item.goods_mgzz_phase.filter(updated_at__range=(start_date,end_date)).first()
                    if temp:
                        temp_items.append(item)
                    items = temp_items

        if zhizuo_state:
            temp_items = []
            for item in items:
                if len(item.goods_mgzz_phase.all()) != 0:
                    temp = item.goods_mgzz_phase.filter(mk_state=int(zhizuo_state)).first()
                    if temp:
                        temp_items.append(item)
            items = temp_items
        if never_shangjia == 'true':
            # 选中 是没有上过架的产品
            temp_items = []
            for item in items:
                for sku in item.goods_skus.all():
                    if len(sku.sku2shop_sku.all()) == 0:
                        temp_items.append(item)
                        break
            items = temp_items

        # 查询一个店铺是否上架过某些产品
        if un_shop:
            shop = Shop.objects.get(pk=int(un_shop))
            temp_items = []
            for item in items:
                length_skus = len(item.goods_skus.all())
                count_sku = 0
                ################################
                for sku in item.goods_skus.all():
                    if not sku.sku2shop_sku.first() :
                        temp_items.append(item)
                        break
                    print('循环下一个sku')
                    #####
                    # length = len(sku.sku2shop_sku.all())
                    for sku_shop in sku.sku2shop_sku.all():
                        # print('执行了sku_shop****---'+str(sku_shop.sku_in_shop_state))
                        if sku_shop.shop == shop:
                            if sku_shop.sku_in_shop_state == 10:
                                count_sku += 1
                ##################################
                # print(count_sku)
                if count_sku == length_skus:
                    temp_items.append(item)
            items = temp_items
        # 查询已经在某个店铺上架的产品
        if do_shop:
            shop = Shop.objects.get(pk=int(do_shop))
            temp_items = []
            for item in items:
                # length_skus = len(item.goods_skus.all())
                # print(length_skus)
                count_sku = 0
                ################################
                for sku in item.goods_skus.all():
                    if not sku.sku2shop_sku.first() :
                        break
                    print('循环下一个item')
                    #####
                    # length = len(sku.sku2shop_sku.all())
                    for sku_shop in sku.sku2shop_sku.all():  # 4
                        # print('执行了sku_shop****---'+str(sku_shop.sku_in_shop_state))
                        if sku_shop.shop == shop:
                            if sku_shop.sku_in_shop_state == 11:
                                count_sku += 1
                ##################################
                # print(count_sku)
                if count_sku > 0:
                    temp_items.append(item)
            items = temp_items

        if shangjia_done:
            # temp_items = []
            # for item in items:
            #     length_skus = len(item.goods_skus.all())
            #     for sku in item.goods_skus.all():
            #         if sku.sku2shop_sku.first() :
            #             temp_items.append(item)
            # items = list(set(temp_items))
            items = items.filter(state_sale = 11)

        if to_shangjia:
            items = items.filter(state_sale=10)

        # 分页
        len_items = len(items)  # 总的记录数
        paginator = Paginator(items,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1
        page_obj = paginator.page(page)
        items = page_obj.object_list
        
        # 条件查询结束
        if not items:
            items = []
        for item in items:
            setattr(item,'suppliers',item.suppiler.all())
            setattr(item,'chargers',item.charger.all())
            setattr(item,'caigou',item.goods_buy_good.order_by('-created_at').first())
            setattr(item,'ruku',item.goods_ruku_good.order_by('-created_at').first())
            if item.goods_mgzz_phase.order_by('-created_at').first():
                setattr(item,'mgzz_ckeck',item.goods_mgzz_phase.order_by('-created_at').first())
            # if len(item.goods_skus.all()) > 0:
            #     setattr(item,'skus',item.goods_skus.all())
            #     setattr(item,'has_skus',True)
            
            temp_list = []
            for sku in item.goods_skus.all():
                for sku_2_shop in sku.sku2shop_sku.all():
                    if sku_2_shop.sku_in_shop_state == 11:
                        temp_list.append(sku_2_shop.shop)
            setattr(item,'shops_shangjia',list(set(temp_list)))   # 去重




        context = {
            'shangjia':True,
            'chargers_all': User.objects.filter(extension__role__name=0),
            'query_url':'/sale/shangjia/',
            'msg':'上架管理',
            'ruku_state_option':GOODS_STORAGE_STATE,
            'zhizuo_state_option':GOOD_MEIGONG_MK_STATE,
            'shops':Shop.objects.all(),
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
                'jibie': jibie or '',
                'chargers': chargers or '',
                'suppliers': suppliers or '',
                'ruku_start': ruku_start or '',
                'ruku_end': ruku_end or '',
                'ruku_state': ruku_state or '',
                'zhizuo_start': zhizuo_start or '',
                'zhizuo_end': zhizuo_end or '',
                'zhizuo_state': zhizuo_state or '',
                'un_shop': un_shop or '',
                'do_shop': do_shop or '',
                'never_shangjia': never_shangjia or '',
                'suppiler_val': suppiler_val or '',
                'shangjia_done': shangjia_done or '',
                'to_shangjia': to_shangjia or '',
             
            })
        }
        # 控制扩展显示和隐藏
        # 查询参数返回
        if chargers:
            chargers = int(chargers)
        if ruku_state:
            ruku_state = int(ruku_state)
        if zhizuo_state:
            zhizuo_state = int(zhizuo_state)
        if un_shop:
            un_shop = int(un_shop)
        if do_shop:
            do_shop = int(do_shop)
        if never_shangjia == 'true':
            never_shangjia = '1'
        url_query_data = {
            'suppiler_val':suppiler_val,
            'suppliers':suppliers,
            'chargers':chargers,
            'code':code,
            'name':name,
            'jibie':jibie,
            'pinlei':pinlei,
            'ruku_start':ruku_start,
            'ruku_end':ruku_end,
            'ruku_state':ruku_state,
            'zhizuo_start':zhizuo_start,
            'zhizuo_end':zhizuo_end,
            'zhizuo_state':zhizuo_state,
            'never_shangjia':never_shangjia,
            'un_shop':un_shop,
            'do_shop':do_shop,
            'shangjia_done':shangjia_done,
            'to_shangjia':to_shangjia,
            'base_domain':QINIU_BASE_DOMAIN,
        }
        page_data = get_pagination_data(paginator,page_obj)
        context.update(page_data)
        context.update(url_query_data)
        return render(request,'sale/product_shangjia.html',context=context)
    
    @transaction.atomic
    def post(self,request):
        '''第一次上架'''
        good_id = request.POST.get('good_id')
        sku_shop_temp = request.POST.get('sku_shop')
        sku_shops = json.loads(sku_shop_temp)

        good = Good.objects.get(pk=int(good_id))
        save_id = transaction.savepoint()
        for sku_shop in sku_shops:
            sku_id = sku_shop['sku_id']
            results = sku_shop['result']
            sku = GoodsSku.objects.get(pk=int(sku_id))
            try:
                for result in results:
                    if not result['is_checked']:
                        SkuToShop.objects.create(
                            sku = sku,
                            shop = Shop.objects.get(pk=int(result['shop_id'])),
                            sku_in_shop_state = 10
                        )
                    elif result['is_checked']:
                        SkuToShop.objects.create(
                            sku = sku,
                            shop = Shop.objects.get(pk=int(result['shop_id'])),
                            sku_in_shop_state = 11
                        )
            except Exception as err2:
                print(err2)
                transaction.savepoint_rollback(save_id)
                return JsonResponse({'code':'3','msg':'处理失败'})
        good.state_sale = 11
        # 记录上架阶段 GoodsShangjiaPhase
        GoodsShangjiaPhase.objects.create(
            good = good,
            operator = request.user,
        )
        good.save()
        transaction.savepoint_commit(save_id)
        return JsonResponse({'code':'0','msg':'ok'})


class CpmProductShangjiaEditView(LoginRequiredMixin,View):
    ''' 管理员 编辑上架 非第一次上架   后面用于权限控制'''
    @transaction.atomic
    def post(self,request):
        good_id = request.POST.get('good_id')
        sku_shop_temp = request.POST.get('sku_shop')
        sku_shops = json.loads(sku_shop_temp)

        good = Good.objects.get(pk=int(good_id))
        for sku_shop in sku_shops:
            sku_id = sku_shop['sku_id']
            results = sku_shop['result']
            sku = GoodsSku.objects.get(pk=int(sku_id))
            try:
                for result in results:
                    if not result['is_checked']:
                        # print(result['is_checked'])  # false 未选中
                        # print(result['shop2_id']) 
                        sku_2_shop = SkuToShop.objects.get(pk=int(result['shop2_id']))
                        sku_2_shop.sku_in_shop_state = 10
                        sku_2_shop.save()
                    elif result['is_checked']:
                        # print(result['is_checked'])  # true
                        # print(result['shop2_id'])  # true
                        sku_2_shop = SkuToShop.objects.get(pk=int(result['shop2_id']))
                        sku_2_shop.sku_in_shop_state = 11
                        sku_2_shop.save()
            except Exception as err2:
                print(err2)
                return JsonResponse({'code':'3','msg':'处理失败'})

        # 记录上架阶段 GoodsShangjiaPhase 累计上架次数自增1
        good.goods_shangjia_sku.update(shangjia_times = F("shangjia_times") + 1)
        return JsonResponse({'code':'0','msg':'ok'})

@method_decorator(csrf_exempt, name='dispatch')
class ShangjiaQuerySkusView(LoginRequiredMixin,View):
    '''查询sku列表接口'''
    def get(self,request):
        good_id = request.GET.get('good_id')
        try:
            good = Good.objects.get(pk=int(good_id))
            skus = good.goods_skus.all()
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'操作失败'})
        return JsonResponse({'code':'0','skus':serializers.serialize('json',skus),'domain':QINIU_BASE_DOMAIN})

    def post(self,request):
        '''获取所有店铺接口 后面会根据当前用户来查询他负责的店铺'''
        try:
            shops = Shop.objects.all() 
            shop_array = []
            for shop in shops:
                setattr(shop,'skus',shop.sku2shop_shop.all())
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'操作失败'})
        return JsonResponse({'code':'0','shops':serializers.serialize('json',shops)})

    def put(self,request):
        '''获取所有店铺接口 同时查询出来该店铺的所有sku信息'''
        put = QueryDict(request.body)
        good_id = put.get('good_id')
        # good_id = request.GET.get('good_id')
        try:
            shops = Shop.objects.all() 
            good = Good.objects.get(pk=int(good_id))
            good_skus = good.goods_skus.all()
            shop_array = []
            for shop in shops:
                # setattr(shop,'skus',shop.sku2shop_shop.all())
                temp_shop = {}
                skus = shop.sku2shop_shop.all()
                sku_array = []
                for sku2shop in skus:
                    # 只查询sku 在这件产品里面的
                    if sku2shop.sku in good_skus:
                        temp = {}
                        temp['shop2_id'] = sku2shop.id
                        temp['sku_id'] = sku2shop.sku.id
                        temp['sku_code'] = sku2shop.sku.sku_code
                        temp['sku_name'] = sku2shop.sku.sku_name
                        temp['sku_image'] = sku2shop.sku.sku_image
                        temp['shop_id'] = sku2shop.shop.id
                        temp['sku_in_shop_state'] = sku2shop.sku_in_shop_state
                        sku_array.append(temp)
                temp_shop['shop_id'] = shop.id
                temp_shop['shop_name'] = shop.name
                temp_shop['shop_skus'] = sku_array
                shop_array.append(temp_shop)
                    
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'操作失败'})
        return JsonResponse({'code':'0','shops':json.dumps(shop_array)})



@method_decorator(csrf_exempt, name='dispatch')
class CpmProductFengcunView(LoginRequiredMixin,View):
    '''封存 启封阶段'''
    def get(self,request):
        # 查询条件
        code = request.GET.get('code','')
        name = request.GET.get('name','')
        pinlei = request.GET.get('pinlei','')
        jibie = request.GET.get('jibie','')
        chargers = request.GET.get('chargers','')
        suppliers = request.GET.get('suppliers','')
        suppiler_val = request.GET.get('suppiler_val','')
        fengcun_state = request.GET.get('fengcun_state','')
        # 新的查询条件
        # 是否封存
        fengcun_done = request.GET.get('fengcun_done','')

        page = int(request.GET.get('p',1))
        items = Good.objects.select_related().filter(state_sale__in=[11,15]).order_by('code')
        # 处理查询条件
        if code:
            items = items.filter(code__icontains=code)
        if name:
            items = items.filter(name__icontains=name)
        if jibie:
            items = items.filter(jibie=jibie)
        if pinlei:
            cates = Category.objects.filter(name__icontains=pinlei)
            items = items.filter(cate__in=cates).distinct()

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

        if fengcun_state:
            items = items.filter(state_sale=fengcun_state)

        if fengcun_done:
            if fengcun_done == '1':
                # 已封存
                items = items.filter(state_sale=15)

            elif fengcun_done == '0':
                # 待封存
                items = items.filter(state_sale=11)
        # 条件查询结束
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
            setattr(item,'suppliers',item.suppiler.all())
            setattr(item,'chargers',item.charger.all())
            setattr(item,'caigou',item.goods_buy_good.order_by('-created_at').first())
            setattr(item,'ruku',item.goods_ruku_good.order_by('-created_at').first())
            # if len(item.goods_skus.all()) > 0:
            #     setattr(item,'skus',item.goods_skus.all())
            #     setattr(item,'has_skus',True)
            # 查询已上架店铺
            temp_list = []
            for sku in item.goods_skus.all():
                for sku_2_shop in sku.sku2shop_sku.all():
                    if sku_2_shop.sku_in_shop_state == 11:
                        temp_list.append(sku_2_shop.shop)
            setattr(item,'shops_shangjia',list(set(temp_list)))   # 去重



        context = {
            'fengcun':True,
            'chargers_all': User.objects.filter(extension__role__name=0),
            'query_url':'/sale/fengcun/',
            'msg':'封存启封管理',
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'fengcun_state_option': GOOD_FENGCUN_STATE,
            'last_pages':len_items/PAGE_SIZE +1,
            # 查询参数
            'url_query': '&'+parse.urlencode({   
                # 'p': page or '',
                'code': code or '',
                'name': name or '',
                'pinlei': pinlei or '',
                'jibie': jibie or '',
                'chargers': chargers or '',
                'suppliers': suppliers or '',
                'fengcun_state': fengcun_state or '',
                'suppiler_val': suppiler_val or '',
                'fengcun_done': fengcun_done or '',
             
            })
        }
        # 控制扩展显示和隐藏
        # 查询参数返回
        if chargers:
            chargers = int(chargers)
        if fengcun_state:
            fengcun_state = int(fengcun_state)
        url_query_data = {
            'suppiler_val':suppiler_val,
            'suppliers':suppliers,
            'chargers':chargers,
            'code':code,
            'name':name,
            'jibie':jibie,
            'fengcun_state':fengcun_state,
            'pinlei':pinlei,
            'fengcun_done':fengcun_done,
            'base_domain':QINIU_BASE_DOMAIN,
        }
        page_data = get_pagination_data(paginator,page_obj)
        context.update(page_data)
        context.update(url_query_data)
        return render(request,'sale/product_fengcun.html',context=context)

    @transaction.atomic
    def post(self,request):
        '''封存'''
        good_id = request.POST.get('good_id')
        try:
            good = Good.objects.get(pk=int(good_id))
            # 产品状态为上架的可以点击封存，产品状态转换为待启封，且将上架店铺设置为空。
            skus = good.goods_skus.all()
            save_id = transaction.savepoint()
            for sku in skus:
                # sku.sku2shop_sku.clear()
                sku.sku2shop_sku.all().delete()
            good.state_sale = 15
            good.save()
            GoodsFengcunPhase.objects.create(
                operator = request.user,
                good = good
            )
            transaction.savepoint_commit(save_id)
        except Exception as err1:
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'code':'1','msg':'操作失败,请刷新重试!'})
        return JsonResponse({'code':'0','msg':'ok'})
    
    def put(self,request):
        '''启封'''
        put = QueryDict(request.body)
        good_id = put.get('good_id')
        try:
            good = Good.objects.get(pk=int(good_id))
            # 产品状态为待启封的可以点击启封，产品状态转换为待上架。 
            save_id = transaction.savepoint()
            good.state_sale = 10
            good.save()
            GoodsQifenPhase.objects.create(
                operator = request.user,
                good = good
            )
            transaction.savepoint_commit(save_id)
        except Exception as err1:
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'code':'1','msg':'操作失败,请刷新重试!'})
        return JsonResponse({'code':'0','msg':'ok'})
        

@method_decorator(csrf_exempt, name='dispatch')
class CpmProductTaotaiView(LoginRequiredMixin,View):
    '''淘汰管理'''
    def get(self,request):
        # 查询条件
        code = request.GET.get('code','')
        name = request.GET.get('name','')
        pinlei = request.GET.get('pinlei','')
        jibie = request.GET.get('jibie','')
        chargers = request.GET.get('chargers','')
        suppliers = request.GET.get('suppliers','')
        suppiler_val = request.GET.get('suppiler_val','')
        taotai_state = request.GET.get('taotai_state','')
        # 新的查询条件

        tuishi_done = request.GET.get('tuishi_done','')

        page = int(request.GET.get('p',1))
        items = Good.objects.select_related().filter(state_sale__in=[11,12,13]).order_by('code')
        # 处理查询条件
        if code:
            items = items.filter(code__icontains=code)
        if name:
            items = items.filter(name__icontains=name)
        if jibie:
            items = items.filter(jibie=jibie)
        if pinlei:
            cates = Category.objects.filter(name__icontains=pinlei)
            items = items.filter(cate__in=cates).distinct()

        # 多对多条件查询 https://docs.djangoproject.com/en/2.2/topics/db/examples/many_to_many/
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

        if taotai_state:
            items = items.filter(state_sale=taotai_state)

        if tuishi_done:
            if tuishi_done == '1':
                # 已淘汰
                items = items.filter(state_sale=13)

            elif tuishi_done == '0':
                # 待淘汰
                items = items.filter(state_sale=12)
        # 条件查询结束
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
            setattr(item,'suppliers',item.suppiler.all())
            setattr(item,'chargers',item.charger.all())
            setattr(item,'caigou',item.goods_buy_good.order_by('-created_at').first())
            setattr(item,'ruku',item.goods_ruku_good.order_by('-created_at').first())
            # if len(item.goods_skus.all()) > 0:
            #     setattr(item,'skus',item.goods_skus.all())
            #     setattr(item,'has_skus',True)
            # 查询已上架店铺
            temp_list = []
            for sku in item.goods_skus.all():
                for sku_2_shop in sku.sku2shop_sku.all():
                    if sku_2_shop.sku_in_shop_state == 11:
                        temp_list.append(sku_2_shop.shop)
            setattr(item,'shops_shangjia',list(set(temp_list)))   # 去重



        context = {
            'taotai':True,
            'chargers_all': User.objects.filter(extension__role__name=0),
            'query_url':'/sale/taotai/',
            'msg':'淘汰退市管理',
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'taotai_state_option': GOOD_TAOTAI_STATE,
            'last_pages':len_items/PAGE_SIZE +1,
            # 查询参数
            'url_query': '&'+parse.urlencode({   
                # 'p': page or '',
                'code': code or '',
                'name': name or '',
                'pinlei': pinlei or '',
                'jibie': jibie or '',
                'chargers': chargers or '',
                'suppliers': suppliers or '',
                'taotai_state': taotai_state or '',
                'suppiler_val': suppiler_val or '',
                'tuishi_done': tuishi_done or '',
             
            })
        }
        # 控制扩展显示和隐藏
        # 查询参数返回
        if chargers:
            chargers = int(chargers)
        if taotai_state:
            taotai_state = int(taotai_state)
        url_query_data = {
            'suppiler_val':suppiler_val,
            'suppliers':suppliers,
            'chargers':chargers,
            'code':code,
            'name':name,
            'jibie':jibie,
            'taotai_state':taotai_state,
            'pinlei':pinlei,
            'tuishi_done':tuishi_done,
            'base_domain':QINIU_BASE_DOMAIN,
        }
        page_data = get_pagination_data(paginator,page_obj)
        context.update(page_data)
        context.update(url_query_data)
        return render(request,'sale/product_taotai.html',context=context)

    @transaction.atomic
    def post(self,request):
        '''淘汰'''
        good_id = request.POST.get('good_id')
        try:
            good = Good.objects.get(pk=int(good_id))
            # 产品状态为上架的可以点击淘汰，产品状态转换为待淘汰
            save_id = transaction.savepoint()
            good.state_sale = 12  # 待淘汰
            good.save()
            GoodsTaotaiPhase.objects.create(
                operator = request.user,
                good = good
            )
            transaction.savepoint_commit(save_id)
        except Exception as err1:
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'code':'1','msg':'操作失败,请刷新重试!'})
        return JsonResponse({'code':'0','msg':'ok'})

    @transaction.atomic
    def put(self,request):
        '''退市'''
        put = QueryDict(request.body)
        good_id = put.get('good_id')
        try:
            good = Good.objects.get(pk=int(good_id))
            # 产品状态为待淘汰的可以点击退市，产品状态转换为已退市，并将上架店铺设置为空。 
            skus = good.goods_skus.all()
            save_id = transaction.savepoint()  
            for sku in skus:
                # sku.sku2shop_sku.clear()
                sku.sku2shop_sku.all().delete()  
            good.state_sale = 13  # (13, '退市'),
            good.save()
            GoodsTuishiPhase.objects.create(
                operator = request.user,
                good = good
            )
            transaction.savepoint_commit(save_id)
        except Exception as err1:
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'code':'1','msg':'操作失败,请刷新重试!'})
        return JsonResponse({'code':'0','msg':'ok'})