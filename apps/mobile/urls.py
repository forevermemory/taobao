from django.urls import path
from . import views


app_name = 'mobile'

urlpatterns = [

    path('', views.MobileIndexView.as_view(), name='index'),
    path('image/', views.MobileImageSearchView.as_view(), name='image'),
    path('query/', views.MobileQueryView.as_view(), name='query'),
    path('login/', views.MobileLoginView.as_view(), name='login'),


]
