from django.core.management.base import BaseCommand, CommandError
from django_redis import get_redis_connection
from datetime import datetime

class Command(BaseCommand):
    '''每天12点清除导出csv失败的任务'''
    commond = '/home/deploy/.local/share/virtualenvs/cpm-NXD7Laz8/bin/python3.8 /home/deploy/apps/cpm/manage.py clear_csv_error >>/home/deploy/apps/log/clear_csv_error.log 2>&1'
    c2 = "51 23 * * * /bin/bash -l -c '/home/deploy/.local/share/virtualenvs/cpm-NXD7Laz8/bin/python3.8 /home/deploy/apps/cpm/manage.py clear_csv_error >>/home/deploy/apps/log/clear_csv_error.log 2>&1'"

    def handle(self, *args, **options):
        conn = get_redis_connection()
        now_str = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        print('start clear_csv_error,current time %s' % now_str)

        length = conn.llen('csv_lists')
        export_csv_result_ = conn.hgetall('export_csv_result') # b'' 真的烦
        export_csv_result = {}
        for key in export_csv_result_:
            export_csv_result[str(key.decode())] = str(export_csv_result_[key].decode())

        item_result = [] # 当前所有导出任务的key
        for key in export_csv_result:
            if len(key.split('__')) == 1:
                item_result.append(key)

        for item in item_result:
            # 
            try:
                export_csv_result[item + '__path'] 
            except Exception as err:
                # 说明这个 任务失败了 清除相关key
                print(err)
                print(item,'error clear it')

                conn.lrem('csv_lists',0,item)
                conn.hdel('export_csv_result',item)
                conn.hdel('export_csv_result',item + '__index')
                conn.hdel('export_csv_result',item + '__now_str')
                conn.hdel('export_csv_result',item + '__path')
        print('start clear_csv_error,current time %s' % datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))