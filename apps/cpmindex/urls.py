from django.urls import path
from . import views

app_name = 'cpmindex'

urlpatterns = [
    path('', views.CpmIndexView.as_view(), name='index'),
    path('query/', views.CpmIndexCommonQueryView.as_view(), name='query'),
    path('get_caigou_echart/',views.CpmGetEchartDataView.as_view(),name="get_caigou_echart"),

]




# from utils.redis_util import get_redis_conn
# conn = get_redis_conn()
# conn.expire()