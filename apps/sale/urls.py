from django.urls import path
from . import views


app_name = 'sale'

urlpatterns = [

    path('shangjia/', views.CpmProductShangjiaView.as_view(), name='shangjia'),
    path('shangjia_edit/', views.CpmProductShangjiaEditView.as_view(), name='shangjia_edit'),

    path('get_good_sku/', views.ShangjiaQuerySkusView.as_view(), name='get_good_sku'),

    path('fengcun/', views.CpmProductFengcunView.as_view(), name='fengcun'),
    path('taotai/', views.CpmProductTaotaiView.as_view(), name='taotai'),

]
