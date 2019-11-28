# Generated by Django 2.2.2 on 2019-08-30 16:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='建立时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('deleted_at', models.DateTimeField(null=True, verbose_name='删除时间')),
                ('name', models.IntegerField(choices=[(0, '买手'), (1, '运营'), (2, '美工'), (3, '仓管'), (4, '采购'), (5, '质检'), (6, '产品助理')], default=999)),
                ('desc', models.CharField(max_length=1024)),
                ('default_permission', models.CharField(max_length=1024)),
                ('permission_desc', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserExtension',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telephone', models.CharField(max_length=11, null=True)),
                ('name', models.CharField(max_length=64, null=True)),
                ('code', models.CharField(max_length=11, null=True)),
                ('address', models.CharField(max_length=256, null=True)),
                ('address_now', models.CharField(max_length=256, null=True)),
                ('xueli', models.CharField(max_length=256, null=True)),
                ('in_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('role', models.ManyToManyField(related_name='user_roles', to='cpmauth.Role')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='extension', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StaffPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='建立时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('deleted_at', models.DateTimeField(null=True, verbose_name='删除时间')),
                ('permission', models.CharField(max_length=1024)),
                ('extension', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
