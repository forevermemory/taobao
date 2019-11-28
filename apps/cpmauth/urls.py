from django.urls import path
from . import views


app_name = 'cpmauth'

urlpatterns = [
    path('group/', views.CpmGroupView.as_view(), name='group'),
    path('group_edit/', views.CpmGroupEditView.as_view(), name='group_edit'),
    path('index/', views.CpmPermissionsIndexView.as_view(), name='index'),
    path('login/', views.CpmLoginView.as_view(), name='login'),
    path('logout/', views.CpmLogoutView.as_view(), name='logout'),


]
