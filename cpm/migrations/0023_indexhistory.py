# Generated by Django 2.2.2 on 2019-10-21 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpm', '0022_goodstaotaiphase_goodstuishiphase'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndexHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('caigou', models.IntegerField(default=0)),
                ('ruku', models.IntegerField(default=0)),
                ('paishe', models.IntegerField(default=0)),
                ('zhizuo', models.IntegerField(default=0)),
                ('shangjia', models.IntegerField(default=0)),
                ('shangjia_done', models.IntegerField(default=0)),
                ('taotai', models.IntegerField(default=0)),
                ('fengcun', models.IntegerField(default=0)),
                ('fengcun_done', models.IntegerField(default=0)),
                ('tuishi_done', models.IntegerField(default=0)),
            ],
        ),
    ]
