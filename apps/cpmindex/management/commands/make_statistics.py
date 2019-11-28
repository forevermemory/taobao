from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.models import Avg,Count,Sum,Max,Min

from datetime import datetime,timedelta
import time
from cpm.settings import GOOD_RUKU_EXPIRE_TIME,GOOD_MGZZ_EXPIRE_TIME
from cpm.models import Good,IndexHistory,GoodsPurchasePhase,GoodsYanhuoPhase,GoodsPhotoStartPhase,GoodsMGZZPhase


class Command(BaseCommand):
    '''预定为每天晚上 11:50执行'''
    success_msg = '执行cpm统计首页数据成功,当前日期为--%s' % datetime.date(datetime.now())
    commond = '/home/deploy/.local/share/virtualenvs/cpm-NXD7Laz8/bin/python3.8 /home/deploy/apps/cpm/manage.py make_statistics >>/home/deploy/cpm/logging.log 2>&1'
    c2 = "50 23 * * * /bin/bash -l -c '/home/deploy/.local/share/virtualenvs/cpm-NXD7Laz8/bin/python3.8 /home/deploy/apps/cpm/manage.py make_statistics >>/home/deploy/apps/log/cpm.log 2>&1'"

    def handle(self, *args, **options):

        goods = Good.objects.all()

        # 上新准备总览 待采购 待入库 待拍摄 待制作 待上架
        caigou = goods.filter(state_caigou=3)
        ruku = goods.filter(state_caigou=6)
        paishe = goods.filter(state_paishe=7)
        zhizuo = goods.filter(state_paishe=9)
        shangjia = goods.filter(state_sale=10)

        # 销售总览 已上架 待淘汰 待封存 已封存 已退市

        shangjia_done = goods.filter(state_sale=11)
        taotai = goods.filter(state_sale=12)
        fengcun = goods.filter(state_sale=11)
        fengcun_done = goods.filter(state_sale=15)
        tuishi_done = goods.filter(state_sale=13)


        # 超期查询
        caigou_exceed = []
        for good in goods:
            order = GoodsPurchasePhase.objects.filter(good=good).filter(good__state_caigou=4).first()
            if order:
                if not self.compute_caigou_exceed(order.expected_data):
                    caigou_exceed.append(good)
                    
        ruku_exceed = []
        for good in goods:
            order = GoodsYanhuoPhase.objects.filter(good=good).filter(good__state_caigou=6).order_by('-created_at').first()
            if order:
                if not self.compute_ruku_exceed(order.created_at):
                    ruku_exceed.append(good)

        paishe_exceed = []
        for good in goods:
            order = GoodsPhotoStartPhase.objects.filter(good = good).filter(good__state_paishe = 8).order_by('-created_at').first()
            if order:
                if not self.compute_caigou_exceed(order.kuaidi_edate):
                    paishe_exceed.append(good)

        zhizuo_exceed = []
        for good in goods:
            order = GoodsMGZZPhase.objects.filter(good = good).order_by('-created_at').filter(good__state_paishe = 9).first()
            if order:
                if not self.compute_zhizuo_exceed(order.mk_date):
                    zhizuo_exceed.append(good)

        now_date = datetime.today().date()
        IndexHistory.objects.create(
            date = now_date,
            caigou = len(caigou),
            ruku = len(ruku),
            paishe = len(paishe),
            zhizuo = len(zhizuo),
            shangjia = len(shangjia),
            shangjia_done = len(shangjia_done),
            taotai = len(taotai),
            fengcun = len(fengcun),
            fengcun_done = len(fengcun_done),
            tuishi_done = len(tuishi_done),
            caigou_exceed = len(caigou_exceed),
            ruku_exceed = len(ruku_exceed),
            paishe_exceed = len(paishe_exceed),
            zhizuo_exceed = len(zhizuo_exceed),
        )

        print('------------'+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'---------------------')
        self.stdout.write(self.style.SUCCESS(self.success_msg))

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
