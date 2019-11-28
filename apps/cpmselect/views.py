from django.shortcuts import render,redirect,reverse,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.http import HttpResponse,JsonResponse,QueryDict
from django.core import serializers
from django.contrib.auth.models import User
from django.db import transaction
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from utils.export_csv import export_csv
from utils.login_required import LoginRequiredMixin
from utils.page_util import get_pagination_data
from utils.baidu_image_retrieve import BaiduImageSearch

from datetime import datetime
from urllib import parse
from cpm.settings import PAGE_SIZE,QINIU_BASE_DOMAIN
from cpmauth.models import Role
from cpm.models import Category,SonCategory,Good,GoodsBrand,GoodsSku,TagChangjing,TagDingwei,Supplier,GoodsSelectPhase,SupplierChange,ChargerChange,GoodsPingshenPhase,GOOD_PINGSHEN_CANCEL,GOOD_PINGSHEN_WAIT


# 产品
class CpmProduct(LoginRequiredMixin, View):
    def get(self,request):
        #  渲染  [{'':['']},{},{}]
        tags = [
            {'name':'选品','val':['候选品','评审','新增商品','批量导入']},
            {'name':'上新准备','val':['采购','分货','验货','入库','拍摄','制作','店铺录入']},
            {'name':'销售','val':['启封','封存','淘汰','退市']}
        ]

        context = {
            'msg':'商品流程导航',
            'pro_index':True,
            'tags':tags,
        }
        return render(request,'select/product/product.html',context=context)


class CpmEditOneProduct(LoginRequiredMixin, View):
    '''# 候选商品编辑'''
    def get(self,request):
        pid = request.GET.get('pid','')
        good = get_object_or_404(Good,pk=int(pid))
        brands = GoodsBrand.objects.all()
        chargers = User.objects.filter(extension__role__name=0)
        new = request.GET.get('new','')

        setattr(good,'suppliers',good.suppiler.all())
        setattr(good,'chargers',good.charger.all()[0])
        setattr(good,'dingweis',good.dingwei.all())
        setattr(good,'changjings',good.changjing.all())
        context = {
            'msg':'修改候选商品',
            'good':good,
            'brands':brands,
            'chargers':chargers,
        }
        if new:
            return render(request,'select/product/product_new_edit_one.html',context=context)

        return render(request,'select/product/product_edit_one.html',context=context)

    @transaction.atomic
    def post(self,request):
        pid = request.POST.get('pid')

        code = request.POST.get('code')
        hcode = request.POST.get('hcode')
        name = request.POST.get('name')
        shiling = request.POST.get('shiling')
        jibie = request.POST.get('jibie')
        pifa = request.POST.get('pifa')
        desc = request.POST.get('desc')
        new = request.POST.get('new','')
        exist_good_hcode = Good.objects.filter(hcode=hcode).first()

        # 校验hcode或者code是否重复
        if exist_good_hcode:
            if exist_good_hcode.id != int(pid):
                return JsonResponse({'code':'8','msg':'hcode is repeated,'})
        exist_good_code = Good.objects.filter(code=code).first()
        if exist_good_code:
            if exist_good_code.id != int(pid):
                return JsonResponse({'code':'8-1','msg':'code is repeated,'})

        pinlei_id = request.POST.get('pinleis')
        pinpai_id = request.POST.get('pinpai')

        tag_dingwei_ids = request.POST.get('tag_dingwei')
        tag_changjing_ids = request.POST.get('tag_changjing')

        charger_ids = request.POST.get('chargers')
        raw_chargers = request.POST.get('raw_chargers')
        suppliers_ids = request.POST.get('suppliers')
        raw_suppliers = request.POST.get('raw_suppliers')
        is_change_charger = request.POST.get('is_change_charger')
        is_change_supplier = request.POST.get('is_change_supplier')
        # 设置事务保存点
        save_id = transaction.savepoint()
        try:
            good = Good.objects.get(pk=int(pid))
            if code:
                good.code = code
            if hcode:
                good.hcode = hcode
            good.name = name
            good.desc = desc
            good.shiling = shiling
            good.jibie = jibie
            good.pifa = pifa
            good.brand = GoodsBrand.objects.get(pk=int(pinpai_id))
            good.cate = Category.objects.get(pk=int(pinlei_id))

            # 多对多关系重新设置
            good.dingwei.clear()
            tag_dingwei_arr = tag_dingwei_ids.split(',')
            for temp in tag_dingwei_arr:
                if temp != '':
                    dw = TagDingwei.objects.get(pk=int(temp))
                    good.dingwei.add(dw)

            good.changjing.clear()
            tag_changjing_arr = tag_changjing_ids.split(',')
            for temp in tag_changjing_arr:
                if temp != '':
                    cj = TagChangjing.objects.get(pk=int(temp))
                    good.changjing.add(cj)
            good.save()

            if is_change_charger == 'true':
                # 变更了负责人
                good.charger.clear()
                chargers_arr = charger_ids.split(',')
                for temp in chargers_arr:
                    if temp != '':
                        char = User.objects.get(pk=int(temp))
                        good.charger.add(char)
                # 记录变更记录
                charger_change = ChargerChange.objects.create(good = good)
                # 原负责人
                raw_chargers_arr = raw_chargers.split(',')
                for temp in raw_chargers_arr:
                    if temp != '':
                        char = User.objects.get(pk=int(temp))
                        charger_change.raw_charger.add(char)
                # 现负责人
                now_chargers_arr = charger_ids.split(',')
                for temp in now_chargers_arr:
                    if temp != '':
                        char = User.objects.get(pk=int(temp))
                        charger_change.now_charger.add(char)
                charger_change.save()
                good.save()

            if is_change_supplier == 'true':
                # 变更了供应商
                good.suppiler.clear()
                suppliers_arr = suppliers_ids.split(',')
                for temp in suppliers_arr:
                    if temp != '':
                        char = Supplier.objects.get(pk=int(temp))
                        good.suppiler.add(char)
                # 记录变更记录
                suppiler_change = SupplierChange.objects.create(good = good)
                # 原供应商
                raw_suppliers_arr = raw_suppliers.split(',')
                for temp in raw_suppliers_arr:
                    if temp != '':
                        char = Supplier.objects.get(pk=int(temp))
                        suppiler_change.raw_supplier.add(char)
                # 现供应商
                now_suppliers_arr = suppliers_ids.split(',')
                for temp in now_suppliers_arr:
                    if temp != '':
                        char = Supplier.objects.get(pk=int(temp))
                        suppiler_change.now_supplier.add(char)
                suppiler_change.save()
                good.save()
                
            transaction.savepoint_commit(save_id)
        except Exception as err:
            print(err)
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'code':'2','msg':'更新失败,请刷新重试!'})
            
        return JsonResponse({'code':'0','msg':'ok ','new':new,'url':'/select/add_one_success?pid='+str(good.id)})


# 新增候选商品
class CpmAddOneProduct(LoginRequiredMixin, View):
    def get(self,request):
        brands = GoodsBrand.objects.all()
        chargers = User.objects.filter(extension__role__name=0)
        # 'chargers':chargers,
        context = {
            'brands':brands,
            'msg':'新增候选商品',
            'add_one':True,
            'chargers':chargers,
        }
        return render(request,'select/product/product_add_one.html',context=context)

    @transaction.atomic
    def post(self,request):

        hcode = request.POST.get('hcode')
        exist_good_hcode = Good.objects.filter(hcode=hcode).first()
        if exist_good_hcode:
            return JsonResponse({'code':'8','msg':'hcode is repeated,please try again!'})
        name = request.POST.get('name')
        pinlei_id = request.POST.get('pinleis')
        pinpai_id = request.POST.get('pinpai')
        charger_ids = request.POST.get('chargers')
        suppliers_ids = request.POST.get('suppliers')
        shiling = request.POST.get('shiling')
        jibie = request.POST.get('jibie')
        pifa = request.POST.get('pifa')
        tag_dingwei_ids = request.POST.get('tag_dingwei')
        tag_changjing_ids = request.POST.get('tag_changjing')
        desc = request.POST.get('desc')
        # creater_id = request.user.id
        # 设置事务保存点
        save_id = transaction.savepoint()

        try:
            good = Good.objects.create(
                hcode = hcode,
                name = name,
                creater = request.user,
                shiling = shiling,
                jibie = jibie,
                pifa = pifa,
                desc = desc,
            )
            good.brand = GoodsBrand.objects.get(pk=int(pinpai_id))
            good.cate = Category.objects.get(pk=int(pinlei_id))
            print('good---设置多对多关系')
            # 设置多对多关系
            # 负责人
            charger_arr = charger_ids.split(',')
            for temp in charger_arr:
                if temp != '':
                    user = User.objects.get(pk=int(temp))
                    good.charger.add(user)
            # 供应商
            supplier_arr = suppliers_ids.split(',')
            for temp in supplier_arr:
                if temp != '':
                    supplier = Supplier.objects.get(pk=int(temp))
                    good.suppiler.add(supplier)
            # 定位
            tag_dingwei_arr = tag_dingwei_ids.split(',')
            for temp in tag_dingwei_arr:
                if temp != '':
                    tag_dingwei = TagDingwei.objects.get(pk=int(temp))
                    good.dingwei.add(tag_dingwei)
            # 场景
            tag_changjing_arr = tag_changjing_ids.split(',')
            for temp in tag_changjing_arr:
                if temp != '':
                    tag_changjing = TagChangjing.objects.get(pk=int(temp))
                    good.changjing.add(tag_changjing)
            print('多对多关系设置ＯＫ')
            # category存入失败


            good.save()
            transaction.savepoint_commit(save_id)
        except Exception as err:
            print(err)
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'code':'1','msg':'err,please try again!'})
        # return reverse(redirect('select:add_one_success'))
        return JsonResponse({'code':'0','msg':'ok','url':'/select/add_one_success?pid='+str(good.id),'pid':good.id})

class CpmProductCancelOne(View):
    '''终止一个产品'''
    def get(self,request):
        good_id = request.GET.get('good_id')
        print(good_id)
        try:
            good = Good.objects.get(pk=int(good_id))
            good.state_caigou = 2
            good.save()

        except Exception as err:
            return JsonResponse({'code':'2','msg':'操作失败，请重试'})
        return JsonResponse({'code':'0','msg':'ok'})


class CpmAddOneProductSuccess(LoginRequiredMixin,View):
    '''新增候选品成功的重定向页面'''
    def get(self,request):
        query_url = request.GET.get('query_url')
        pid = request.GET.get('pid')
        return render(request,'select/product/product_add_one_success.html',{'msg':'新增/编辑候选商品成功','pid':pid})


class CpmAddOneKindProduct(LoginRequiredMixin,View):
    '''get supplier charger dingwei changjing role api return json'''
    def get(self,request):
        kind = request.GET.get('kind')
        if kind=='charger':
            chargers = User.objects.filter(extension__role__name=0)
            # 主表对象名.从表类名小写 有 related_name='extension'用related_name
            # 反向　与正向查询一个意思 https://blog.csdn.net/weixin_43796223/article/details/88636840
            temp_chargers  = []
            for c in chargers:
                temp_dict = {}
                temp_dict['id'] = c.id
                temp_dict['name'] = c.extension.name
                temp_chargers.append(temp_dict)
            return JsonResponse({'chargers':temp_chargers,'kind':kind})
        elif kind == 'supplier':
            suppliers = Supplier.objects.all()
            return JsonResponse({'suppliers':serializers.serialize('json',suppliers),'kind':kind})
        elif kind == 'role':
            roles = Role.objects.all()
            return JsonResponse({'roles':serializers.serialize('json',roles),'kind':kind})
        elif kind == 'dingwei':
            dingweis = TagDingwei.objects.all()
            return JsonResponse({'dingweis':serializers.serialize('json',dingweis),'kind':kind})
        elif kind == 'changjing':
            changjings = TagChangjing.objects.all()
            return JsonResponse({'changjings':serializers.serialize('json',changjings),'kind':kind})
        else:
            return JsonResponse({'code':'0','msg':'unknown err'})
            
            



class CpmProductSelectList(LoginRequiredMixin,View):
    '''候选品列表'''
    def get(self,request):
        # 查询条件
        dingwei_val = request.GET.get('dingweiVal','')
        suppiler_val = request.GET.get('suppilerVal','')
        spread = request.GET.get('spread','')
        

        code = request.GET.get('code','')
        name = request.GET.get('name','')
        pinlei = request.GET.get('pinlei','')
        chargers = request.GET.get('chargers','')
        suppliers = request.GET.get('suppliers','')
        dingweis = request.GET.get('dingweis','')
        jibie = request.GET.get('jibie','')
        shiling = request.GET.get('shiling','')
        pifa = request.GET.get('pifa','')
        pinpai = request.GET.get('pinpai','0')
        start = request.GET.get('start','')
        end = request.GET.get('end','')
        creater = request.GET.get('creater','0')
        sku_name = request.GET.get('sku_name','')
        page = int(request.GET.get('p',1))

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
            setattr(item,'dingweis',item.dingwei.all())
            setattr(item,'chargers',item.charger.all())
        # 是否是导出csv



        context = {
            'p_list':True,
            'brands':brands,
            'users':users,
            'chargers_all': User.objects.filter(extension__role__name=0),
            'query_url':'/select/p_list/',
            'msg':'候选品列表',
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
                'dingweis': dingweis or '',
                'jibie': jibie or '',
                'shiling': shiling or '',
                'pifa': pifa or '',
                'pinpai': pinpai or '',
                'start': start or '',
                'end': end or '',
                'creater': creater or '',
                'sku_name': sku_name or '',
            })
        }
        # 控制扩展显示和隐藏
        if spread == 'false':
            spread =False
        else:
            spread = True
        # 查询参数返回

        if chargers:
            chargers = int(chargers)
        url_query_data = {
            'suppiler_val':suppiler_val,
            'dingwei_val':dingwei_val,
            'chargers':chargers,
            'suppliers':suppliers,
            'dingweis':dingweis,
            'code':code,
            'name':name,
            'sku_name':sku_name,
            'pinlei':pinlei,
            'start':start,
            'end':end,
            'spread':spread,
            'jibie':jibie,
            'shiling':shiling,
            'pifa':pifa,
            'creater':int(creater),
            'pinpai':int(pinpai),

        }
        page_data = get_pagination_data(paginator,page_obj)
        context.update(page_data)
        context.update(url_query_data)
        return render(request,'select/product/product_select_list.html',context=context)
    
    def export_csv(self,context,file_name):
        '''导出csv'''
        print('导出csv')
        # filename = "候选品管理"
        response = HttpResponse()
        response['Content-Type']=' application/octet-stream'  
        response['Content-Disposition'] = 'attachment;filename="%s"'%(urlquote(file_name))
        context = context
        
        template = loader.get_template('csv/houxuanpin.txt')
        csv_template = template.render(context)
        response.content = csv_template
        return response



class CpmQueryCategory(View):
    '''查询品类API'''
    '''1 167   2 3360  3 10787 4 9717  24031 23931'''
    def get(self,request):
        is_cate = request.GET.get('is_cate')
        first_id = request.GET.get('first')
        second_id = request.GET.get('second')
        third_id = request.GET.get('third')
        enter_query = request.GET.get('enter_query')

        # 品类管理 自定义新增品类
        if is_cate == '1':
            if enter_query:
                querys = Category.objects.filter(name=enter_query,is_parent=0)
                return JsonResponse({'items':serializers.serialize('json',querys)})
            if first_id:
                second_cate = Category.objects.filter(level=2,parent_id=int(first_id))
                return JsonResponse({'items':serializers.serialize('json',second_cate)})
            if second_id:
                third_cate = Category.objects.filter(level=3,parent_id=int(second_id))
                return JsonResponse({'items':serializers.serialize('json',third_cate)})
            if third_id:
                forth_cate = Category.objects.filter(level=4,parent_id=int(third_id))
                return JsonResponse({'items':serializers.serialize('json',forth_cate)})

            first_cate = Category.objects.filter(level=1)
            return JsonResponse({'items':serializers.serialize('json',first_cate)})

        if enter_query:
            querys = SonCategory.objects.filter(name=enter_query,is_parent=0)
            return JsonResponse({'items':serializers.serialize('json',querys)})
        if first_id:
            second_cate = SonCategory.objects.filter(level=2,parent_id=int(first_id))
            return JsonResponse({'items':serializers.serialize('json',second_cate)})
        if second_id:
            third_cate = SonCategory.objects.filter(level=3,parent_id=int(second_id))
            return JsonResponse({'items':serializers.serialize('json',third_cate)})
        if third_id:
            forth_cate = SonCategory.objects.filter(level=4,parent_id=int(third_id))
            return JsonResponse({'items':serializers.serialize('json',forth_cate)})

        first_cate = SonCategory.objects.filter(level=1)
        # print(len(first_cate))
        return JsonResponse({'items':serializers.serialize('json',first_cate)})
        

        # 查询所有一级
        # https://www.17sucai.com/pins/demo-show?id=29426
        # https://www.17sucai.com/pins/29426.html
        # https://github.com/Copterfly/regionPicker


class CpmProductSelectListPingshen(LoginRequiredMixin,View):
    '''评审列表页面'''
    def get(self,request):
        # 查询条件
        dingwei_val = request.GET.get('dingweiVal','')
        suppiler_val = request.GET.get('suppilerVal','')
        
        spread = request.GET.get('spread','')
        

        code = request.GET.get('code','')
        name = request.GET.get('name','')
        pinlei = request.GET.get('pinlei','')
        chargers = request.GET.get('chargers','')
        suppliers = request.GET.get('suppliers','')
        dingweis = request.GET.get('dingweis','')
        jibie = request.GET.get('jibie','')
        shiling = request.GET.get('shiling','')
        pifa = request.GET.get('pifa','')
        pinpai = request.GET.get('pinpai','0')
        start = request.GET.get('start','')
        end = request.GET.get('end','')
        creater = request.GET.get('creater','0')
        sku_name = request.GET.get('sku_name','')
        page = int(request.GET.get('p',1))

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
            setattr(item,'dingweis',item.dingwei.all())
            setattr(item,'chargers',item.charger.all())
        # 是否是导出csv

        context = {
            'p_list_pingshen':True,
            'brands':brands,
            'users':users,
            'query_url':'/select/pingshen/',
            'msg':'候选品列表',
            'chargers_all': User.objects.filter(extension__role__name=0),
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'cancels': GOOD_PINGSHEN_CANCEL,
            'waits': GOOD_PINGSHEN_WAIT,
            'last_pages':len_items/PAGE_SIZE +1,
            # 查询参数
            'url_query': '&'+parse.urlencode({   
                # 'p': page or '',
                'code': code or '',
                'name': name or '',
                'pinlei': pinlei or '',
                'chargers': chargers or '',
                'suppliers': suppliers or '',
                'dingweis': dingweis or '',
                'jibie': jibie or '',
                'shiling': shiling or '',
                'pifa': pifa or '',
                'pinpai': pinpai or '',
                'start': start or '',
                'end': end or '',
                'creater': creater or '',
                'sku_name': sku_name or '',
            })
        }
        # 控制扩展显示和隐藏
        if spread == 'false':
            spread =False
        else:
            spread = True
        # 查询参数返回
        if chargers:
            chargers=int(chargers)
        url_query_data = {
            'suppiler_val':suppiler_val,
            'dingwei_val':dingwei_val,
            'chargers':chargers,
            'suppliers':suppliers,
            'dingweis':dingweis,
            'code':code,
            'name':name,
            'sku_name':sku_name,
            'pinlei':pinlei,
            'start':start,
            'end':end,
            'spread':spread,
            'jibie':jibie,
            'shiling':shiling,
            'pifa':pifa,
            'creater':int(creater),
            'pinpai':int(pinpai),

        }
        page_data = get_pagination_data(paginator,page_obj)
        context.update(page_data)
        context.update(url_query_data)
        return render(request,'select/product/product_s_l_pingshen.html',context=context)
    
    def post(self,request):
        '''评审'''
        pid = request.POST.get('pid')
        state = request.POST.get('state')
        hcode = request.POST.get('hcode')
        desc = request.POST.get('desc')
        wait = request.POST.get('wait')
        cancel = request.POST.get('cancel')
        try:
            good = get_object_or_404(Good,pk=int(pid))
            good.state_caigou = int(state)
            # 1 通过　0 待定　2 终止
    
            if state == '1':
                # 通过评审 
                # 查询最后一条通过评审的good的code 
                new_good_pingshen = GoodsPingshenPhase.objects.first()
                if not new_good_pingshen:
                    good.code = '19001'
                else:
                    # 这里应该从最新通过评审的产品中取code
                    last_good_pingshen = GoodsPingshenPhase.objects.filter(cancel__isnull=True,wait__isnull=True).order_by('-created_at')[0]
                    tnow_code = last_good_pingshen.good.code

                    now_code = self.check_good_code(tnow_code+1)
                    if now_code == 0:
                        good.code = '19001'
                    else:
                        # 因为用户可以任意修改code 这里需要校验
                        good.code = str(int(now_code))
                GoodsPingshenPhase.objects.create(
                    pingshener = request.user,
                    good = good,
                    desc = desc,
                )

            elif state == '0':
                # 记录评审人
                GoodsPingshenPhase.objects.create(
                    pingshener = request.user,
                    good = good,
                    desc = desc,
                    wait = int(wait)
                )
            elif state == '2':
                GoodsPingshenPhase.objects.create(
                    pingshener = request.user,
                    good = good,
                    desc = desc,
                    cancel = int(cancel)
                )
            good.save()
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'err'})
        return JsonResponse({'code':'0','msg':'ok','url':'/select/pingshen/'})

    def check_good_code(self,code):
        '''递归查询合适的code'''
        good = Good.objects.filter(code=code).first()
        if good:
            return self.check_good_code(code+1)
        else:
            return code





class CpmProductSelectListAddSKU(LoginRequiredMixin,View):
    '''新品列表页面 '''
    def get(self,request):
        # 查询条件
        dingwei_val = request.GET.get('dingweiVal','')
        suppiler_val = request.GET.get('suppilerVal','')
        spread = request.GET.get('spread','')
        

        code = request.GET.get('code','')
        name = request.GET.get('name','')
        pinlei = request.GET.get('pinlei','')
        chargers = request.GET.get('chargers','')
        suppliers = request.GET.get('suppliers','')
        dingweis = request.GET.get('dingweis','')
        jibie = request.GET.get('jibie','')
        shiling = request.GET.get('shiling','')
        pifa = request.GET.get('pifa','')
        pinpai = request.GET.get('pinpai','0')
        start = request.GET.get('start','')
        end = request.GET.get('end','')
        creater = request.GET.get('creater','0')
        sku_name = request.GET.get('sku_name','')
        page = int(request.GET.get('p',1))

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
            items = items.filter(goods_skus__sku_name__icontains=sku_name).distinct()


        brands = GoodsBrand.objects.all()
        users = User.objects.filter(is_superuser = False).select_related().all()
        # 分页
        len_items = len(items)  # 总的记录数
        paginator = Paginator(items,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1
        page_obj = paginator.page(page)
        items = page_obj.object_list
        if not items:
            items = []
        # 注释调set sku 可以提高0.6s
        for item in items:
            # 供应商 
            setattr(item,'suppliers',item.suppiler.all())
            setattr(item,'dingweis',item.dingwei.all())
            setattr(item,'chargers',item.charger.all())


        context = {
            'add_sku':True,
            'brands':brands,
            'users':users,
            'chargers_all': User.objects.filter(extension__role__name=0),
            'query_url':'/select/add_sku/',
            'msg':'新品列表',
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
                'dingweis': dingweis or '',
                'jibie': jibie or '',
                'shiling': shiling or '',
                'pifa': pifa or '',
                'pinpai': pinpai or '',
                'start': start or '',
                'end': end or '',
                'creater': creater or '',
                'sku_name': sku_name or '',
            })
        }
        # 控制扩展显示和隐藏
        if spread == 'false':
            spread =False
        else:
            spread = True
        # 条件查询form参数返回
        url_query_data = {
            'suppiler_val':suppiler_val,
            'dingwei_val':dingwei_val,
            'chargers':chargers,
            'suppliers':suppliers,
            'dingweis':dingweis,
            'code':code,
            'name':name,
            'sku_name':sku_name,
            'pinlei':pinlei,
            'start':start,
            'end':end,
            'spread':spread,
            'jibie':jibie,
            'shiling':shiling,
            'pifa':pifa,
            'creater':int(creater),
            'pinpai':int(pinpai),
            'base_domain':QINIU_BASE_DOMAIN,
        }
        page_data = get_pagination_data(paginator,page_obj)
        context.update(page_data)
        context.update(url_query_data)
        return render(request,'select/product/product_s_l_new.html',context=context)


@method_decorator(csrf_exempt, name='dispatch')
class CpmProductSelectListAddSKUEdit(LoginRequiredMixin,View):
    '''进入产品详情页面添加sku'''
    def get(self,request):
        pid = request.GET.get('pid','')
        good = get_object_or_404(Good,pk=int(pid))

        setattr(good,'suppliers',good.suppiler.all())
        setattr(good,'chargers',good.charger.all())
        setattr(good,'dingweis',good.dingwei.all())
        setattr(good,'changjings',good.changjing.all())
        skus = GoodsSku.objects.filter(sku_good = good)
        for sku in skus:
            if not sku.sku_image.startswith('http'):
                sku.sku_image = QINIU_BASE_DOMAIN + sku.sku_image
            sku.price_jin = sku.price_jin / 100
            sku.price_sale = sku.price_sale / 100
            sku.price_pifa = sku.price_pifa / 100
            if sku.price_is_limit:
                sku.price_is_limit = '是'
            else:
                sku.price_is_limit = '否'
                
        context = {
            'add_sku':True,
            'msg':'创建新品',
            'good':good,
            'skus':skus,
            'base_domain':QINIU_BASE_DOMAIN
        }
        return render(request,'select/product/product_s_l_as_detail.html',context=context)

    @transaction.atomic
    def post(self,request):
        pid = request.POST.get('pid','')
        sku_code = request.POST.get('sku-code','')
        sku_bar_code = request.POST.get('sku_bar_code','')
        sku_name = request.POST.get('sku-name','')
        length = request.POST.get('sku-len','')
        width = request.POST.get('sku-wid','')
        height = request.POST.get('sku-hei','')
        weight = request.POST.get('sku-wei','')

        price_jin = request.POST.get('price_jin','0')
        price_sale = request.POST.get('price_sale','0')
        price_pifa = request.POST.get('price_pifa','0')

        price_is_limit = request.POST.get('price_is_limit','false')
        if price_is_limit == 'false':
            price_is_limit = False
        elif price_is_limit == 'true':
            price_is_limit = True
        quality = request.POST.get('quality','0')
        number_box = request.POST.get('number_box','0')
        date_market = request.POST.get('date_market')  # ['2019/09/08']

        
        p_cycle = request.POST.get('p_cycle','0')
        desc = request.POST.get('desc','')
        sku_image = request.FILES.get('sku-img')
        if not sku_image:
            return JsonResponse({'code':'12','msg':'请上传sku图片'})

        try:
            save_id = transaction.savepoint()
            # 保存good_sku
            try:
                good = Good.objects.get(pk=int(pid))
            except Exception as err1:
                print(err1)
                return JsonResponse({'code':'3','msg':'处理失败,请正确操作'})
            # 校验sku_code是否重复
            is_exist = GoodsSku.objects.filter(sku_good=good,sku_code=sku_code).first()
            if is_exist:
                return JsonResponse({'code':'5','msg':'sku编码已经存在,请重试'})
            # 创建了第一个sku时候更新good状态
            exist_sku = GoodsSku.objects.filter(sku_good=good).first()
            if not exist_sku:
                good.state_caigou = 3
                good.state_paishe = 7
                good.state_raw = 3


            good_sku = GoodsSku.objects.create(
                sku_good = good,
                sku_code = sku_code,
                sku_bar_code = sku_bar_code,
                sku_name = sku_name,
                length = length,
                width = width,
                height = height,
                weight = weight,
                price_jin = int(float(price_jin)*100),
                price_sale = int(float(price_sale)*100),
                price_pifa = int(float(price_pifa)*100),

                quality = quality,
                number_box = number_box,
                p_cycle = p_cycle,
                desc = desc,
                price_is_limit = price_is_limit,
                date_market = datetime.strptime(date_market,'%Y/%m/%d').date(),
            )
            # 重新定义图片的名称
            img_key = self.get_image_filename(sku_image,good,sku_code)
            good_sku.sku_image = img_key
            #  存储图片到七牛云 同时存储 sku_img key
            ret = self.save_image(img_key,sku_image)
            if not ret:
                transaction.savepoint_rollback(save_id)
                return JsonResponse({'code':'5','msg':'处理失败,请重试'})

            # 存储到百度
            self.save_image_to_baidu(img_key,good,good_sku)
            good_sku.save()
            good.save()
            transaction.savepoint_commit(save_id)
        except Exception as err:
            print(err)
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'code':'4','msg':'处理失败,请重试'})
        return JsonResponse({'code':'0','msg':'ok','url':'/select/add_sku_detail/?pid='+pid})

    def save_image_to_baidu(self,img_key,good,sku):
        '''存到百度用于图像识别'''
        print('存到百度用于图像识别')
        b = BaiduImageSearch()
        b.upload('/tmp/'+img_key,good.id,sku.id)
        print('over')



    def get_image_filename(self,sku_image,good,sku_code):
        img_name = sku_image.name
        ext_name = img_name.split('.')[-1]
        file_name = str(datetime.now().timestamp())+'-'+str(good.code) +'-'+ sku_code + '.' + ext_name
        return file_name

    def save_image(self,img_key,sku_image):
        import os
        file_path_name = os.path.join('/tmp',img_key)
        with open('/tmp/'+img_key, 'wb+') as f:
            for chunk in sku_image.chunks():
                f.write(chunk)  
        # 调用七牛存储
        from utils.qiniu_util import QiniuStorage
        res = QiniuStorage().get_qiniu_auth(img_key)
        return res

@method_decorator(csrf_exempt, name='dispatch')
class CpmProductEditGoodsSku(LoginRequiredMixin,View):
    '''编辑一个sku'''
    def get(self,request):
        sid = request.GET.get('sid','')
        try:
            sku = GoodsSku.objects.filter(id=int(sid))
            return JsonResponse({'sku':serializers.serialize('json',sku),'code':'0'})
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'err'})

    @transaction.atomic
    def post(self,request):
        sku_id = request.POST.get('sku-id','')
        good_id = request.POST.get('good-id','')
        sku_code = request.POST.get('sku-code','')
        sku_bar_code = request.POST.get('sku_bar_code','')
        sku_name = request.POST.get('sku-name','')
        length = request.POST.get('sku-len','')
        width = request.POST.get('sku-wid','')
        height = request.POST.get('sku-hei','')
        weight = request.POST.get('sku-wei','')

        price_jin = request.POST.get('price_jin','0')
        price_sale = request.POST.get('price_sale','0')
        price_pifa = request.POST.get('price_pifa','0')
        price_is_limit = request.POST.get('price_is_limit','false')
        if price_is_limit == 'false':
            price_is_limit = False
        elif price_is_limit == 'true':
            price_is_limit = True
        quality = request.POST.get('quality')
        number_box = request.POST.get('number_box')
        date_market = request.POST.get('date_market')  # ['2019/09/08']

        p_cycle = request.POST.get('p_cycle','')
        desc = request.POST.get('desc','')
        sku_image = request.FILES.get('sku-img')
        try:
            save_id = transaction.savepoint()
            try:
                good = Good.objects.get(pk=int(good_id))
            except Exception as err1:
                print(err1)
                return JsonResponse({'code':'6','msg':'处理失败,请正确操作'})
            try:
                sku = GoodsSku.objects.get(id=int(sku_id))
                old_img_key = sku.sku_image
            except Exception as e2:
                print(e2)
                return JsonResponse({'code':'7','msg':'处理失败,请正确操作'})
            # 更新信息
            sku.sku_bar_code = sku_bar_code
            sku.sku_name = sku_name
            sku.length = length
            sku.width = width
            sku.height = height
            sku.weight = weight
            sku.price_jin = int(float(price_jin)*100)
            sku.price_sale = int(float(price_sale)*100)
            sku.price_pifa = int(float(price_pifa)*100)

            sku.quality = int(quality)
            sku.number_box = int(number_box)
            sku.p_cycle = p_cycle
            sku.desc = desc
            sku.price_is_limit = price_is_limit
            sku.date_market = datetime.strptime(date_market,'%Y/%m/%d').date()
            # 判断是否更新了图片
            if sku_image:
                # 重新定义图片的名称
                img_key = self.get_image_filename(sku_image,good,sku_code)
                sku.sku_image = img_key
                #  存储图片到七牛云 同时存储 sku_img key
                ret = self.save_image(img_key,sku_image)
                # 先删除百度原有的图片 然后再存储到百度
                if not ret:
                    transaction.savepoint_rollback(save_id)
                    return JsonResponse({'code':'5','msg':'处理失败,请重试'})

                self.save_image_to_baidu(img_key,good,sku,old_img_key)
            sku.save()
            transaction.savepoint_commit(save_id)
        except Exception as err:
            print(err)
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'code':'4','msg':'处理失败,请重试'})
        return JsonResponse({'code':'0','msg':'ok','url':'/select/add_sku_detail/?pid='+good_id})

    def save_image_to_baidu(self,img_key,good,sku,old_img_key):
        '''存到百度用于图像识别'''
        print('存到百度用于图像识别')
        b = BaiduImageSearch()
        # 先删除
        b.delete(old_img_key)
        # 在上传新的
        b.upload('/tmp/'+img_key,good.id,sku.id)
        print('over')

    def get_image_filename(self,sku_image,good,sku_code):
        img_name = sku_image.name
        ext_name = img_name.split('.')[-1]
        file_name = str(datetime.now().timestamp())+'-'+str(good.code) +'-'+ sku_code + '.' + ext_name
        return file_name

    def save_image(self,img_key,sku_image):
        import os
        file_path_name = os.path.join('/tmp',img_key)
        with open('/tmp/'+img_key, 'wb+') as f:
            for chunk in sku_image.chunks():
                f.write(chunk)  
        # 调用七牛存储
        from utils.qiniu_util import QiniuStorage
        res = QiniuStorage().get_qiniu_auth(img_key)

    def delete(self,request):
        '''删除sku'''
        delete = QueryDict(request.body)
        sku_id = delete.get('sku_id')
        good_id = delete.get('good_id')

        # 关联查询是否已经采购或者拍摄了
        try:
            sku = GoodsSku.objects.get(pk=int(sku_id))
            good = Good.objects.get(pk=int(good_id))
            if len(good.goods_buy_good.all()) > 0 or len(good.goods_detail_good.all()) > 0:
                return JsonResponse({'code':'6','msg':'该产品已经进行采购或者拍摄,无法删除sku'})

            old_img_key = sku.sku_image
            b = BaiduImageSearch()
            # 删除百度中存的图片
            b.delete(old_img_key)
            sku.delete()
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'删除失败！请正确操作！'})
        return JsonResponse({'code':'0','msg':'ok','url':'/select/add_sku_detail/?pid='+good_id})
        