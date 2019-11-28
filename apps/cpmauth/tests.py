from django.test import TestCase

from datetime import datetime,timedelta
now = datetime.now()
print(datetime.now())
print(datetime.utcnow())
print(datetime.today())
print(datetime.timestamp(now))
# print(datetime.timetuple(now))
# print(datetime.utctimetuple(now))
print(datetime.date(now))  # 2019-07-22
print(datetime.time(now))  # 21:10:41.954115
print(datetime.timetz(now))  # 21:10:41.954115

print(pass_time.seconds())
# utc_now = now.astimezone(pytz.timezone("UTC"))

