from django.contrib import admin





from .models import Role


# 方式一
# class RoleAdmin(admin.ModelAdmin):
#     list_per_page = 10
#     list_display = ['id','name','desc']

# admin.site.register(Role, RoleAdmin)

# 方式二

'''
@admin.register(Role)
class AuthorAdmin(admin.ModelAdmin):
    list_per_page = 10
    # list_display = ['id','name','desc']  列表和元组都可以
    list_display = ('id','name','desc')




@admin.register(GoodsInfo)
class GoodsInfoAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ('goods_code','goods_name','arrival_stat')

    # list_filter = ('goods_name', ) # 右侧边栏中的过滤器
    list_select_related = True
'''