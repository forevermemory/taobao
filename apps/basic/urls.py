from django.urls import path
from . import views


app_name = 'basic'

urlpatterns = [
    path('index/', views.BasicIndexView.as_view(), name='index'),

    path('changjing/', views.TagChangjingView.as_view(), name='changjing'),
    path('changjing_add/', views.GoodsAddTagChangjingView.as_view(), name='changjing_add'),

    path('dingwei/', views.TagDingweiView.as_view(), name='dingwei'),
    path('dingwei_add/', views.GoodsAddTagDingweiView.as_view(), name='dingwei_add'),

    path('cpmuser/', views.AdminCpmuserView.as_view(), name='cpmuser'),
    path('cpmuser_add/', views.AdminAddCpmuserView.as_view(), name='cpmuser_add'),

    path('brand/', views.GoodsBrandView.as_view(), name='brand'),
    path('brand_add/', views.GoodsAddBrandView.as_view(), name='brand_add'),

    path('supplier/', views.SupplierView.as_view(), name='supplier'),
    path('supplier_add/', views.GoodsAddSupplierView.as_view(), name='supplier_add'),
    
    path('avenue/', views.AvenueAddView.as_view(), name='avenue'),
    path('shop/', views.ShopCrudView.as_view(), name='shop'),
    path('cate/', views.CpmCategory.as_view(), name='cate'),

    path('qiniu/', views.QiniuPicView.as_view(), name='qiniu'),
    # path('util/', views.CateUtil.as_view(), name='util'),


    path('add_multi/',views.CpmMultiAddProduct.as_view(),name="add_multi"),
    path('r/',views.CpmRewriteR.as_view(),name="r"),
    path('csv/',views.CpmExportCsvResult.as_view(),name="csv"),


]
