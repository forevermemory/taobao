from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField("建立时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    deleted_at = models.DateTimeField("删除时间", null=True)

    class Meta:
        abstract = True