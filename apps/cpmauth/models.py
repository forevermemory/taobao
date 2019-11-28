from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save,pre_init
from utils.base_model import BaseModel
# Create your models here.


ROLE = (
    (0, '买手'),
    (1, '运营'),
    (2, '美工'),
    (3, '仓管'),
    (4, '采购'),
    (5, '质检'),
    (6, '产品助理'),
)

# 角色
class Role(BaseModel):   # 一
    name = models.IntegerField(choices=ROLE, default=999)
    desc = models.CharField(max_length=1024)
    default_permission =models.CharField(max_length=1024)
    permission_desc =  models.CharField(max_length=1024)

# 权限
class StaffPermission(BaseModel):
    permission = models.CharField(max_length=1024)
    extension = models.ForeignKey(User,on_delete=models.CASCADE)

# 工号 first_name
# 姓名 username    first_name last_name email is_active
# 部门
# 角色 user.extension.role
# 补充权限  学历，入职日期，联系地址 常驻工作地

class UserExtension(models.Model):   # 多
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='extension')
    telephone = models.CharField(max_length=11,null=True)
    name = models.CharField(max_length=64,null=True)
    code = models.CharField(max_length=11,null=True)
    address = models.CharField(max_length=256,null=True)
    address_now = models.CharField(max_length=256,null=True)
    xueli = models.CharField(max_length=256,null=True)
    in_date = models.DateTimeField(auto_now_add=True,null=True)
    role = models.ManyToManyField(Role,related_name='user_roles')



# django的modal对象保存后，自动触发保存extension
@receiver(post_save,sender=User)
def create_user_extension(sender,instance,created,**kwargs):
    if created:
        UserExtension.objects.create(user=instance)
    else:
        instance.extension.save()






from django.db.models.signals import pre_migrate,post_migrate
from cpm.models import TagChangjing,TagDingwei
k = 0
# 初始化role表的数据
#  @receiver(post_migrate, sender=Role)
@receiver(post_migrate)
def role_init_data(sender, **kwargs):
    global k
    if k > 0:
        return
    try:
        Role.objects.get(pk=1)
        print('无需初始化基本数据')
        pass
    except Exception as err:
        Role.objects.create(name=0,desc="买手")
        Role.objects.create(name=1,desc="店铺运营")
        Role.objects.create(name=2,desc="美工")
        Role.objects.create(name=3,desc="仓库管理员")
        Role.objects.create(name=4,desc="采购")
        Role.objects.create(name=5,desc="质检员")
        Role.objects.create(name=6,desc="产品助理")
        TagDingwei.objects.create(name='日销款')
        TagDingwei.objects.create(name='利润款')
        TagDingwei.objects.create(name='流量款')
        TagDingwei.objects.create(name='活动款')
        TagDingwei.objects.create(name='形象款')

        TagChangjing.objects.create(name='旅游')
        TagChangjing.objects.create(name='学习')
        TagChangjing.objects.create(name='办公')
        print('初始化基本数据，执行完毕')
    print('执行了初始化 %s次数' % k)
    k += 1

# post_migrate.connect(role_init_data)
