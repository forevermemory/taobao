#encoding: utf-8
from django import template
# from datetime import datetime
# from django.utils.timezone import now as now_func,localtime

register = template.Library()

@register.filter
def arrival_stat(value):
    if value == 0:
        return "到货"
    elif value == 1:
        return "退回"
    elif value == 2:
        return "未到"
    elif value == 3:
        return "异常"
    else:
        return ""





