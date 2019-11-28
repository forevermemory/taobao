from django.shortcuts import render,redirect,reverse
from django.http import HttpResponse,JsonResponse
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User,Permission,Group


from django.contrib.auth.decorators import login_required,permission_required
'''
from django.contrib.auth.models import Permission,ContentType,Group

添加权限
方式一：直接在模型中添加
class Meta:
    permissions = [
        ('view_article','看文章的权限！')
    ]
方式二：视图中添加
def add_permission(request):
    content_type = ContentType.objects.get_for_model(Article)
    permission = Permission.objects.create(codename='black_article',name='拉黑文章',content_type=content_type)
    return HttpResponse('权限创建成功！')

'''


'''

user.user_permissions 操作权限  PermissionsMixin存放在这个类中
set(permissions)
clear() 清空所有多对多关系

# 添加或者删除一个权限
remove(permission)
add(*permissions) 同set() 

user.has_perm('front.view_article')  是否有某个app下面的某个权限
user.get_all_permissions() 获取某个用户所有权限

权限控制  没有权限则跳转到403
@permission_required(['front.add_article','front.view_article'],raise_exception=True)
def operate_permission(request):
    user = User.objects.first()
    content_type = ContentType.objects.get_for_model(Article)
    permissions = Permission.objects.filter(content_type=content_type)
    for permission in permissions:
        print(permission)
    user.user_permissions.set(permissions)
    user.save()
    # user.user_permissions.clear()
    # user.user_permissions.remove(*permissions)
    if user.has_perm('front.view_article'):
        print('这个拥有view_article权限！')
    else:
        print('这个没有view_article权限！')
    print(user.get_all_permissions())


分组
name 字段   permissions多对多关系

创建分组  给分组添加权限
group = Group.objects.create(name='运营')
content_type = ContentType.objects.get_for_model(Article)
permissions = Permission.objects.filter(content_type=content_type)
group.permissions.set(permissions)

将用户添加到分组
group = Group.objects.filter(name='运营').first()
user = User.objects.first()
user.groups.add(group)
user.save()


user.has_perm：
1. 首先判断user.permissions下有没有这个权限，如果有，就True
2. 如果user.permissions下没有这个权限，那么就会判断他所属的分组下有没有这个权限
(user.has_perms(['front.add_article','front.change_article']))

html页面中控制显示权限

{% if perms.app_name.add_user %}
    <a href="#">添加文章</a>
{% endif %}


'''