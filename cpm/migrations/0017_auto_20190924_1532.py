# Generated by Django 2.2.2 on 2019-09-24 15:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cpm', '0016_auto_20190923_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodspingshenphase',
            name='good',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='goods_pingshen_phase', to='cpm.Good'),
        ),
        migrations.CreateModel(
            name='GoodsMGZZPhase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='建立时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('deleted_at', models.DateTimeField(null=True, verbose_name='删除时间')),
                ('mk_state', models.IntegerField(choices=[(0, '未分配'), (1, '已分配'), (2, '待审核')], default=0)),
                ('mk_date', models.DateTimeField(null=True)),
                ('mk_desc', models.CharField(max_length=1024, null=True)),
                ('submit_date', models.DateTimeField(null=True)),
                ('good', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='goods_mgzz_phase', to='cpm.Good')),
                ('mk_operator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='goods_mgzz_mk_operator', to=settings.AUTH_USER_MODEL)),
                ('mk_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='goods_mgzz_mk_to', to=settings.AUTH_USER_MODEL)),
                ('submit_operator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='goods_mgzz_submit_operator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GoodsMGZZCheckDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='建立时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('deleted_at', models.DateTimeField(null=True, verbose_name='删除时间')),
                ('check_state', models.IntegerField(choices=[(0, '通过'), (1, '不通过')])),
                ('check_desc', models.CharField(max_length=1024, null=True)),
                ('check_operator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='goods_mgzz_check_detail_operator', to=settings.AUTH_USER_MODEL)),
                ('mgzz', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mgzz_tetail', to='cpm.GoodsMGZZPhase')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
