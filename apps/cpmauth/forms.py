from django import forms

from utils.forms import FormMixin
from django.contrib.auth.models import User
from django.db import models

class CpmLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class SaveChangesForm(forms.Form,FormMixin):
    pk = forms.IntegerField()
    username = forms.CharField()
    email = forms.EmailField()
    telephone = forms.CharField(max_length=11)
    role = forms.IntegerField()
    # {'pk':id,'username':username,'email':email,'telephone':telephone,'role':role}

class ResetPasswordForm(forms.Form,FormMixin):
    pk = forms.IntegerField()
    new_password = forms.CharField()
    







class RegisterForm(forms.Form,FormMixin):
    email = forms.CharField()
    role = forms.IntegerField()
    telephone = forms.CharField(max_length=11)
    username = forms.CharField()


    password1 = forms.CharField(max_length=20, min_length=6,
                               error_messages={"max_length": "密码最多不能超过20个字符！", "min_length": "密码最少不能少于6个字符！"})
    password2 = forms.CharField(max_length=20, min_length=6,
                                error_messages={"max_length": "密码最多不能超过20个字符！", "min_length": "密码最少不能少于6个字符！"})
    
    
    
    
    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()

        username = cleaned_data.get('username')
        if len(username) < 3:
            raise forms.ValidationError("Your username must be at least 3 characters long.")
        elif len(username) > 50:
            raise forms.ValidationError("Your username is too long.")
        exists = User.objects.filter(username=username).exists()
        if exists:
            raise forms.ValidationError('用户名已经存在')

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('两次密码输入不一致！')

        email = cleaned_data.get('email')
        exists = User.objects.filter(email=email).exists()
        if exists:
            raise forms.ValidationError('邮箱已经存在')



        telephone = cleaned_data.get('telephone')
        exists = User.objects.filter(extension__telephone=telephone).exists()
        if exists:
            raise forms.ValidationError('手机号码已经被注册！')

        return cleaned_data