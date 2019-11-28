from django.urls import path
from . import views


app_name = 'photo'

urlpatterns = [
    path('start/', views.CpmProductPhotoStart.as_view(), name='start'),
    path('sysx/', views.CpmProductPhotoSYSXView.as_view(), name='sysx'),
    
    path('mgzz/', views.CpmProductMeiGongZhiZuoView.as_view(), name='mgzz'),
    path('mgzz_fenpei/', views.CpmProductMGZZFenpeiView.as_view(), name='mgzz_fenpei'),


]
