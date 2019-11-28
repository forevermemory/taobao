from django.db import models
from django.core import validators
from django.contrib.auth.models import User

from utils.base_model import BaseModel


GOODS_ARRIVAL_STAT = (
    (0, '正常到货'),
    (1, '异常到货'),
    (2, '未到'),
    (3, '超期'),

)


GOODS_MATERIAL_STAT= (
    (0, '用供货商图片'),
    (1, '寄出'),
)

GOODS_SALES_STAT = (
    (0, '未上架'),
    (1, '已上架'),
)

GOODS_STAT = (
    (0, '待评审'),
    (1, '待创建新品'),
    (2, '终止'),
    (3, '待采购'),
    (4, '待分货点货'),
    (5, '待验货'),
    (6, '待入库'),
    (7, '待拍摄'),
    (8, '拍摄中'),
    (9, '待制作'),
    (10, '待上架'),
    (11, '已上架'),
    (12, '待淘汰'),
    (13, '退市'),
    (14, '待封存'),
    (15, '待启封'),
)

# 渠道  code 10-99  name
class Avenue(BaseModel):
    code = models.IntegerField(unique=True,null=True)
    name = models.CharField(null=True,max_length=128)

# 店铺
class Shop(BaseModel):
    avenue = models.ForeignKey(Avenue, related_name='avenue_shops', on_delete=models.SET_NULL, null=True)
    code = models.IntegerField(null=True) # 100-999
    name = models.CharField(null=True,max_length=256)
    sub_name = models.CharField(null=True,max_length=8)
    link = models.CharField(null=True,max_length=1024)
    # 和 sku 形成多对多关系 在sku那边负责维护外键会方便一些



# 品类 对产品的类别定义，本系统采用阿里巴巴的品类定义体系
class Category(models.Model):
    cid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=2048)

    is_parent = models.IntegerField(default=0)
    parent_id = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    pathid = models.CharField(max_length=2048,null=True)
    path = models.CharField(max_length=2048,null=True)
    class Meta:
        db_table = 'wp_ex_source_goods_tb_cat_copy'
        unique_together = (("cid",),)  # unique索引,((里面有多个就是联合unique索引))
        indexes = [
            # models.Index(fields=['cid']),
            models.Index(fields=['parent_id']), # 普通索引
            models.Index(fields=['level']),
        ]

# 品牌库
class GoodsBrand(BaseModel):
    code = models.CharField(max_length=32,null=True)  # 00001 -99999　我生成
    name = models.CharField(max_length=64,null=True) 



# 供应商
class Supplier(BaseModel):
    code = models.CharField(max_length=64)  # 0001-9999 用户填写
    name = models.CharField(max_length=64)
    concat = models.CharField(max_length=64)
    address = models.CharField(max_length=1024)
    phone = models.CharField(max_length=32)
    telephone = models.CharField(max_length=32)
    email = models.CharField(max_length=64)
    note = models.CharField(max_length=1024)


# 标签 中的 定位 TagDingwei  运营维护　
class TagDingwei(BaseModel):
    '''
    日销款(default)　形象款，活动款，流量款，利润款，
    '''
    name = models.CharField(max_length=32)

# 标签 中的 场景TagChangjing  运营维护　
class TagChangjing(BaseModel):
    name = models.CharField(max_length=32)


GOODS_SHILING = (
    (0,'常规'),
    (1,'冬季'),
    (2,'夏季'),
)
GOODS_JIBIE = (
    (0,'普通'),
    (1,'核心'),
    (2,'重点'),
)
GOODS_PIFA = (
    (0,'不可批发'),
    (1,'可批发'),
)

# 产品上架多个店铺的不同状态
# 淘汰　所有全部淘汰才算淘汰
# ******************产品*******************
class Good(BaseModel):

    hcode = models.CharField(max_length=16,default='')  # 参考erp　预编码 h19001 
    code = models.CharField(max_length=16,default='')  # 新品 19001  我校验是否重复
    name = models.CharField(max_length=1024)
    creater = models.ForeignKey(User, related_name='goods_creater', on_delete=models.SET_NULL, null=True)
    cate = models.ForeignKey(Category, related_name='goods_cate', on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(GoodsBrand, related_name='goods_brand', on_delete=models.SET_NULL, null=True)

    charger = models.ManyToManyField(User, related_name='goods_charger')
    suppiler = models.ManyToManyField(Supplier, related_name='goods_suppiler')

    shiling = models.IntegerField(choices=GOODS_SHILING)# 时令
    jibie = models.IntegerField(choices=GOODS_JIBIE,default=0) # 级别
    pifa = models.IntegerField(choices=GOODS_PIFA,default=0)  # false 不可批发　
    dingwei = models.ManyToManyField(TagDingwei,related_name='dingweis') # 定位
    changjing = models.ManyToManyField(TagChangjing,related_name='changjings') # 场景　后期多选

    state_caigou = models.IntegerField(choices=GOODS_STAT,default=0) # 用于记录采购阶段
    state_paishe = models.IntegerField(choices=GOODS_STAT,default=0) # 用于记录拍摄制作阶段
    state_sale = models.IntegerField(choices=GOODS_STAT,default=0) # 用于记录上架销售
    state_raw = models.IntegerField(choices=GOODS_STAT,default=0)# 用于记录后面上架销售阶段
    desc = models.TextField(null=True,default='')

    is_first_shangjia = models.BooleanField(default=True) # 是否是第一次上架
    is_multi_export = models.BooleanField(default=False)  # 判断是不是批量导入的 1 可以显示上架



# SKU 信息  与商品 1  --> 多 sku
class GoodsSku(BaseModel):
    sku_good = models.ForeignKey(Good,related_name='goods_skus', on_delete=models.SET_NULL, null=True)
    sku_code = models.CharField(max_length=32,default='') # 必须
    sku_bar_code = models.CharField(max_length=64,null=True)
    sku_name = models.CharField(max_length=128,default='') # 必须
    sku_image = models.CharField(max_length=256,default='') # 必须

    length = models.CharField(null=True,max_length=32) # 必须
    width = models.CharField(null=True,max_length=32) # 必须
    height = models.CharField(null=True,max_length=32) # 必须
    weight = models.CharField(null=True,max_length=32) # 必须

    price_jin = models.IntegerField(default=0) # 必须 进货价(元)
    price_sale = models.IntegerField(default=0) # 建议零售价
    price_pifa = models.IntegerField(default=0) # 批发价
    price_is_limit = models.BooleanField(default=False) # 必须 是否限价
    quality = models.IntegerField(default=0) # 保质期（天
    number_box = models.IntegerField(default=0) # 装箱数
    date_market = models.DateTimeField(null=True) # 上市日期
    p_cycle = models.CharField(null=True,max_length=64,default='0') # 采购周期
    desc = models.CharField(null=True,max_length=1024,default='')



#
# 选品阶段select phase  
class GoodsSelectPhase(BaseModel):
    is_change_charger = models.BooleanField(default=False)
    charger = models.ForeignKey(User, related_name='goods_select_charger', on_delete=models.SET_NULL, null=True)
    
    good = models.ForeignKey(Good, on_delete=models.SET_NULL, null=True)

# 出现供应商增加，删除，修改等情况,用做备查
class SupplierChange(BaseModel):
    good = models.ForeignKey(Good,related_name='goods_supplier_change',on_delete=models.SET_NULL,null=True)
    raw_supplier = models.ManyToManyField(Supplier, related_name='goods_supplier_raw_supplier', )
    now_supplier = models.ManyToManyField(Supplier, related_name='goods_supplier_now_supplier', )

# 出现负责人增加，删除，修改等情况,用做备查
class ChargerChange(BaseModel):
    good = models.ForeignKey(Good,related_name='good_charger_change',on_delete=models.SET_NULL,null=True)
    raw_charger = models.ManyToManyField(User, related_name='goods_raw_charger', )
    now_charger = models.ManyToManyField(User, related_name='goods_now_charger', )


# 同类产品过多，价格无优势，供应保障问题，上市时间问题，知识产权问题，无必要资质，其他
GOOD_PINGSHEN_CANCEL = (
    (0,'同类产品过多'),
    (1,'价格无优势'),
    (2,'供应保障问题'),
    (3,'上市时间问题'),
    (4,'知识产权问题'),
    (5,'无必要资质'),
    (6,'其他'),
)
# 待定原因：补充信息，推迟评审，其他。
GOOD_PINGSHEN_WAIT = (
    (0,'补充信息'),
    (1,'推迟评审'),
    (2,'其他'),
)
# 评审阶段 记录评审人
class GoodsPingshenPhase(BaseModel):
    good = models.ForeignKey(Good, related_name='goods_pingshen_phase', on_delete=models.SET_NULL, null=True)
    pingshener = models.ForeignKey(User, related_name='goods_pingshen_charger', on_delete=models.SET_NULL, null=True)
    cancel = models.IntegerField(choices=GOOD_PINGSHEN_CANCEL,null=True)
    wait = models.IntegerField(choices=GOOD_PINGSHEN_WAIT,null=True)
    desc = models.CharField(null=True,max_length=1024)




#  采购人	  采购日期   预计到货日期	入库日期
class GoodsPurchasePhase(BaseModel):
    good = models.ForeignKey(Good, related_name='goods_buy_good', on_delete=models.SET_NULL, null=True)
    operator = models.ForeignKey(User, related_name='goods_buy_operator', on_delete=models.SET_NULL, null=True)
    buyer = models.ForeignKey(User, related_name='goods_buy_buyer', on_delete=models.SET_NULL, null=True)
    purchase_date = models.DateTimeField(null=True)
    expected_data = models.DateTimeField(null=True)
    state_caigou = models.IntegerField(choices=GOODS_STAT,default=4) # 用于记录采购阶段
    desc = models.CharField(null=True,max_length=1024)





# 入库相关属性   到货状态	到货情况描述	到货日期	到货检查	检查结果描述
# 到货检查
GOODS_EXCEPT_DETAIL = (
    (0, '正常'),
    (1, '缺货'),
    (2, '发错货'),
    (3, '其他'),
)
GOODS_EXCEPT_DEAL = (
    (0,'退货退款'),
    (1,'供应商补发货/换货'),
    (2,'品质问题可接受'),
    (3,'其他方式'),
)


class GoodsDianAndFenPhase(BaseModel):
    
    good = models.ForeignKey(Good, related_name='goods_dian_fen', on_delete=models.SET_NULL, null=True)
    operator = models.ForeignKey(User, related_name='goods_fen_dian_operator', on_delete=models.SET_NULL, null=True)
    charger = models.ForeignKey(User, related_name='goods_fen_dian_charger', on_delete=models.SET_NULL, null=True)
    state = models.IntegerField(choices=GOODS_EXCEPT_DETAIL,default=0)
    desc = models.CharField(null=True,max_length=1024)
    real_arrival_date = models.DateTimeField(null=True)    

    # 目前不关联该商品的采购订单 一件产品只考虑采购一次

GOODS_DETAIL_TYPE = (
    (0, '上新'),
    (1, '翻新'),
)
GOODS_PAISHE_TYPE = (
    (0, '外部拍摄'),
    (1, '内部拍摄'),
)
# 验货
GOODS_YANHUO_RESULT = (
    (0, '合格'),
    (1, '不合格'),
    (2, '其他'),

)


# 验货
class GoodsYanhuoPhase(BaseModel):
    good = models.ForeignKey(Good, related_name='goods_yanhuo_good', on_delete=models.SET_NULL, null=True)
    operator = models.ForeignKey(User, related_name='goods_yanhuo_operator', on_delete=models.SET_NULL, null=True)
    charger = models.ForeignKey(User, related_name='goods_yanhuo_charger', on_delete=models.SET_NULL, null=True)
    result = models.IntegerField(choices=GOODS_YANHUO_RESULT)
    video = models.CharField(null=True,max_length=256)
    images = models.CharField(null=True,max_length=2048)
    desc = models.CharField(null=True,max_length=1024)

# 入库

GOODS_STORAGE_STATE = (
    (0, '入库'),
    (1, '退货退款'),
    (2, '补货换货'),
)
class GoodRukuPhase(BaseModel):
    good = models.ForeignKey(Good, related_name='goods_ruku_good', on_delete=models.SET_NULL, null=True)
    operator = models.ForeignKey(User, related_name='goods_ruku_operator', on_delete=models.SET_NULL, null=True)
    charger = models.ForeignKey(User, related_name='goods_ruku_charger', on_delete=models.SET_NULL, null=True)
    result = models.IntegerField(choices=GOODS_STORAGE_STATE)
    desc = models.CharField(null=True,max_length=1024)



# 产品拍摄准备
class GoodsPhotoStartPhase(BaseModel):
    good = models.ForeignKey(Good, related_name='goods_detail_good', on_delete=models.SET_NULL, null=True)
    operator = models.ForeignKey(User, related_name='goods_detail_operator', on_delete=models.SET_NULL, null=True)
    photo_genzonger = models.ForeignKey(User, related_name='goods_detail_genzonger', on_delete=models.SET_NULL, null=True)
    detail_type = models.IntegerField(choices=GOODS_DETAIL_TYPE, default=0)
    good_photo_method = models.IntegerField(choices=GOODS_PAISHE_TYPE)

    # 快递
    kuaidi_sender = models.ForeignKey(User, related_name='goods_detail_kuaidi_sender', on_delete=models.SET_NULL, null=True)
    kuaidi_name = models.CharField(max_length=64,null=True)
    kuaidi_code = models.CharField(max_length=128,null=True)
    kuaidi_jdate = models.DateTimeField(null=True)
    kuaidi_edate = models.DateTimeField(null=True)
    is_need_jisong = models.BooleanField(default=False)
    desc = models.CharField(null=True,max_length=1024)

# 产品不拍摄直接进入产品进入待制作状态。 记录操作人和时间
class GoodsNotPhotoToMakingPhase(BaseModel):
    good = models.ForeignKey(Good, related_name='goods_not_photo', on_delete=models.SET_NULL, null=True)
    operator = models.ForeignKey(User, related_name='goods_not_photo_operator', on_delete=models.SET_NULL, null=True)

# 摄影摄像后 进行交付记录
class GoodsSYSXingAndFinishPhase(BaseModel):
    good = models.ForeignKey(Good, related_name='goods_sysx_phase', on_delete=models.SET_NULL, null=True)
    operator = models.ForeignKey(User, related_name='goods_sysx_operator', on_delete=models.SET_NULL, null=True)
    photo_start = models.OneToOneField(GoodsPhotoStartPhase, related_name='goods_sysx_photo_start', on_delete=models.SET_NULL, null=True)

    real_date = models.DateTimeField(null=True)
    desc = models.CharField(null=True,max_length=1024)


# 美工制作阶段
GOOD_MEIGONG_MK_STATE = (
    (0, '未分配'),
    (1, '已分配'),
    (2, '待审核'),
    (3, '制作完成'),
)
GOOD_MEIGONG_CHECK = (
    (0, '通过'),
    (1, '不通过'),
)
class GoodsMGZZPhase(BaseModel):
    good = models.ForeignKey(Good, related_name='goods_mgzz_phase', on_delete=models.SET_NULL, null=True)

    # 点击分配
    mk_operator = models.ForeignKey(User, related_name='goods_mgzz_mk_operator', on_delete=models.SET_NULL, null=True)
    mk_to = models.ForeignKey(User, related_name='goods_mgzz_mk_to', on_delete=models.SET_NULL, null=True)
    mk_state = models.IntegerField(choices=GOOD_MEIGONG_MK_STATE,default=0)
    mk_date = models.DateTimeField(null=True)
    mk_desc = models.CharField(null=True,max_length=1024)
    # 提交
    submit_operator = models.ForeignKey(User, related_name='goods_mgzz_submit_operator', on_delete=models.SET_NULL, null=True)
    submit_date = models.DateTimeField(null=True)

class GoodsMGZZCheckDetail(BaseModel):
    # 审核 与mgzz形成一对多 会出现多次审核的记录
    mgzz = models.ForeignKey(GoodsMGZZPhase, related_name='mgzz_tetail', on_delete=models.SET_NULL, null=True)
    check_operator = models.ForeignKey(User, related_name='goods_mgzz_check_detail_operator', on_delete=models.SET_NULL, null=True)
    check_state = models.IntegerField(choices=GOOD_MEIGONG_CHECK)
    check_desc = models.CharField(null=True,max_length=1024)



# sku和店铺的关联关系 和销售阶段的状态变更都是用这个表
class SkuToShop(BaseModel):
    sku = models.ForeignKey(GoodsSku, related_name='sku2shop_sku', on_delete=models.SET_NULL, null=True)
    shop = models.ForeignKey(Shop, related_name='sku2shop_shop', on_delete=models.SET_NULL, null=True)
    sku_in_shop_state = models.IntegerField(choices=GOODS_STAT,default=10)# 用于记录sku在店铺中的销售状态



# 上架阶段 
class GoodsShangjiaPhase(BaseModel):
    operator = models.ForeignKey(User, related_name='goods_shangjia_operator', on_delete=models.SET_NULL, null=True)
    good = models.ForeignKey(Good, related_name='goods_shangjia_sku', on_delete=models.SET_NULL, null=True)
    shangjia_times = models.IntegerField(default=1) # 累计上架次数


GOOD_FENGCUN_STATE = (
    (11, '已上架'),
    (15, '待启封'),
)
# 记录封存 
class GoodsFengcunPhase(BaseModel):
    operator = models.ForeignKey(User, related_name='goods_fengcun_operator', on_delete=models.SET_NULL, null=True)
    good = models.ForeignKey(Good, related_name='goods_fengcun_sku', on_delete=models.SET_NULL, null=True)

# 记录启封
class GoodsQifenPhase(BaseModel):
    operator = models.ForeignKey(User, related_name='goods_qifeng_operator', on_delete=models.SET_NULL, null=True)
    good = models.ForeignKey(Good, related_name='goods_qifeng_sku', on_delete=models.SET_NULL, null=True)


GOOD_TAOTAI_STATE = (
    (11, '已上架'),
    (12, '待淘汰'),
    (13, '已退市'),
)
# 记录淘汰
class GoodsTaotaiPhase(BaseModel):
    operator = models.ForeignKey(User, related_name='goods_taotai_operator', on_delete=models.SET_NULL, null=True)
    good = models.ForeignKey(Good, related_name='goods_taotai_sku', on_delete=models.SET_NULL, null=True)

# 记录退市
class GoodsTuishiPhase(BaseModel):
    operator = models.ForeignKey(User, related_name='goods_tuishi_operator', on_delete=models.SET_NULL, null=True)
    good = models.ForeignKey(Good, related_name='goods_tuishi_sku', on_delete=models.SET_NULL, null=True)



class IndexHistory(models.Model):
    '''每日生成首页报表的历史记录'''
    date = models.DateField()

    caigou = models.IntegerField(default=0)
    ruku = models.IntegerField(default=0)
    paishe = models.IntegerField(default=0)
    zhizuo = models.IntegerField(default=0)
    shangjia = models.IntegerField(default=0)

    shangjia_done = models.IntegerField(default=0)
    taotai = models.IntegerField(default=0)
    fengcun = models.IntegerField(default=0)
    fengcun_done = models.IntegerField(default=0)
    tuishi_done = models.IntegerField(default=0)

    caigou_exceed = models.IntegerField(default=0)
    ruku_exceed = models.IntegerField(default=0)
    paishe_exceed = models.IntegerField(default=0)
    zhizuo_exceed = models.IntegerField(default=0)


# 首页的上新阶段查询下拉
INDEX_SHANGXIN_ITEMS = (
    (0, '创建时间'),
    (1, '采购时间'),
    (2, '到货时间'),
    (3, '入库时间'),
    (4, '拍摄时间'),
    (5, '制作时间'),
)
# 首页的销售阶段查询下拉
INDEX_SALE_ITEMS = (
    (0, '上架时间'),
    (1, '封存时间'),
    (2, '淘汰时间'),
    (3, '退市时间'),
)





# # 自定义品类
# class CpmCategory(models.Model):
#     cid = models.IntegerField(primary_key=True)
#     name = models.CharField(max_length=2048)
#     good_nums = models.IntegerField(default=0)

#     is_parent = models.IntegerField(default=0)
#     parent_id = models.IntegerField(default=0)
#     level = models.IntegerField(default=0)  # 0 1 2 3
#     pathid = models.CharField(max_length=2048,null=True)
#     path = models.CharField(max_length=2048,null=True)
#     class Meta:
#         unique_together = (("cid",),)  # unique索引,((里面有多个就是联合unique索引))
#         indexes = [
#             models.Index(fields=['parent_id']), # 普通索引
#         ]

class SonCategory(models.Model):
    cid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=2048)
    is_parent = models.IntegerField(default=0)
    parent_id = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    pathid = models.CharField(max_length=2048,null=True)
    path = models.CharField(max_length=2048,null=True)
    class Meta:
        db_table = 't_category'
        unique_together = (("cid",),)  
        indexes = [
            models.Index(fields=['parent_id']), 
        ]





'''

    (10, '待上架'),
    (11, '已上架'),
    (12, '待淘汰'),
    (13, '退市'),  已经淘汰
    (14, '待封存'),
    (15, '待启封'),
'''