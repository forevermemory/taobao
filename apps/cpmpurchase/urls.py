from django.urls import path
from . import views


app_name = 'purchase'

urlpatterns = [
    path('purchase/', views.CpmProductPurchaseIndex.as_view(), name='purchase'),
    path('fen_dian/', views.CpmProductFenAndDian.as_view(), name='fen_dian'),
    path('yanhuo/', views.CpmProductYanhuoView.as_view(), name='yanhuo'),
    path('ruku/', views.CpmProductRukuView.as_view(), name='ruku'),
    path('ruku_get_detail/', views.CpmProductRukuGetOneDetail.as_view(), name='ruku_get_detail'),


]
