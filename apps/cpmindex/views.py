from django.shortcuts import render,redirect,reverse,get_object_or_404
from django.views.generic import View
from django.http import HttpResponse,JsonResponse,QueryDict
from django.core import serializers
from django.contrib.auth.models import User
from django.db.models import Q,F,Sum,functions,Max,Avg

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django_redis import get_redis_connection
from django.core import serializers

from utils.export_csv import export_csv
from utils.login_required import LoginRequiredMixin
from utils.redis_util import get_redis_conn
from utils.thirteen_month_ago import get_13_month_list
from utils.page_util import get_pagination_data

from datetime import datetime,timedelta,date
from cpm.settings import PAGE_SIZE,QINIU_BASE_DOMAIN,GOOD_RUKU_EXPIRE_TIME,GOOD_MGZZ_EXPIRE_TIME
from calendar import monthrange
 
import json,math
from urllib import parse
from datetime import datetime

from cpmauth.models import Role
from cpm.models import Category,Good,GoodsBrand,GoodsSku,TagChangjing,TagDingwei,Supplier,GoodsSelectPhase,SupplierChange,ChargerChange,GoodsPingshenPhase,GOOD_PINGSHEN_CANCEL,GOOD_PINGSHEN_WAIT,GoodsPurchasePhase,GoodsDianAndFenPhase,GoodsYanhuoPhase,GoodRukuPhase,GoodsPhotoStartPhase,GoodsNotPhotoToMakingPhase,GoodsSYSXingAndFinishPhase,GoodsMGZZPhase,GoodsMGZZCheckDetail,SkuToShop,GoodsShangjiaPhase,GoodsFengcunPhase,GoodsQifenPhase,GoodsTaotaiPhase,GoodsTuishiPhase,IndexHistory,INDEX_SALE_ITEMS,INDEX_SHANGXIN_ITEMS,Shop,SkuToShop



class CpmIndexView(LoginRequiredMixin,View):
    '''首页看板'''
    def get(self,request):
        return render(request,'index/index.html',{'msg':'首页'})
    # (0, '待评审'),
    # (1, '待创建新品'),
    # (2, '终止'),
    # (3, '待采购'),
    # (4, '待分货点货'),
    # (5, '待验货'),
    # (6, '待入库'),
    # (7, '待拍摄'),
    # (8, '拍摄中'),
    # (9, '待制作'),
    # (10, '待上架'),
    # (11, '已上架'),
    # (12, '待淘汰'),
    # (13, '退市'),
    # (14, '待封存'),
    # (15, '待启封'),

@method_decorator(csrf_exempt, name='dispatch')
class CpmGetEchartDataView(View):
    '''获取  echart 数据的api'''
    def get(self,request):
        caigouDay7 = request.GET.get('caigouDay7')
        caigouYesterday = request.GET.get('caigouYesterday')
        caigouDay30 = request.GET.get('caigouDay30')
        caigouShishi = request.GET.get('caigouShishi')
        caigouWeek = request.GET.get('caigouWeek')
        caigouMonth = request.GET.get('caigouMonth')

    
        dayRange = request.GET.get('dayRange')

        today_date = datetime.today().date()
        one_day_ago = today_date + timedelta(days=-1)

        # 根据天的区间查询
        if dayRange:
            day_range = []
            for day in dayRange.split('-'):
                day_range.append(datetime.strptime(day.strip(),'%Y/%m/%d').date())
            orders = IndexHistory.objects.filter(date__range=(day_range[0],day_range[1])).order_by('-date')
            return JsonResponse({'code':'0','data':serializers.serialize('json',orders)})
                        

        # 以月度为尺度
        if caigouMonth:
            # 计算时间
            thirteen_month = today_date.month-1
            last_year = today_date.year-1
            if today_date.month == 1:
                thirteen_month = 12
                last_year = today_date.year-2
                
            thirteen_month_ago = date(last_year,thirteen_month,1)

            # 获取近13个月份数据
            one_year_data = IndexHistory.objects.filter(date__gte = thirteen_month_ago)
            # 分组统计每个月的数据
            sum_res = one_year_data.annotate(
                    year=functions.ExtractYear('date'),
                    month=functions.ExtractMonth('date')
                    ).values('year', 'month').order_by('-year', '-month').annotate(
                            caigou = Avg('caigou'),
                            ruku = Avg('ruku'),
                            paishe = Avg('paishe'),
                            zhizuo = Avg('zhizuo'),
                            shangjia = Avg('shangjia'),
                            shangjia_done = Avg('shangjia_done'),
                            taotai = Avg('taotai'),
                            fengcun = Avg('fengcun'),
                            fengcun_done = Avg('fengcun_done'),
                            tuishi_done = Avg('tuishi_done'),
                            caigou_exceed = Avg('caigou_exceed'),
                            ruku_exceed = Avg('ruku_exceed'),
                            paishe_exceed = Avg('paishe_exceed'),
                            zhizuo_exceed = Avg('zhizuo_exceed'),
                        )
            # ceil
            for su in sum_res:
                for key in su:
                    su[key] = math.ceil(su[key])
            if len(sum_res) != 13:
                # 空数据填充前面月份的数据
                thirteen = get_13_month_list()
                sum_res_list =list(sum_res)
                for i in range(len(sum_res),13):
                    sum_res_list.append({'year': thirteen[i][:4], 'month': thirteen[i][5:7], 'caigou': 0, 'ruku': 0, 'paishe': 0, 'zhizuo': 0, 'shangjia': 0, 'shangjia_done': 0, 'taotai': 0, 'fengcun': 0, 'fengcun_done': 0, 'tuishi_done': 0, 'caigou_exceed': 0, 'ruku_exceed': 0, 'paishe_exceed': 0, 'zhizuo_exceed': 0})
            return JsonResponse({'code':'0','data':json.dumps(sum_res_list),'month_week':'month'})

        # 以周为尺度
        if caigouWeek:
            #  0-6  一 - 周日
            thirteen_week_day = today_date + timedelta(days=-today_date.weekday()-1-7*13)
            # 获取近13周数据
            one_year_data = IndexHistory.objects.filter(date__gte = thirteen_week_day)
            # 分组统计每周的数据
            sum_res = one_year_data.annotate(
                    # day=functions.ExtractWeekDay('date'),
                    week=functions.ExtractWeek('date'),
                    ).values('week').order_by( '-week').annotate(
                            date = Max('date'),
                            caigou = Avg('caigou'),
                            ruku = Avg('ruku'),
                            paishe = Avg('paishe'),
                            zhizuo = Avg('zhizuo'),
                            shangjia = Avg('shangjia'),
                            shangjia_done = Avg('shangjia_done'),
                            taotai = Avg('taotai'),
                            fengcun = Avg('fengcun'),
                            fengcun_done = Avg('fengcun_done'),
                            tuishi_done = Avg('tuishi_done'),
                            caigou_exceed = Avg('caigou_exceed'),
                            ruku_exceed = Avg('ruku_exceed'),
                            paishe_exceed = Avg('paishe_exceed'),
                            zhizuo_exceed = Avg('zhizuo_exceed'),
                        )
            # print(sum_res)
            # print(len(sum_res))
            for su in sum_res:
                for key in su:
                    if isinstance(key,float):
                        su[key] = math.ceil(su[key])
            for res in sum_res:
                res['date'] = str(res['date'])[5:]
            # if len(sum_res) != 13:
            #     # 空数据填充前面月份的数据
            #     thirteen = get_13_month_list()
            #     sum_res_list =list(sum_res)
            #     for i in range(len(sum_res),13):
            #         sum_res_list.append({'year': thirteen[i][:4], 'month': thirteen[i][5:7], 'caigou': 0, 'ruku': 0, 'paishe': 0, 'zhizuo': 0, 'shangjia': 0, 'shangjia_done': 0, 'taotai': 0, 'fengcun': 0, 'fengcun_done': 0, 'tuishi_done': 0, 'caigou_exceed': 0, 'ruku_exceed': 0, 'paishe_exceed': 0, 'zhizuo_exceed': 0})
            return JsonResponse({'code':'0','data':json.dumps(list(sum_res)),'month_week':'week'})
            
        # 查询七天前的记录
        if caigouDay7:
            orders = IndexHistory.objects.order_by('-date')[0:7]
            return JsonResponse({'code':'0','data':serializers.serialize('json',orders)})
        # 查询昨天的记录
        if caigouYesterday:
            orders = IndexHistory.objects.order_by('-date')[0:1]
            return JsonResponse({'code':'0','data':serializers.serialize('json',orders)})
        # 查询30天前的记录
        if caigouDay30:
            orders = IndexHistory.objects.order_by('-date')[0:30]
            return JsonResponse({'code':'0','data':serializers.serialize('json',orders)})

        # 实时的记录
        if caigouShishi:
            conn = get_redis_connection()
            index_ = conn.hgetall('index') # b'' 真的烦
            index = {}
            for key in index_:
                index[str(key.decode())] = str(index_[key].decode())
            index['date'] = str(datetime.now().date())
            res_array = []
            res_array.append({'fields':index})
            return JsonResponse({'code':'0','data':json.dumps(res_array)})

    def post(self,request):
        '''获取  首页的统计信息 后台命令每隔一小时执行统计一次'''
        conn = get_redis_connection()
        index_data = conn.hgetall('index')
        if index_data:
            print('redis')
            new_data = {}
            for key in index_data:
                new_data[str(key.decode())] = str(index_data[key].decode())
            return JsonResponse(new_data)



@method_decorator(csrf_exempt, name='dispatch')
class CpmIndexCommonQueryView(LoginRequiredMixin,View):
    '''首页通用产品查询'''
    def get(self,request):
        # 查询条件
        suppiler_val = request.GET.get('suppilerVal','')
        code = request.GET.get('code','')
        name = request.GET.get('name','')
        pinlei = request.GET.get('pinlei','')
        jibie = request.GET.get('jibie','')
        chargers = request.GET.get('chargers','')
        suppliers = request.GET.get('suppliers','')
        page = int(request.GET.get('p',1))

        shangxin_type = request.GET.get('shangxin_type','')
        shangxin_start = request.GET.get('shangxin_start','')
        shangxin_end = request.GET.get('shangxin_end','')
        sale_type = request.GET.get('sale_type','')
        sale_start = request.GET.get('sale_start','')
        sale_end = request.GET.get('sale_end','')
        do_shop = request.GET.get('do_shop','')

        items = Good.objects.select_related().filter(state_caigou__gte=1).order_by('code')
        chargers_all = User.objects.filter(extension__role__name=0)
        # 处理查询条件
        if code:
            items = items.filter(code__icontains=code)
        if jibie:
            items = items.filter(jibie=jibie)
        if name:
            items = items.filter(name__icontains=name)
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

        # 通用查询 新增条件
        if shangxin_start or shangxin_end:
            print('enter  shangxin --------')

            if shangxin_start:
                start_date = datetime.strptime(shangxin_start,'%Y-%m-%d')
            else:
                start_date = datetime(year=2019,month=9,day=1)
            if shangxin_end:
                end_date = datetime.strptime(shangxin_end,'%Y-%m-%d')
            else:
                end_date = datetime.today()
            # 判断 shangxin_type 0创建时间 1采购下单时间 2实际到货时间 3入库完成 4拍摄交付 5 制作审核通过
            if shangxin_type == '0':
                items = items.filter(created_at__range=(start_date,end_date))
            elif shangxin_type == '1':
                items = items.filter(goods_buy_good__purchase_date__range=(start_date,end_date))
            elif shangxin_type == '2':
                item_fendian = items.filter(goods_dian_fen__real_arrival_date__range=(start_date,end_date))
                item_yanhuo = items.filter(goods_yanhuo_good__created_at__range=(start_date,end_date))
                items = list(set(list(item_fendian)+list(item_yanhuo)))
            elif shangxin_type == '3':
                items = items.filter(goods_ruku_good__created_at__range=(start_date,end_date))
            elif shangxin_type == '4':
                items = items.filter(goods_sysx_phase__real_date__range=(start_date,end_date))
            elif shangxin_type == '5':
                temp_item = []
                for item in items:
                    mgzz = item.goods_mgzz_phase.order_by('-created_at').first()
                    if mgzz:
                        details = GoodsMGZZCheckDetail.objects.filter(mgzz=mgzz,created_at__range=(start_date,end_date)).order_by('-created_at')
                        if len(details) > 0:
                            for detail in details:
                                if detail.check_state==0:
                                    temp_item.append(item)
                items = list(set(temp_item))
        if sale_start or sale_end:
            print('enter  sale --------')
            if sale_start:
                start_date = datetime.strptime(sale_start,'%Y-%m-%d')
            else:
                start_date = datetime(year=2019,month=9,day=1)
            if sale_end:
                end_date = datetime.strptime(sale_end,'%Y-%m-%d')
            else:
                end_date = datetime.today()
            # 判断 sale_type 0首个店铺设置为上架的时间 1封存 2淘汰 3退市
            if sale_type == '0':
                temp_item = []
                for item in items:
                    skus = item.goods_skus.all()
                    if len(skus) > 0:
                        for sku in skus:
                            sku_shops = sku.sku2shop_sku.filter(created_at__range=(start_date,end_date))
                            if len(sku_shops) >0:
                                for sku_2_shop in sku_shops:
                                    if sku_2_shop.sku_in_shop_state == 11:
                                        temp_item.append(item)
                items = list(set(temp_item))
            elif sale_type == '1':
                items = items.filter(goods_fengcun_sku__created_at__range=(start_date,end_date),state_sale=15).distinct()
            elif sale_type == '2':
                items = items.filter(goods_taotai_sku__created_at__range=(start_date,end_date)).distinct()
            elif sale_type == '3':
                items = items.filter(goods_tuishi_sku__created_at__range=(start_date,end_date)).distinct()

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

        # 分页 
        # if flag != '1':
        len_items = len(items)  # 总的记录数
        paginator = Paginator(items,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1
        page_obj = paginator.page(page)

        items = page_obj.object_list

        if not items:
            items = []
        print('enter for items')
        now = datetime.now().timestamp()
        for item in items:
            setattr(item,'suppliers',item.suppiler.all())
            setattr(item,'chargers',item.charger.all())
            '''
            setattr(item,'caigou',item.goods_buy_good.order_by('-created_at').first())
            setattr(item,'fendian',item.goods_dian_fen.order_by('-created_at').first())
            setattr(item,'yanhuo',item.goods_yanhuo_good.order_by('-created_at').first())
            setattr(item,'ruku',item.goods_ruku_good.order_by('-created_at').first())
            setattr(item,'paishe',item.goods_detail_good.order_by('-created_at').first())
            mgzz = item.goods_mgzz_phase.order_by('-created_at').first()
            setattr(item,'zhizuo',mgzz)
            setattr(item,'zhizuo_detail',GoodsMGZZCheckDetail.objects.filter(mgzz=mgzz).order_by('-created_at').first())
            setattr(item,'shangjia',item.goods_shangjia_sku.order_by('-created_at').first())
            setattr(item,'fengcun',item.goods_fengcun_sku.order_by('-created_at').first())
            setattr(item,'taotai',item.goods_taotai_sku.order_by('-created_at').first())
            setattr(item,'tuishi',item.goods_tuishi_sku.order_by('-created_at').first())
            # 上架店铺
            temp_list = []
            for sku in item.goods_skus.all():
                for sku_2_shop in sku.sku2shop_sku.all():
                    if sku_2_shop.sku_in_shop_state == 11:
                        temp_list.append(sku_2_shop.shop)
            setattr(item,'shops_shangjia',list(set(temp_list)))   # 去重
            '''

        after = datetime.now().timestamp()



        print(after-now)
        print('enter return')

        context = {
            'query':True,
            'chargers_all': chargers_all,
            'query_url':'/query/',
            'msg':'通用查询',
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'shops':Shop.objects.all(),
            'total_item': len_items,
            'index_sale': INDEX_SALE_ITEMS,
            'index_shangxin': INDEX_SHANGXIN_ITEMS,
            'last_pages':len_items/PAGE_SIZE +1,
            # 查询参数
            'url_query': '&'+parse.urlencode({   
                'code': code or '',
                'name': name or '',
                'pinlei': pinlei or '',
                'chargers': chargers or '',
                'suppliers': suppliers or '',
                'jibie': jibie or '',
                'shangxin_type': shangxin_type or '',
                'shangxin_start': shangxin_start or '',
                'shangxin_end': shangxin_end or '',
                'sale_type': sale_type or '',
                'sale_start': sale_start or '',
                'sale_end': sale_end or '',
                'do_shop': do_shop or '',
            })
        }
        # 查询参数返回
        if chargers:
            chargers = int(chargers)
        if shangxin_type:
            shangxin_type = int(shangxin_type)
        if sale_type:
            sale_type = int(sale_type)
        if do_shop:
            do_shop = int(do_shop)
        url_query_data = {
            'suppiler_val':suppiler_val,
            'chargers':chargers,
            'suppliers':suppliers,
            'code':code,
            'jibie':jibie,
            'do_shop':do_shop,
            'name':name,
            'pinlei':pinlei,
            'shangxin_type':shangxin_type,
            'shangxin_start':shangxin_start,
            'shangxin_end':shangxin_end,
            'sale_type':sale_type,
            'sale_start':sale_start,
            'sale_end':sale_end,
            'base_domain':QINIU_BASE_DOMAIN,
        }
        page_data = get_pagination_data(paginator,page_obj)
        context.update(page_data)
        context.update(url_query_data)
        return render(request,'index/common_query.html',context=context)






    def post(self,request):
        '''根据传过来的good_ids 返回对应的内容'''
        good_ids = request.POST.get('good_ids').split(',')
        kind = request.POST.get('kind')
        if kind == 'skus':
            goods = []
            for good_id in good_ids:
                try:
                    temp_dict = {}
                    good = Good.objects.get(pk=int(good_id))
                    skus = good.goods_skus.all()
                    temp_dict['good_id'] = good_id
                    temp_dict['good_code'] = good.code
                    temp_sku_arr = []
                    for sku in skus:
                        temp_sku_dict = {}
                        temp_sku_dict['sku_id'] = sku.id
                        temp_sku_dict['sku_code'] = sku.sku_code
                        temp_sku_dict['sku_name'] = sku.sku_name
                        temp_sku_dict['sku_v'] = float(sku.height) * float(sku.width) * float(sku.length) / 1000000
                        temp_sku_dict['sku_weight'] = sku.weight
                        # 区分一下是否是批量导入的图片
                        temp_sku_dict['sku_image'] = QINIU_BASE_DOMAIN + sku.sku_image
                        if sku.sku_image.startswith('http'):
                            temp_sku_dict['sku_image'] = sku.sku_image
                        temp_sku_arr.append(temp_sku_dict)
                    temp_dict['skus'] = temp_sku_arr
                    goods.append(temp_dict)
                except Exception as err:
                    print(err)
                    pass
            return JsonResponse({'code':'0','msg':'ok','res':goods})
        elif kind == 'cates':
            cate_arr = []
            for good_id in good_ids:
                temp_dict = {}
                good = Good.objects.get(pk=int(good_id))
                temp_dict['good_id'] = good_id
                temp_dict['cate_name'] = good.cate.name
                cate_arr.append(temp_dict)
            return JsonResponse({'code':'0','msg':'ok','res':cate_arr})
        elif kind == 'make':
            sale_arr = []
            now = datetime.now().timestamp()
            for good_id in good_ids:
                temp_dict = {}
                try:
                    good = Good.objects.get(pk=int(good_id))
                    temp_dict['good_id'] = good_id
                    temp_dict['good_state_sale'] = good.state_sale
                    # 采购  goods_buy_good
                    caigou = good.goods_buy_good.order_by('-created_at').first()
                    caigou_dict = {}
                    if caigou:
                        caigou_dict['date'] = caigou.created_at.strftime('%Y年%m月%d日 %H:%M')
                    temp_dict['caigou'] = caigou_dict
                    # 到货日期  分货点货的情况
                    fendian_yanhuo_dict = {}
                    fendian = good.goods_dian_fen.order_by('-created_at').first()
                    yanhuo = good.goods_yanhuo_good.order_by('-created_at').first()
                    if fendian:
                        fendian_yanhuo_dict['date'] = fendian.real_arrival_date.strftime('%Y年%m月%d日 %H:%M')
                    if not fendian  and yanhuo:
                        fendian_yanhuo_dict['date'] = yanhuo.created_at.strftime('%Y年%m月%d日 %H:%M')
                    temp_dict['fendian'] = fendian_yanhuo_dict
                    # 入库
                    ruku = good.goods_ruku_good.order_by('-created_at').first()
                    ruku_dict = {}
                    if ruku:
                        ruku_dict['date'] = ruku.created_at.strftime('%Y年%m月%d日 %H:%M')
                        ruku_dict['state'] = ruku.get_result_display()
                    temp_dict['ruku'] = ruku_dict
                    # 拍摄  取交付的时间 
                    paishe = good.goods_sysx_phase.order_by('-created_at').first()
                    paishe_dict = {}
                    if paishe:
                        paishe_dict['date'] = paishe.created_at.strftime('%Y年%m月%d日 %H:%M')
                    temp_dict['paishe'] = paishe_dict
                    # 制作  取制作完成的时间 
                    zhizuo = good.goods_mgzz_phase.order_by('-created_at').first()
                    zhizuo_dict = {}
                    if zhizuo:
                        zhizuo_detail = GoodsMGZZCheckDetail.objects.filter(mgzz=zhizuo).order_by('-created_at').first()

                        if zhizuo_detail:
                            if zhizuo_detail.check_state == 0:
                                zhizuo_dict['date'] = zhizuo_detail.created_at.strftime('%Y年%m月%d日 %H:%M')
                        zhizuo_dict['state'] = zhizuo.get_mk_state_display()
                    temp_dict['zhizuo'] = zhizuo_dict
                   
                    sale_arr.append(temp_dict)
                except Exception as err:
                    print(err)
            end = datetime.now().timestamp()
            print(str(end-now) + 'make--------')
            # print(sale_arr)
            return JsonResponse({'code':'0','msg':'ok','res':sale_arr})
            
        elif kind == 'sale':
            sale_arr = []
            now = datetime.now().timestamp()
            for good_id in good_ids:
                temp_dict = {}
                try:
                    good = Good.objects.get(pk=int(good_id))
                    temp_dict['good_id'] = good_id
                    temp_dict['good_state_sale'] = good.state_sale
                    # 上架
                    shangjia = good.goods_shangjia_sku.order_by('-created_at').first()
                    shangjia_dict = {}
                    if shangjia:
                        shangjia_dict['date'] = shangjia.created_at.strftime('%Y年%m月%d日 %H:%M')
                    temp_dict['shangjia'] = shangjia_dict
                    # 封存
                    fengcun = good.goods_fengcun_sku.order_by('-created_at').first()
                    fengcun_dict = {}
                    if fengcun:
                        fengcun_dict['date'] = fengcun.created_at.strftime('%Y年%m月%d日 %H:%M')
                    temp_dict['fengcun'] = fengcun_dict
                    # 淘汰
                    taotai = good.goods_taotai_sku.order_by('-created_at').first()
                    taotai_dict = {}
                    if taotai:
                        taotai_dict['date'] = taotai.created_at.strftime('%Y年%m月%d日 %H:%M')
                    temp_dict['taotai'] = taotai_dict
                    # 退市
                    tuishi = good.goods_tuishi_sku.order_by('-created_at').first()
                    tuishi_dict = {}
                    if tuishi:
                        tuishi_dict['date'] = tuishi.created_at.strftime('%Y年%m月%d日 %H:%M')
                    temp_dict['tuishi'] = tuishi_dict

                    sale_arr.append(temp_dict)
                except Exception as err:
                    print(err)
            end = datetime.now().timestamp()
            print(str(end-now) + 'sale-------')
            # print(sale_arr)
            return JsonResponse({'code':'0','msg':'ok','res':sale_arr})
            
            
        elif kind == 'dianpu':
            sale_arr = []
            now = datetime.now().timestamp()
            for good_id in good_ids:
                temp_dict = {}
                try:
                    good = Good.objects.get(pk=int(good_id))
                    temp_dict['good_id'] = good_id
                    temp_dict['good_state_sale'] = good.state_sale
                    # 上架店铺
                    temp_list_shop = []
                    for sku in good.goods_skus.all():
                        for sku_2_shop in sku.sku2shop_sku.all():
                            if sku_2_shop.sku_in_shop_state == 11:
                                temp_list_shop.append(sku_2_shop.shop)
                    temp_list_shop = list(set(temp_list_shop))
                    temp_list_shop_res = []
                    for shop in temp_list_shop:
                        shop_dict = {}
                        shop_dict['name'] = shop.name
                        shop_dict['sub_name'] = shop.sub_name
                        temp_list_shop_res.append(shop_dict)

                    temp_dict['shops'] = temp_list_shop_res

                    sale_arr.append(temp_dict)
                except Exception as err:
                    print(err)
            end = datetime.now().timestamp()
            print(end-now)
            # print(sale_arr)
            return JsonResponse({'code':'0','msg':'ok','res':sale_arr})
            
