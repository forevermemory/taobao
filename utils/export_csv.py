import csv
from django.http import HttpResponse
from django.utils.http import urlquote
from datetime import datetime
import os
from cpm.settings import BASE_DIR

def export_csv(file_name,rows):
    now = datetime.now().strftime('%Y年%m月%d日 %H:%M') + '.csv'
    # now = datetime.now().strftime('%Y年%m月%d日 %H:%M') 
    response = HttpResponse()
    response['Content-Type']=' application/octet-stream'  
    response['Content-Disposition'] = 'attachment;filename="%s"'%(urlquote(file_name+now))
    writer = csv.writer(response)
    for row in rows:
        writer.writerow(row)
    return response


def create_csv_file(file_name,rows):
    now ='__' + datetime.now().strftime('%Y年%m月%d日 %H:%M') + '.csv'
    absolute_path = os.path.join(BASE_DIR,'media','download','csv',file_name + now) 
    # 写入csv 文件
    with open(absolute_path,'w') as csv_file:
        writer = csv.writer(csv_file)
        for row in rows:
            writer.writerow(row)
    print('ok--------------------')
    return absolute_path