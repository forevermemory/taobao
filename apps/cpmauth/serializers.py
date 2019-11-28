from rest_framework import serializers
# pip install djangorestframework
# 
from .models import UserExtension,Role
from django.contrib.auth.models import User
# pip install djangorestframework

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id','name', 'desc')


















class UserSerializer(serializers.ModelSerializer):

    extension = UserExtensionSerializer()
    
    class Meta:
        model = User
        fields = ('pk','username', 'email', 'extension')





'''
{"model": "auth.user", "pk": 15, "fields": {"password": "pbkdf2_sha256$150000$dmK8xOr80fRM$XLqg0DDvvZ8/ISH6nt243qyuv0Lr1qQ5bdwOaK0kkH4=", "last_login": "2019-06-12T09:08:29.746Z", "is_superuser": true, "username": "admin", "first_name": "", "last_name": "", "email": "admin@admin.com", "is_staff": true, "is_active": true, "date_joined": "2019-06-12T07:35:37.235Z", "groups": [], "user_permissions": []}}, 
'''



