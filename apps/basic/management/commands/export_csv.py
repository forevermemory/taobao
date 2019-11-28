from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from datetime import datetime,timedelta
from django_redis import get_redis_connection
from django.db.models import Q,F

import json
from cpm.models import Good,GoodsSku,Supplier,TagChangjing,TagDingwei,Category,GoodsBrand,GoodsMGZZCheckDetail,GoodsPingshenPhase,GoodsPurchasePhase,GoodsDianAndFenPhase,GoodsYanhuoPhase
import pandas as pd
import pickle
from utils.export_csv import create_csv_file
from cpm.settings import BASE_DIR,QINIU_BASE_DOMAIN

class Command(BaseCommand):
    '''导出csv'''
    success_msg = '执行生成csv任务创建成功,当前时间为%s' % datetime.date(datetime.now())
    commond = '/home/deploy/.local/share/virtualenvs/cpm-NXD7Laz8/bin/python3.8 /home/deploy/apps/cpm/manage.py export_csv >>/home/deploy/apps/log/export_csv.log 2>&1'

    def handle(self, *args, **options):
        conn = get_redis_connection()
        now = datetime.now().timestamp()
        now_str = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        csv_path = pickle.loads(conn.get('csv_path'))
        request_get = pickle.loads(conn.get('request_get'))
        conn.delete('csv_path')
        conn.delete('request_get')
        try:
            if not csv_path:
                raise
            # 根据csv_path 分类解析
            absolute_path = ''
            # 来一个导出任务就往list中存入一个记录 下载过了就把它删除即可
            csv_path_now = csv_path +'**'+ str(now)
            csv_lists_length = conn.lpush('csv_lists',csv_path_now) 
            conn.hset('export_csv_result',csv_path_now + '__index',csv_lists_length - 1)
            conn.hset('export_csv_result',csv_path_now + '__now_str',now_str)

            # 0 正在计算中  1 已经完成 
            conn.hset('export_csv_result',csv_path_now,'0')
            
            if csv_path == '/query/':
                absolute_path = self.parse_index_common_query(csv_path,request_get)

            elif csv_path == '/sale/shangjia/':
                absolute_path = self.parse_sale_shangjia(csv_path,request_get)    
            elif csv_path == '/sale/fengcun/':
                absolute_path = self.parse_sale_fengcun(csv_path,request_get) 
            elif csv_path == '/sale/taotai/':
                absolute_path = self.parse_sale_taotai(csv_path,request_get)

            elif csv_path == '/photo/start/':
                absolute_path = self.parse_photo_start(csv_path,request_get)
            elif csv_path == '/photo/sysx/':
                absolute_path = self.parse_photo_sysx(csv_path,request_get)
            elif csv_path == '/photo/mgzz/':
                absolute_path = self.parse_photo_mgzz(csv_path,request_get)

            elif csv_path == '/purchase/purchase/':
                absolute_path = self.parse_purchase_purchase(csv_path,request_get)
            elif csv_path == '/purchase/fen_dian/':
                absolute_path = self.parse_purchase_fen_dian(csv_path,request_get)
            elif csv_path == '/purchase/yanhuo/':
                absolute_path = self.parse_purchase_yanhuo(csv_path,request_get)
            elif csv_path == '/purchase/ruku/':
                absolute_path = self.parse_purchase_ruku(csv_path,request_get)

            elif csv_path == '/select/p_list/':
                absolute_path = self.parse_select_p_list(csv_path,request_get)
            elif csv_path == '/select/pingshen/':
                absolute_path = self.parse_select_pingshen(csv_path,request_get)
            elif csv_path == '/select/add_sku/':
                absolute_path = self.parse_select_add_sku(csv_path,request_get)



            after = datetime.now().timestamp()
            pass_time = int(after-now)
            print('执行生成csv任务创建成功,共花费%d' % pass_time)
            print('执行生成csv任务创建成功,当前导出的path：%s' % csv_path)
            print('执行生成csv任务创建成功,时间为：%s' % datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))
            conn.hset('export_csv_result',csv_path_now,'1')
            conn.hset('export_csv_result',csv_path_now + '__path',absolute_path)
        except Exception as err:
            conn.hset('export_csv_result',csv_path_now,'2')
            print(err)



    def parse_index_common_query(self,csv_path,request_get):
        '''首页通用查询的csv导出'''
        # 查询条件
        suppiler_val = request_get.get('suppilerVal','')
        code = request_get.get('code')
        name = request_get.get('name')
        pinlei = request_get.get('pinlei')
        jibie = request_get.get('jibie')
        chargers = request_get.get('chargers')
        suppliers = request_get.get('suppliers')

        shangxin_type = request_get.get('shangxin_type')
        shangxin_start = request_get.get('shangxin_start')
        shangxin_end = request_get.get('shangxin_end')
        sale_type = request_get.get('sale_type')
        sale_start = request_get.get('sale_start')
        sale_end = request_get.get('sale_end')

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

        if not items:
            items = []
        now = datetime.now().timestamp()
        for item in items:
            setattr(item,'suppliers',item.suppiler.all())
            setattr(item,'chargers',item.charger.all())
        after = datetime.now().timestamp()

        file_name = '查询'
        rows = self.export_csv_common_query(items)
        # 生成csv
        absolute_path = create_csv_file(file_name,rows)
        return absolute_path

    def export_csv_common_query(self,items):
        '''通用查询导出util'''
        rows = []
        rows.append(['产品编码','sku编码','缩略图', '产品名称', '品类', '产品负责人','级别','供应商','创建日期','采购日期','到货日期','入库日期','拍摄日期','制作日期','入库状态','制作状态','销售状态','已上架店铺','上架日期','封存日期','淘汰日期','退市日期'])

        for item in items:
            caigou_date = ''
            arrive_date = ''
            ruku_date = ''
            paishe_date = ''
            make_date = ''
            ruku_state= ''
            make_state = ''
            sale_state = ''
            shops = ''
            shangjia_date = ''
            fengcun_date = ''
            taotai_date = ''
            tuishi_date = ''

            caigou_ = item.goods_buy_good.order_by('-created_at').first()
            if caigou_:
                caigou_date = caigou_.created_at.strftime('%Y年%m月%d日 %H:%M')

            fendian_ = item.goods_dian_fen.order_by('-created_at').first()
            yanhuo_ = item.goods_yanhuo_good.order_by('-created_at').first()
            if fendian_:
                arrive_date = fendian_.real_arrival_date.strftime('%Y年%m月%d日 %H:%M')
            if not fendian_ and yanhuo_:
                arrive_date= yanhuo_.created_at.strftime('%Y年%m月%d日 %H:%M')

            ruku_ = item.goods_ruku_good.order_by('-created_at').first()
            if ruku_:
                ruku_date = ruku_.created_at.strftime('%Y年%m月%d日 %H:%M'),
                ruku_state = ruku_.get_result_display(),

            paishe_ = item.goods_detail_good.order_by('-created_at').first()
            if paishe_:
                paishe_date = paishe_.created_at.strftime('%Y年%m月%d日 %H:%M')
            
            zhizuo_ = item.goods_mgzz_phase.order_by('-created_at').first()

            if zhizuo_:
                zhizuo_detail = GoodsMGZZCheckDetail.objects.filter(mgzz=zhizuo_).order_by('-created_at').first()

                if zhizuo_detail:
                    if zhizuo_detail.check_state == 0:
                        make_date = zhizuo_detail.created_at.strftime('%Y年%m月%d日 %H:%M')
                make_state = zhizuo_.get_mk_state_display()


                shangjia_ = item.goods_shangjia_sku.order_by('-created_at').first()
                if shangjia_:
                    shangjia_date = shangjia_.created_at.strftime('%Y年%m月%d日 %H:%M')
                fengcun_ = item.goods_fengcun_sku.order_by('-created_at').first()
                if fengcun_:
                    fengcun_date = fengcun_.created_at.strftime('%Y年%m月%d日 %H:%M')
                taotai_ = item.goods_taotai_sku.order_by('-created_at').first()
                if taotai_:
                    taotai_date = taotai_.created_at.strftime('%Y年%m月%d日 %H:%M')
                tuishi_ = item.goods_tuishi_sku.order_by('-created_at').first()
                if tuishi_:
                    tuishi_date = tuishi_.created_at.strftime('%Y年%m月%d日 %H:%M')


                temp_list = []
                for sku in item.goods_skus.all():
                    for sku_2_shop in sku.sku2shop_sku.all():
                        if sku_2_shop.sku_in_shop_state == 11:
                            temp_list.append(sku_2_shop.shop)
                shops_shangjia = list(set(temp_list))
                shops = ''.join([i.name+' ' for i in shops_shangjia])

            if item.state_sale > 10:
                sale_state = item.get_state_sale_display()
            data = [
                item.code,
                '',
                '',
                item.name,
                item.cate.name,
                ''.join(list(i.extension.name+' ' for i in item.charger.all())).strip(),
                item.get_jibie_display(),
                ''.join([i.name+' ' for i in  item.suppiler.all() ]).strip(),
                item.created_at.strftime('%Y年%m月%d日 %H:%M'),
                caigou_date,
                arrive_date,
                ''.join(ruku_date).strip(),
                paishe_date,
                make_date,
                ''.join(ruku_state).strip(),
                make_state,
                sale_state,
                shops.strip(),
                shangjia_date,
                fengcun_date,
                taotai_date,
                tuishi_date,
            ]
            rows.append(data) 
            skus = item.goods_skus.all()
            if skus:
                for sku in skus:
                    sku_images = sku.sku_image
                    if sku_images and not sku_images.startswith('http:'):
                        sku_images = QINIU_BASE_DOMAIN + sku_images
                    data2 = [
                        '',
                        str(item.code)+'-'+sku.sku_code,
                        sku_images,
                        sku.sku_name,
                        '','','','','','','','','','','','','','','','','',''
                    ]
                    rows.append(data2) 
        return rows

    def parse_sale_shangjia(self,csv_path,request_get):
        '''销售-上架-导出csv'''
        code = request_get.get('code')
        name = request_get.get('name')
        pinlei = request_get.get('pinlei')
        jibie = request_get.get('jibie')
        chargers = request_get.get('chargers')
        suppliers = request_get.get('suppliers')
        suppiler_val = request_get.get('suppiler_val')
        # 新的查询条件
        ruku_start = request_get.get('ruku_start')
        ruku_end = request_get.get('ruku_end')
        ruku_state = request_get.get('ruku_state')
        zhizuo_start = request_get.get('zhizuo_start')
        zhizuo_end = request_get.get('zhizuo_end')
        zhizuo_state = request_get.get('zhizuo_state')

        un_shop = request_get.get('un_shop')
        do_shop = request_get.get('do_shop')
        never_shangjia = request_get.get('never_shangjia')

        # 上过架的产品
        shangjia_done = request_get.get('shangjia_done')
        to_shangjia = request_get.get('to_shangjia')

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

        if chargers:
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
                print(count_sku)
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
                print(count_sku)
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
            
            temp_list = []
            for sku in item.goods_skus.all():
                for sku_2_shop in sku.sku2shop_sku.all():
                    if sku_2_shop.sku_in_shop_state == 11:
                        temp_list.append(sku_2_shop.shop)
            setattr(item,'shops_shangjia',list(set(temp_list)))   # 去重



        # 导出csv
        file_name = '销售-上架'
        rows = []
        rows.append(['产品编码','sku编码','缩略图', '产品名称', '品类', '产品负责人','级别','供应商','创建日期','采购日期','入库日期','入库状态','制作状态','已上架店铺'])
        for item in items:
            caigou_date = ''
            ruku_date = ''
            ruku_state = ''
            make_state = ''
            shops = ''
            if item.caigou:
                caigou_date = item.caigou.created_at.strftime('%Y年%m月%d日 %H:%M')
            if item.ruku:
                ruku_date = item.ruku.created_at.strftime('%Y年%m月%d日 %H:%M'),
                ruku_state = item.ruku.get_result_display(),
            if item.goods_mgzz_phase.order_by('-created_at').first():
                make_state = item.mgzz_ckeck.get_mk_state_display()
            if item.shops_shangjia:
                shops = ''.join([i.name+' ' for i in item.shops_shangjia])
            

            data = [
                item.code,
                '',
                '',
                item.name,
                item.cate.name,
                ''.join(list(i.extension.name+' ' for i in item.charger.all())).strip(),
                item.get_jibie_display(),
                ''.join([i.name+' ' for i in  item.suppiler.all() ]).strip(),
                item.created_at.strftime('%Y年%m月%d日 %H:%M'),
                caigou_date,
                ''.join(ruku_date).strip(),
                ''.join(ruku_state).strip(),
                make_state,
                shops.strip(),
            ]
            rows.append(data) 
            skus = item.goods_skus.all()
            if skus:
                for sku in skus:
                    sku_images = sku.sku_image
                    if sku_images and not sku_images.startswith('http:'):
                        sku_images = QINIU_BASE_DOMAIN + sku_images
                        
                    data2 = [
                        '',
                        str(item.code)+'-'+sku.sku_code,
                        sku_images,
                        sku.sku_name,
                        '','','','','','','','','','',
                    ]
                    rows.append(data2) 
        absolute_path = create_csv_file(file_name,rows)
        return absolute_path

    def parse_sale_fengcun(self,csv_path,request_get):
        '''销售-封存-导出csv'''
        code = request_get.get('code')
        name = request_get.get('name')
        pinlei = request_get.get('pinlei')
        jibie = request_get.get('jibie')
        chargers = request_get.get('chargers')
        suppliers = request_get.get('suppliers')
        suppiler_val = request_get.get('suppiler_val')
        fengcun_state = request_get.get('fengcun_state')
        # 新的查询条件
        # 是否封存
        fengcun_done = request_get.get('fengcun_done')

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
        if not items:
            items = []
        for item in items:
            setattr(item,'suppliers',item.suppiler.all())
            setattr(item,'chargers',item.charger.all())
            setattr(item,'caigou',item.goods_buy_good.order_by('-created_at').first())
            setattr(item,'ruku',item.goods_ruku_good.order_by('-created_at').first())

            temp_list = []
            for sku in item.goods_skus.all():
                for sku_2_shop in sku.sku2shop_sku.all():
                    if sku_2_shop.sku_in_shop_state == 11:
                        temp_list.append(sku_2_shop.shop)
            setattr(item,'shops_shangjia',list(set(temp_list)))   # 去重

        # 导出csv
        file_name = '销售-封存启封'
        rows = []
        rows.append(['产品编码','sku编码','缩略图', '产品名称', '品类', '产品负责人','级别','供应商','创建日期','采购日期','入库日期','已上架店铺','产品状态'])
        for item in items:
            caigou_date = ''
            ruku_date = ''
            shops = ''
            if item.caigou:
                caigou_date = item.caigou.created_at.strftime('%Y年%m月%d日 %H:%M')
            if item.ruku:
                ruku_date = item.ruku.created_at.strftime('%Y年%m月%d日 %H:%M'),
                ruku_state = item.ruku.get_result_display(),
            if item.shops_shangjia:
                shops = ''.join([i.name+' ' for i in item.shops_shangjia])

            data = [
                item.code,
                '',
                '',
                item.name,
                item.cate.name,
                ''.join(list(i.extension.name+' ' for i in item.charger.all())).strip(),
                item.get_jibie_display(),
                ''.join([i.name+' ' for i in  item.suppiler.all() ]).strip(),
                item.created_at.strftime('%Y年%m月%d日 %H:%M'),
                caigou_date,
                ''.join(ruku_date),
                shops.strip(),
                item.get_state_sale_display()
            ]
            rows.append(data) 
            skus = item.goods_skus.all()
            if skus:
                for sku in skus:
                    sku_images = sku.sku_image
                    if sku_images and not sku_images.startswith('http:'):
                        sku_images = QINIU_BASE_DOMAIN + sku_images
                        
                    data2 = [
                        '',
                        str(item.code)+'-'+sku.sku_code,
                        sku_images,
                        sku.sku_name,
                        '','','','','','','','','',
                    ]
                    rows.append(data2) 
        absolute_path = create_csv_file(file_name,rows)
        return absolute_path


    def parse_sale_taotai(self,csv_path,request_get):
        '''销售-淘汰-导出csv'''

        code = request_get.get('code')
        name = request_get.get('name')
        pinlei = request_get.get('pinlei')
        jibie = request_get.get('jibie')
        chargers = request_get.get('chargers')
        suppliers = request_get.get('suppliers')
        suppiler_val = request_get.get('suppiler_val')
        taotai_state = request_get.get('taotai_state')
        # 新的查询条件

        tuishi_done = request_get.get('tuishi_done')

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

        if not items:
            items = []
        for item in items:
            setattr(item,'suppliers',item.suppiler.all())
            setattr(item,'chargers',item.charger.all())
            setattr(item,'caigou',item.goods_buy_good.order_by('-created_at').first())
            setattr(item,'ruku',item.goods_ruku_good.order_by('-created_at').first())

            temp_list = []
            for sku in item.goods_skus.all():
                for sku_2_shop in sku.sku2shop_sku.all():
                    if sku_2_shop.sku_in_shop_state == 11:
                        temp_list.append(sku_2_shop.shop)
            setattr(item,'shops_shangjia',list(set(temp_list)))   # 去重


        # 导出csv
        file_name = '销售-淘汰退市'
        rows = []
        rows.append(['产品编码','sku编码','缩略图', '产品名称', '品类', '产品负责人','级别','供应商','创建日期','采购日期','入库日期','已上架店铺','产品状态'])
        for item in items:
            caigou_date = ''
            ruku_date = ''
            shops = ''
            if item.caigou:
                caigou_date = item.caigou.created_at.strftime('%Y年%m月%d日 %H:%M')
            if item.ruku:
                ruku_date = item.ruku.created_at.strftime('%Y年%m月%d日 %H:%M'),
                ruku_state = item.ruku.get_result_display(),
            if item.shops_shangjia:
                shops = ''.join([i.name+' ' for i in item.shops_shangjia])

            data = [
                item.code,
                '',
                '',
                item.name,
                item.cate.name,
                ''.join(list(i.extension.name+' ' for i in item.charger.all())).strip(),
                item.get_jibie_display(),
                ''.join([i.name+' ' for i in  item.suppiler.all() ]).strip(),
                item.created_at.strftime('%Y年%m月%d日 %H:%M'),
                caigou_date,
                ''.join(ruku_date),
                shops.strip(),
                item.get_state_sale_display()
            ]
            rows.append(data) 
            skus = item.goods_skus.all()
            if skus:
                for sku in skus:
                    sku_images = sku.sku_image
                    if sku_images and not sku_images.startswith('http:'):
                        sku_images = QINIU_BASE_DOMAIN + sku_images
                        
                    data2 = [
                        '',
                        str(item.code)+'-'+sku.sku_code,
                        sku_images,
                        sku.sku_name,
                        '','','','','','','','','',
                    ]
                    rows.append(data2) 
        absolute_path = create_csv_file(file_name,rows)
        return absolute_path



    def parse_photo_start(self,csv_path,request_get):
        '''拍摄准备-导出csv'''
        suppiler_val = request_get.get('suppilerVal')

        code = request_get.get('code')
        name = request_get.get('name')
        pinlei = request_get.get('pinlei')
        chargers = request_get.get('chargers')
        suppliers = request_get.get('suppliers')
        jibie = request_get.get('jibie')
        start = request_get.get('start')
        end = request_get.get('end')

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


        file_name = '拍摄准备'
        rows = []
        rows.append(['产品编码','缩略图', '产品名称', '品类', '产品负责人','级别','供应商','创建日期','通过评审日期'])
        for item in items:
            data = [
                item.code,
                QINIU_BASE_DOMAIN + item.goods_skus.first().sku_image,
                item.name,
                item.cate.name,
                ''.join(list(i.extension.name+' ' for i in item.charger.all())).strip(),
                item.get_jibie_display(),
                ''.join([i.name+' ' for i in  item.suppiler.all() ]).strip(),
                item.created_at.strftime('%Y年%m月%d日 %H:%M'),
                item.pingshen_date.created_at.strftime('%Y年%m月%d日 %H:%M'),
            ]
            rows.append(data) 
        absolute_path = create_csv_file(file_name,rows)
        return absolute_path

    def parse_photo_sysx(self,csv_path,request_get):
        '''摄影摄像-导出csv'''
        suppiler_val = request_get.get('suppilerVal')

        code = request_get.get('code')
        name = request_get.get('name')
        pinlei = request_get.get('pinlei')
        genzonger = request_get.get('genzonger')
        suppliers = request_get.get('suppliers')
        jibie = request_get.get('jibie')
        start = request_get.get('start')
        end = request_get.get('end')

        # 首页进入  拍摄超期
        paishe_exceed = request_get.get('paishe_exceed')

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
        file_name = '摄影摄像'
        rows = []
        rows.append(['产品编码','缩略图', '产品名称', '品类', '产品负责人','级别','供应商','拍摄跟踪人','拍摄方式','预计拍摄完成日期'])
        for item in items:
            data = [
                item.code,
                QINIU_BASE_DOMAIN + item.goods_skus.first().sku_image,
                item.name,
                item.cate.name,
                ''.join(list(i.extension.name+' ' for i in item.charger.all())).strip(),
                item.get_jibie_display(),
                ''.join([i.name+' ' for i in  item.suppiler.all() ]).strip(),
                item.photo.photo_genzonger.extension.name,
                item.photo.get_good_photo_method_display(),
                item.photo.kuaidi_edate.strftime('%Y年%m月%d日 %H:%M'),
            ]
            rows.append(data) 
        absolute_path = create_csv_file(file_name,rows)
        return absolute_path


    def parse_photo_mgzz(self,csv_path,request_get):
        '''美工制作-导出csv'''
        suppiler_val = request_get.get('suppilerVal','')

        code = request_get.get('code')
        name = request_get.get('name')
        pinlei = request_get.get('pinlei')
        chargers = request_get.get('chargers')
        suppliers = request_get.get('suppliers')
        suppiler_val = request_get.get('suppiler_val')
        jibie = request_get.get('jibie')
  
        start_fp = request_get.get('start_fp')
        end_fp = request_get.get('end_fp')
        start_tj = request_get.get('start_tj')
        end_tj = request_get.get('end_tj')
        meigong = request_get.get('meigong')
        mk_state = request_get.get('mk_state')
     
        # 首页进入 制作超期
        zhizuo_exceed = request_get.get('zhizuo_exceed')

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
        file_name = '美工制作'
        rows = []
        rows.append(['产品编码','缩略图', '产品名称', '品类', '产品负责人','级别','供应商','通过评审日期','创建日期','分配日期','美工','提交日期','制作状态'])
        for item in items:
            mg_fp_date = ''
            mg_name = ''
            mg_submit_date = ''
            mg_mk_stat = '未分配'
            if item.mgzz:
                mg_fp_date = item.mgzz.mk_date.strftime('%Y年%m月%d日 %H:%M')
                mg_name = item.mgzz.mk_to.extension.name
                mg_submit_date = item.mgzz.submit_date
                if item.mgzz.mk_state:
                    mg_mk_stat = item.mgzz.get_mk_state_display()

            data = [
                item.code,
                QINIU_BASE_DOMAIN + item.goods_skus.first().sku_image,
                item.name,
                item.cate.name,
                ''.join(list(i.extension.name+' ' for i in item.charger.all())).strip(),
                item.get_jibie_display(),
                ''.join([i.name+' ' for i in  item.suppiler.all() ]).strip(),
                item.pingshen.created_at.strftime('%Y年%m月%d日 %H:%M'),
                item.created_at.strftime('%Y年%m月%d日 %H:%M'),
                mg_fp_date,
                mg_name,
                mg_submit_date,
                mg_mk_stat,
            ]
            rows.append(data) 
        absolute_path = create_csv_file(file_name,rows)
        return absolute_path



    def parse_purchase_purchase(self,csv_path,request_get):
        '''采购 新品采购-导出csv'''
        suppiler_val = request_get.get('suppilerVal')

        code = request_get.get('code')
        name = request_get.get('name')
        pinlei = request_get.get('pinlei')
        chargers = request_get.get('chargers')
        suppliers = request_get.get('suppliers')
        jibie = request_get.get('jibie')
        start = request_get.get('start')
        end = request_get.get('end')

        items = Good.objects.select_related().filter(state_caigou__exact=3).order_by('code')
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
        file_name = '新品采购'
        rows = []
        rows.append(['产品编码','缩略图', '产品名称', '品类', '产品负责人','级别','供应商','通过评审日期','创建日期'])
        for item in items:
            data = [
                item.code,
                QINIU_BASE_DOMAIN + item.goods_skus.first().sku_image,
                item.name,
                item.cate.name,
                ''.join(list(i.extension.name+' ' for i in item.charger.all())).strip(),
                item.get_jibie_display(),
                ''.join([i.name+' ' for i in  item.suppiler.all() ]).strip(),
                item.pingshen_date.created_at.strftime('%Y年%m月%d日 %H:%M'),
                item.created_at.strftime('%Y年%m月%d日 %H:%M'),
            ]
            rows.append(data) 
        absolute_path = create_csv_file(file_name,rows)
        return absolute_path

    def parse_purchase_fen_dian(self,csv_path,request_get):
        '''采购 分货点货-导出csv'''
        suppiler_val = request_get.get('suppilerVal')


        code = request_get.get('code')
        name = request_get.get('name')
        pinlei = request_get.get('pinlei')
        chargers = request_get.get('chargers')
        suppliers = request_get.get('suppliers')
        jibie = request_get.get('jibie')
        start = request_get.get('start')
        end = request_get.get('end')
        state = request_get.get('state')

        # 首页点进来查看超期的产品
        caigou_exceed = request_get.get('caigou_exceed')

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
        file_name = '分货点货'
        rows = []
        rows.append(['产品编码','缩略图', '产品名称', '品类', '产品负责人','级别','供应商','创建日期','采购日期','预计到货日期','到货状态'])
        for item in items:
            data = [
                item.code,
                QINIU_BASE_DOMAIN + item.goods_skus.first().sku_image,
                item.name,
                item.cate.name,
                ''.join(list(i.extension.name+' ' for i in item.charger.all())).strip(),
                item.get_jibie_display(),
                ''.join([i.name+' ' for i in  item.suppiler.all() ]).strip(),
                item.created_at.strftime('%Y年%m月%d日 %H:%M'),
                item.order.purchase_date.strftime('%Y年%m月%d日 %H:%M'),
                item.order.expected_data.strftime('%Y年%m月%d日 %H:%M'),
                item.good_e_state,
            ]
            rows.append(data) 
        absolute_path = create_csv_file(file_name,rows)
        return absolute_path

    def compute_good_state(self,expected_data):
        '''计算分货点货阶段超期情况'''

        timeStamp1 = expected_data.timestamp()
        now_timestamp = datetime.now().timestamp()

        interval = timeStamp1 - now_timestamp 

        if interval > 0:
            return '正常'
        elif interval > -3600*24*3:
            return '超期'
        else:
            return '严重超期'

    def parse_purchase_yanhuo(self,csv_path,request_get):
        '''采购 验货-导出csv'''
        suppiler_val = request_get.get('suppilerVal')

        code = request_get.get('code')
        name = request_get.get('name')
        pinlei = request_get.get('pinlei')
        chargers = request_get.get('chargers')
        suppliers = request_get.get('suppliers')
        jibie = request_get.get('jibie')
        start = request_get.get('start')
        end = request_get.get('end')
        state = request_get.get('state')

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
        file_name = '验货'
        rows = []
        rows.append(['产品编码','缩略图', '产品名称', '品类', '产品负责人','级别','供应商','创建日期','采购日期','预计到货日期','点货结果','点货备注'])
        for item in items:
            dianhuo_desc = ''
            dianhuo_result = ''
            if item.goods_dianfen:
                dianhuo_result = item.goods_dianfen.get_state_display()
                dianhuo_desc = item.goods_dianfen.desc
            data = [
                item.code,
                QINIU_BASE_DOMAIN + item.goods_skus.first().sku_image,
                item.name,
                item.cate.name,
                ''.join(list(i.extension.name+' ' for i in item.charger.all())).strip(),
                item.get_jibie_display(),
                ''.join([i.name+' ' for i in  item.suppiler.all() ]).strip(),
                item.created_at.strftime('%Y年%m月%d日 %H:%M'),
                item.order.purchase_date.strftime('%Y年%m月%d日 %H:%M'),
                item.order.expected_data.strftime('%Y年%m月%d日 %H:%M'),
                dianhuo_result,
                dianhuo_desc,
            ]
            rows.append(data) 

        absolute_path = create_csv_file(file_name,rows)
        return absolute_path
    def parse_purchase_ruku(self,csv_path,request_get):
        '''采购 入库-导出csv'''
        suppiler_val = request_get.get('suppilerVal')

        code = request_get.get('code')
        name = request_get.get('name')
        pinlei = request_get.get('pinlei')
        chargers = request_get.get('chargers')
        suppliers = request_get.get('suppliers')
        jibie = request_get.get('jibie')
        start = request_get.get('start')
        end = request_get.get('end')
        dianhuo = request_get.get('dianhuo')
        yanhuo = request_get.get('yanhuo')

        # 首页进入 入库超期
        ruku_exceed = request_get.get('ruku_exceed')


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
        file_name = '入库'
        rows = []
        rows.append(['产品编码','缩略图', '产品名称', '品类', '产品负责人','级别','供应商','创建日期','采购日期','预计到货日期','实际到货日期','点货结果','验货结果'])
        for item in items:
            real_arrival_date = ''
            dianho_result = ''
            if item.dianhuo:
                real_arrival_date = item.dianhuo.real_arrival_date.strftime('%Y年%m月%d日 %H:%M')
                dianho_result = item.dianhuo.get_state_display()
            else:
                real_arrival_date = item.yanhuo.created_at.strftime('%Y年%m月%d日 %H:%M')
            data = [
                item.code,
                QINIU_BASE_DOMAIN + item.goods_skus.first().sku_image,
                item.name,
                item.cate.name,
                ''.join(list(i.extension.name+' ' for i in item.charger.all())).strip(),
                item.get_jibie_display(),
                ''.join([i.name+' ' for i in  item.suppiler.all() ]).strip(),
                item.created_at.strftime('%Y年%m月%d日 %H:%M'),
                item.order.purchase_date.strftime('%Y年%m月%d日 %H:%M'),
                item.order.expected_data.strftime('%Y年%m月%d日 %H:%M'),
                real_arrival_date,
                dianho_result,
                item.yanhuo.get_result_display(),
            ]
            rows.append(data) 

        absolute_path = create_csv_file(file_name,rows)
        return absolute_path

    def parse_select_p_list(self,csv_path,request_get):
        '''候选品品管理-导出csv'''
        

        code = request_get.get('code')
        name = request_get.get('name')
        pinlei = request_get.get('pinlei')
        chargers = request_get.get('chargers')
        suppliers = request_get.get('suppliers')
        dingweis = request_get.get('dingweis')
        jibie = request_get.get('jibie')
        shiling = request_get.get('shiling')
        pifa = request_get.get('pifa')
        pinpai = request_get.get('pinpai')
        start = request_get.get('start')
        end = request_get.get('end')
        creater = request_get.get('creater')
        sku_name = request_get.get('sku_name')

        items = Good.objects.select_related().filter(state_caigou=0).order_by('id')
        # 处理查询条件
        if code:
            items = items.filter(hcode__icontains=code)
        if name:
            items = items.filter(name__icontains=name)
        if jibie:
            items = items.filter(jibie=jibie)
        if shiling:
            items = items.filter(shiling=shiling)
        if pifa:
            items = items.filter(pifa=int(pifa))
        if pinpai != '0':
            brand = get_object_or_404(GoodsBrand,pk=int(pinpai))
            items = items.filter(brand=brand)
        if creater != '0':
            user = get_object_or_404(User,pk=int(creater))
            items = items.filter(creater=user)
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
        if dingweis:
            dingwei_ids = dingweis.split(',')
            int_dingwei_ids = []
            for tem in dingwei_ids:
                if tem!= '':
                    int_dingwei_ids.append(int(tem))
            items = items.filter(dingwei__in=int_dingwei_ids).distinct()
        if pinlei:
            cates = Category.objects.filter(name__icontains=pinlei)
            items = items.filter(cate__in=cates).distinct()
        if sku_name:
            items = items.filter(goods_skus__sku_name__icontains=sku_name).first()


        brands = GoodsBrand.objects.all()
        users = User.objects.filter(is_superuser = False).select_related().all()

        if not items:
            items = []
        for item in items:
            setattr(item,'suppliers',item.suppiler.all())
            setattr(item,'dingweis',item.dingwei.all())
            setattr(item,'chargers',item.charger.all())
        # 是否是导出csv
        file_name = '候选品管理'
        rows = []
        rows.append(['产品预编码', '产品名称', '品类', '产品负责人','级别','定位','时令','供应商','品牌','批发','创建日期'])
        for item in items:
            data = [
                item.hcode,
                item.name,
                item.cate.name,
                ''.join(list(i.extension.name+' ' for i in item.charger.all())).strip(),
                item.get_jibie_display(),
                ''.join(list([i.name+' ' for i in item.dingwei.all() ])).strip(),
                item.get_shiling_display(),
                ''.join([i.name+' ' for i in  item.suppiler.all() ]).strip(),
                item.brand.name,
                item.get_pifa_display(),
                item.created_at.strftime('%Y年%m月%d日 %H:%M'),
            ]
            rows.append(data) 

        absolute_path = create_csv_file(file_name,rows)
        return absolute_path

    def parse_select_pingshen(self,csv_path,request_get):
        '''评审管理-导出csv'''
        code = request_get.get('code')
        name = request_get.get('name')
        pinlei = request_get.get('pinlei')
        chargers = request_get.get('chargers')
        suppliers = request_get.get('suppliers')
        dingweis = request_get.get('dingweis')
        jibie = request_get.get('jibie')
        shiling = request_get.get('shiling')
        pifa = request_get.get('pifa')
        pinpai = request_get.get('pinpai')
        start = request_get.get('start')
        end = request_get.get('end')
        creater = request_get.get('creater')
        sku_name = request_get.get('sku_name')

        items = Good.objects.select_related().filter(state_caigou=0).order_by('id')
        # 处理查询条件
        if code:
            items = items.filter(hcode__icontains=code)
        if name:
            items = items.filter(name__icontains=name)
        if jibie:
            items = items.filter(jibie=jibie)
        if shiling:
            items = items.filter(shiling=shiling)
        if pifa:
            items = items.filter(pifa=int(pifa))
        if pinpai != '0':
            brand = get_object_or_404(GoodsBrand,pk=int(pinpai))
            items = items.filter(brand=brand)
        if creater != '0':
            user = get_object_or_404(User,pk=int(creater))
            items = items.filter(creater=user)
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
        if dingweis:
            dingwei_ids = dingweis.split(',')
            int_dingwei_ids = []
            for tem in dingwei_ids:
                if tem!= '':
                    int_dingwei_ids.append(int(tem))
            items = items.filter(dingwei__in=int_dingwei_ids).distinct()
        if pinlei:
            cates = Category.objects.filter(name__icontains=pinlei)
            items = items.filter(cate__in=cates).distinct()
        if sku_name:
            items = items.filter(goods_skus__sku_name__icontains=sku_name).first()


        brands = GoodsBrand.objects.all()
        users = User.objects.filter(is_superuser = False).select_related().all()

        if not items:
            items = []
        for item in items:
            # 供应商 
            setattr(item,'suppliers',item.suppiler.all())
            setattr(item,'dingweis',item.dingwei.all())
            setattr(item,'chargers',item.charger.all())
        file_name = '评审管理'
        rows = []
        rows.append(['产品预编码', '产品名称', '品类', '产品负责人','级别','定位','时令','供应商','品牌','批发','创建日期'])
        for item in items:
            data = [
                item.hcode,
                item.name,
                item.cate.name,
                ''.join(list(i.extension.name+' ' for i in item.charger.all())).strip(),
                item.get_jibie_display(),
                ''.join(list([i.name+' ' for i in item.dingwei.all() ])).strip(),
                item.get_shiling_display(),
                ''.join([i.name+' ' for i in  item.suppiler.all() ]).strip(),
                item.brand.name,
                item.get_pifa_display(),
                item.created_at.strftime('%Y年%m月%d日 %H:%M'),
            ]
            rows.append(data) 

        absolute_path = create_csv_file(file_name,rows)
        return absolute_path

    def parse_select_add_sku(self,csv_path,request_get):
        '''新品管理-导出csv'''
        code = request_get.get('code')
        name = request_get.get('name')
        pinlei = request_get.get('pinlei')
        chargers = request_get.get('chargers')
        suppliers = request_get.get('suppliers')
        dingweis = request_get.get('dingweis')
        jibie = request_get.get('jibie')
        shiling = request_get.get('shiling')
        pifa = request_get.get('pifa')
        pinpai = request_get.get('pinpai')
        start = request_get.get('start')
        end = request_get.get('end')
        creater = request_get.get('creater')
        sku_name = request_get.get('sku_name')

        items = Good.objects.select_related().filter(state_caigou__gte=1).order_by('code')
        # 处理查询条件
        if code:
            items = items.filter(code__icontains=code)
        if name:
            items = items.filter(name__icontains=name)
        if jibie:
            items = items.filter(jibie=jibie)
        if shiling:
            items = items.filter(shiling=shiling)
        if pifa:
            items = items.filter(pifa=int(pifa))
        if pinpai != '0':
            brand = get_object_or_404(GoodsBrand,pk=int(pinpai))
            items = items.filter(brand=brand)
        if creater != '0':
            user = get_object_or_404(User,pk=int(creater))
            items = items.filter(creater=user)
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
        if dingweis:
            dingwei_ids = dingweis.split(',')
            int_dingwei_ids = []
            for tem in dingwei_ids:
                if tem!= '':
                    int_dingwei_ids.append(int(tem))
            items = items.filter(dingwei__in=int_dingwei_ids).distinct()
        if pinlei:
            cates = Category.objects.filter(name__icontains=pinlei)
            items = items.filter(cate__in=cates).distinct()
        if sku_name:
            items = items.filter(goods_skus__sku_name__icontains=sku_name).distinct()


        brands = GoodsBrand.objects.all()
        users = User.objects.filter(is_superuser = False).select_related().all()

        if not items:
            items = []
        # 注释调set sku 可以提高0.6s
        for item in items:
            # 供应商 
            setattr(item,'suppliers',item.suppiler.all())
            setattr(item,'dingweis',item.dingwei.all())
            setattr(item,'chargers',item.charger.all())

        # 导出csv
        file_name = '新品管理'
        rows = []
        rows.append(['产品编码','sku编码','缩略图', '产品名称','重量','体积', '品类', '产品负责人','级别','定位','时令','供应商','品牌','批发','创建日期'])
        for item in items:
            data = [
                item.code,
                '',
                '',
                item.name,
                '0',
                '0',
                item.cate.name,
                ''.join(list(i.extension.name+' ' for i in item.charger.all())).strip(),
                item.get_jibie_display(),
                ''.join(list([i.name+' ' for i in item.dingwei.all() ])).strip(),
                item.get_shiling_display(),
                ''.join([i.name+' ' for i in  item.suppiler.all() ]).strip(),
                item.brand.name,
                item.get_pifa_display(),
                item.created_at.strftime('%Y年%m月%d日 %H:%M'),
            ]
            rows.append(data) 
            skus = item.goods_skus.all()
            if skus:
                for sku in skus:
                    sku_images = sku.sku_image
                    if sku_images and not sku_images.startswith('http:'):
                        sku_images = QINIU_BASE_DOMAIN + sku_images
                        
                    data2 = [
                        '',
                        str(item.code)+'-'+sku.sku_code,
                        sku_images,
                        sku.sku_name,
                        str(sku.weight) + 'kg',
                        float(sku.height) * float(sku.width) * float(sku.length) / 1000000,
                        '','','','','','','','','',
                    ]
                    rows.append(data2) 

        absolute_path = create_csv_file(file_name,rows)
        return absolute_path
