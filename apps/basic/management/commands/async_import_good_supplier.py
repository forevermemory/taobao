from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from datetime import datetime,timedelta
from django_redis import get_redis_connection

import json
from django.db import transaction
from cpm.models import Good,GoodsSku,Supplier,TagChangjing,TagDingwei,Category,GoodsBrand
import pandas as pd

class Command(BaseCommand):
    '''后台异步导入good'''
    success_msg = '执行后台导入good成功,当前时间为%s' % datetime.date(datetime.now())
    commond = '/home/deploy/.local/share/virtualenvs/cpm-NXD7Laz8/bin/python3.8 /home/deploy/apps/cpm/manage.py async_import_good_supplier >>/home/deploy/apps/log/import.log 2>&1'

    def handle(self, *args, **options):
        conn = get_redis_connection()

        try:
            _type = str(conn.get('_type').decode())
            import_step = str(conn.get('import_step').decode())
            file_path = str(conn.get('file_path').decode())
            user_id = str(conn.get('user_id').decode())
            # 正在读取文件中
            conn.set('is_read_file','1')

            now = datetime.now().timestamp()
            # 先读取文件
            pd_obj = pd.read_excel(file_path,dtype=str)
            conn.set('all_length',len(pd_obj))
            # 删除原来的key
            conn.delete('_type')
            conn.delete('file_path')
            conn.delete('user_id')
            conn.delete('is_read_file')
            num_success = 0
            length = 0

            # 导入供应商后者产品 产品和店铺关系
            if _type == 'supplier':
                num_success,length = self.import_supplier(pd_obj,conn)
            if _type == 'good':
                num_success,length = self.import_good_and_sku(user_id,pd_obj,conn)
            after = datetime.now().timestamp()
            pass_time = int(after-now)

            # 删除进度
            conn.delete('progress')
            # 导入完成后的提示信息
            conn.set('success_length',num_success)
            conn.set('pass_time',pass_time)
            conn.set('import_step','2')

            # 设置有效期为1h
            conn.expire('pass_time',60*60)
            conn.expire('all_length',60*60)
            conn.expire('success_length',60*60)

            print('执行脚本成功,花费的时间为 %d' % pass_time)
        except Exception as err:
            # print('执行脚本成功,花费的时间为 %d' % pass_time)
            print(err)
            print('执行脚本失败')

        
    def import_supplier(self,pd_obj,conn):
        '''导入supplier'''
        success = 0
        # 去除编码重复 
        length = len(pd_obj.values)

        pd_obj.drop_duplicates(subset=['供应商编码'], keep='first', inplace=True)
        pd_obj['备注'] = pd_obj['备注'].fillna('无')
        pd_obj['手机'] = pd_obj['手机'].fillna('无')
        pd_obj['固话'] = pd_obj['固话'].fillna('无')
        pd_obj['联系人'] = pd_obj['联系人'].fillna('无')
        pd_obj['E-mail'] = pd_obj['E-mail'].fillna('无')
        pd_obj['地址'] = pd_obj['地址'].fillna('无')
        # 过滤掉  delete-0418 delete 开头  和 0000开头的 code
        pd_obj= pd_obj[(-pd_obj['供应商编码'].str.contains('delete'))]
        pd_obj = pd_obj[(-pd_obj['供应商编码'].str.startswith('0000'))]
        all_supplier = Supplier.objects.all()
        codes = [i.code for i in all_supplier]   # ['0001', '0002']
        for i in range(0,length):
            conn.set('progress',i / length)
            
            try:
                code = pd_obj.loc[i,'供应商编码']
                # code = str('%04d' % int(pd_obj.loc[i,'供应商编码']))
                if code in codes:
                    print('continue=-----%s' % code)
                    continue
                Supplier.objects.create(
                    code = code,
                    name = pd_obj.loc[i,'供应商名称'],
                    concat = pd_obj.loc[i,'联系人'],
                    address = pd_obj.loc[i,'地址'],
                    telephone = str(pd_obj.loc[i,'手机']),
                    phone = str(pd_obj.loc[i,'固话']),
                    email = pd_obj.loc[i,'E-mail'],
                    note = pd_obj.loc[i,'备注'],
                )        
                success += 1
            except Exception as err:
                print(err)
        return success,length

    def import_good_and_sku(self,user_id,pd_obj,conn):
        '''导入good和skus'''
        # 将上传的good 进行数据清洗
        length = len(pd_obj.values)

        df_goods,df_good_skus = self.parse_good_info(pd_obj) 
        df_goods_length = len(df_goods)
        # 导入good      
        good_success = self.import_good(user_id,df_goods,length,conn)
        # 导入skus
        upload_good_codes = pd_obj['商品编码'].values.tolist()
        sku_success = self.import_good_skus(upload_good_codes,df_good_skus,length,df_goods_length,conn)
        success = good_success + sku_success
        return success,length

    @transaction.atomic
    def import_good(self,user_id,df_goods,all_length,conn):
        '''批量导入good'''
        success = 0
        goods = Good.objects.all()
        good_codes = [i.code for i in goods] 
        # print(good_codes,'++++'*20) 

        # 上传的good codes
        default_brand = GoodsBrand.objects.get(pk=1)
        user = User.objects.get(pk=int(user_id))
        for i in range(0,len(df_goods)):
            # 显示进度
            conn.set('progress',i / all_length)
            save_id = transaction.savepoint()
            try:
                code = df_goods.loc[i,'商品编码']
                if code in good_codes:
                    continue
                print('import --- %s' % code) 
                

                desc = df_goods.loc[i,'备注']
                if str(desc) == 'nan':
                    desc = '无'
                pifa = df_goods.loc[i,'批发']
                if str(pifa) == 'nan':
                    pifa = 0
                jibie = df_goods.loc[i,'级别']
                if str(jibie) == 'nan':
                    jibie = 0
                shiling = df_goods.loc[i,'时令']
                if str(shiling) == 'nan':
                    shiling = 0

                good = Good.objects.create(
                    code = code,
                    name = df_goods.loc[i,'商品名称'],
                    shiling = shiling,
                    jibie = jibie,
                    pifa = pifa,
                    desc = desc,
                    creater = user,
                )
                brand_name = df_goods.loc[i,'品牌'].strip()
                good.brand = default_brand
                if brand_name != 'nan':
                    brand_exist = GoodsBrand.objects.filter(name__contains=brand_name).first()
                    if brand_exist:
                        good.brand = brand_exist

                good.cate = Category.objects.get(pk=int(df_goods.loc[i,'品类']))


                # 设置多对多关系
                charger_arr = df_goods.loc[i,'产品负责人'].strip().split(',')
                for temp in charger_arr:
                    if temp != '':
                        user = User.objects.get(pk=int(temp))
                        if user:
                            good.charger.add(user)
                # # 供应商
                product_gen = df_goods.loc[i,'供应商']  #TODO 报错
                if product_gen != 'nan':
                    supplier_arr = product_gen.strip().split(',')
                    for temp in supplier_arr:
                        if temp != '':
                            supplier = Supplier.objects.get(pk=int(temp))
                            if supplier:
                                good.suppiler.add(supplier)

                # # 定位
                dingwei = df_goods.loc[i,'定位']
                if dingwei != 'nan':
                    tag_dingwei_arr = dingwei.strip().split(',')
                    for temp in tag_dingwei_arr:
                        if temp != '':
                            tag_dingwei = TagDingwei.objects.get(pk=int(temp))
                            if tag_dingwei:
                                good.dingwei.add(tag_dingwei)
                # # 场景
                changjing = df_goods.loc[i,'场景']
                if changjing != 'nan':
                    tag_changjing_arr = changjing.split(',')
                    for temp in tag_changjing_arr:
                        if temp != '':
                            tag_changjing = TagChangjing.objects.get(pk=int(temp))
                            if tag_changjing:
                                good.changjing.add(tag_changjing)
                
                # # 设置good的各个阶段状态

                # 判断销售状态一列的值
                im_sale_stat = df_goods.loc[i,'销售状态']
                #    '淘汰':'0', '已上架':'1', '已退市':'2',
                if im_sale_stat == '1':
                    good.state_sale = 11
                elif im_sale_stat == '0':
                    good.state_sale = 12
                elif im_sale_stat == '2':
                    good.state_sale = 13

                good.state_caigou = 1 # 新品上面展示
                good.is_multi_export = True
                good.save()
                success += 1
                transaction.savepoint_commit(save_id)
            except Exception as err:
                transaction.savepoint_rollback(save_id)
                print(err,'******'*10)
        return success
        

    def import_good_skus(self,good_codes,skus,all_length,df_goods_length,conn):
        '''导入skus'''
        success = 0
        # conn = get_redis_connection()
        goods = Good.objects.filter(code__in=good_codes)
        goods_skus = []

        for_length = len(skus['规格编码'].values.tolist()) # 4436
        print(len(skus))
        print('***')
        print('***')
        print('***')
        # 这里的变化也没有找到全部存在的了问题
        for good in goods:
            cur_skus = good.goods_skus.all() 
            exist_skus_codes = [str(good.code) + str(i.sku_code) for i in cur_skus]
            goods_skus += exist_skus_codes

        print(len(goods_skus))  # 4350 知道T19614-001
        # return 

        ajax_upload_list = []

        # TODO 是循环的长度有问题
        for i in range(0,for_length):
            try:
                conn.set('progress',(i + df_goods_length) / all_length)
                # 异步上传图片到百度
                ajax_upload_dict = {}
                # save_id = transaction.savepoint()

                good_code = skus.loc[i,'商品编码']
                good = Good.objects.filter(code=good_code).first()

                # 判断sku是否存在了
                sku_code_raw = skus.loc[i,'规格编码']
                if sku_code_raw == 'nan':
                    print(sku_code_raw)
                    print('con1--')
                    continue
                sku_code_list = sku_code_raw.split('-')
                if len(sku_code_list) <2:
                    print(sku_code_list)
                    print('con2--')
                    continue
                sku_code = sku_code_list[1]
                if str(good_code) + str(sku_code) in goods_skus:
                    # print('continue-- %s' % str(good_code) + str(sku_code))
                    continue

                
                sku_name = skus.loc[i,'规格值1'].strip()

                # 重新过滤nan
                sku_weight = skus.loc[i,'重量(kg)']
                if sku_weight == 'nan':
                    sku_weight = '0.0'
                sku_length = skus.loc[i,'长(cm)']
                if sku_length == 'nan':
                    sku_length = '0.0'
                sku_width = skus.loc[i,'宽(cm)']
                if sku_width == 'nan':
                    sku_width = '0.0'
                sku_height = skus.loc[i,'高(cm)']
                if sku_height == 'nan':
                    sku_height = '0.0'

                sku_bar_code = skus.loc[i,'条码']
                if sku_bar_code == 'nan':
                    sku_bar_code = '0.0'
                price_jin = skus.loc[i,'参考进价']
                if price_jin == 'nan':
                    price_jin = '0.0'
                price_sale = skus.loc[i,'标准售价']
                if price_sale == 'nan':
                    price_sale = '0.0'
                price_pifa = skus.loc[i,'批发价']
                if price_pifa == 'nan':
                    price_pifa = '0.0'

                quality = skus.loc[i,'保质期(天)']
                if quality == 'nan':
                    quality = '0'
                number_box = skus.loc[i,'装箱数']
                if number_box == 'nan':
                    number_box = '0'
                p_cycle = skus.loc[i,'采购周期']
                if p_cycle == 'nan':
                    p_cycle = '0'
                desc = ''
                price_is_limit = skus.loc[i,'是否限价']
                if price_is_limit == 'nan':
                    price_is_limit = False

                date_market = skus.loc[i,'上市日期']

                

                if date_market != 'nan':
                    date_market = datetime.strptime(date_market,'%Y-%m-%d %H:%M:%S')
                else:
                    date_market = datetime.now()

                good_sku = GoodsSku.objects.create(
                    sku_good = good,
                    sku_code = sku_code,
                    sku_bar_code = sku_bar_code,
                    sku_name = sku_name,

                    length = sku_length,
                    width = sku_width,
                    height = sku_height,
                    weight = sku_weight,

                    price_jin = int(float(price_jin)*100),
                    price_sale = int(float(price_sale)*100),
                    price_pifa = int(float(price_pifa)*100),

                    quality = quality,
                    number_box = number_box,
                    p_cycle = p_cycle,
                    desc = desc,
                    price_is_limit = price_is_limit,
                    date_market = date_market,
                )

                sku_image = skus.loc[i,'图片1']
                if sku_image != '无':
                    # 存储到百度 用于图像识别 存到redis 后台ajax发送请求执行
                    # BaiduImageSearch().upload_remote_url(sku_image,good.id,good_sku.id)
                    ajax_upload_dict['sku_image'] = sku_image
                    ajax_upload_dict['good_id'] = good.id
                    ajax_upload_dict['sku_id'] = good_sku.id
                    ajax_upload_list.append(ajax_upload_dict)
                else:
                    sku_image = ''



                good_sku.sku_image = sku_image
                good_sku.save()
                # print('sku save upload to baidu success %d'  % good_sku.id)
                success += 1
                print('导入sku完成 sku %s - %s' % (good_code,sku_code))
                # print('导入sku完成-- %s' % good_sku.id)
                # transaction.savepoint_commit(save_id)
            except Exception as err:
                # transaction.savepoint_rollback(save_id)
                print(err)

        # 存到redis
        conn = get_redis_connection()
        conn.set('ajax_upload_skus_to_baidu',json.dumps(ajax_upload_list))
        conn.expire('ajax_upload_skus_to_baidu',60*30)
        return success

    def parse_good_info(self,df):
        '''对上传的good和skus模板数据进行清洗'''
        df = df[['商品编码','商品名称','规格编码','规格值1','规格值2','条码','重量(kg)','长(cm)',\
            '宽(cm)','高(cm)','体积(m³)','标准售价','批发价'\
            ,'参考进价','单位','品牌','备注','消耗周期(天)','品类','产品负责人',\
            '时令','级别','批发','定位','场景','销售状态','保质期(天)',\
            '上新状态','是否限价','装箱数','上市日期','采购周期','图片1','供应商']]
        # 填充需要的列 根据商品编码
        need_to_fills = ['商品编码','商品名称','品类','品牌','供应商','产品负责人',\
            '时令','级别','批发','定位','场景','销售状态','上新状态','是否限价',\
            '装箱数','上市日期','采购周期','保质期(天)']
        for need in need_to_fills:
            df[need] = self.parse_curr_nan(df,need)
        # 过滤掉 四位数字的产品 包括skus 多位数字编码也过滤
        df = df[df['商品编码'].str.len() >4]
        df = df[df['商品编码'].str.len() <7]

        # 日期转换
        # df['上市日期'] = pd.TimedeltaIndex(df['上市日期'], unit='d') + datetime(1899,12,30)

        df_good_skus = self.clear_good_skus(df)
        df_goods = self.clear_goods(df)
        return df_goods,df_good_skus

    def clear_good_skus(self,df):
        '''清洗skus'''
        df_sku = df[['商品编码','规格编码','规格值1','规格值2','条码','重量(kg)','长(cm)','宽(cm)',\
                '高(cm)','体积(m³)','标准售价','批发价','参考进价','单位','消耗周期(天)',\
                '是否限价','装箱数','上市日期','采购周期','图片1','保质期(天)']]

        # 拼接规格值1和2
        # df_sku['规格值2'] = df_sku['规格值2'].fillna(' ')
        df_sku['规格值1'] = df_sku['规格值1'].str.cat(df_sku['规格值2'],na_rep='')
        df_sku['条码'] = df_sku['条码'].fillna('无')
        df_sku['重量(kg)'] = df_sku['重量(kg)'].fillna('0.0')
        df_sku['长(cm)'] = df_sku['长(cm)'].fillna('0.0')
        df_sku['宽(cm)'] = df_sku['宽(cm)'].fillna('0.0')
        df_sku['高(cm)'] = df_sku['高(cm)'].fillna('0.0')

        df_sku['图片1'] = df_sku['图片1'].fillna('无')
        df_sku['保质期(天)'] = df_sku['保质期(天)'].fillna('0')
        df_sku['装箱数'] = df_sku['装箱数'].fillna('0')
        df_sku['采购周期'] = df_sku['采购周期'].fillna('0')
        df_sku['参考进价'] = df_sku['参考进价'].fillna('0')
        df_sku['标准售价'] = df_sku['标准售价'].fillna('0')
        df_sku['批发价'] = df_sku['批发价'].fillna('0')
        df_sku['是否限价'] = df_sku['是否限价'].fillna('否')
        df_sku.replace({'是否限价': {'否': False,'是':True}}, inplace=True)


        # 去除不是商品编码开头的sku
        g_code = df_sku['规格编码'].values.tolist()
        print(len(g_code))  # 4521
        print('------')
        print('------')
        print('------')
        r_list = []
        for i,val in enumerate(df_sku['商品编码'].values.tolist()):
            # print(val,'---',str(g_code[i]))
            r_list.append(str(g_code[i]).startswith(val))
        df_sku = df_sku[r_list]
        df_sku = df_sku.reset_index(drop=True)
        print(len(df_sku['规格编码'].values.tolist()))  # 这里是正常的 4436
        return df_sku


    def clear_goods(self,df):
        '''清洗good'''
        df_good = df[['商品编码','商品名称','品牌','备注','品类','产品负责人','时令','级别',\
                '批发','定位','场景','销售状态','采购周期','供应商','上新状态','上市日期']]
        df_good.drop_duplicates(subset=['商品编码'], keep='first', inplace=True)
        df_good2 = df_good.reset_index(drop=True)
        # 品牌去数据库查询 全部查询出来 判断是否 in brands
        df_good2.replace({'时令': {'常规': '0', '夏季': '2','冬季':'1'}}, inplace=True)
        df_good2.replace({'级别': {'普通': '0', '重点': '2','核心':'1'}}, inplace=True)
        df_good2.replace({'批发': {'不可批发': '0','可批发':'1'}}, inplace=True)

        p_charger = {
            '沈黎丹':'8',
            '黄琦':'9',
        }
        p_sale_stat = {
            '淘汰':'0',
            '已上架':'1',
            '已退市':'2',
        }
        p_dingwei = {
            '日销款':'1',
            '利润款':'2',
            '流量款':'3',
            '活动款':'4',
            '形象款':'5',
        }
        df_good2.replace({'定位': p_dingwei}, inplace=True)
        df_good2.replace({'产品负责人': p_charger}, inplace=True)
        df_good2.replace({'销售状态': p_sale_stat}, inplace=True)
        return df_good2

        

    # 
    def parse_curr_nan(self,df,para):
        '''根据产品分组替换需要nan'''
        g_code = df[para].values.tolist()
        last_exist = 'nan'
        for i,val in enumerate(g_code):
            if str(val) == 'nan':
                g_code[i] = last_exist
            else:
                last_exist = val
        return g_code

