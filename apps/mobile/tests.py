from django.test import TestCase
import re
result = open('/root/result.txt',errors='ignore').read()

arrs = result.split('******************************************************')

print(len(arrs))  # 5300 
for arr in arrs:
    if len(arr) >1:
        res = re.compile(r'KEY NOT FOUND').findall(arr)
        if not res:
            print(arr)