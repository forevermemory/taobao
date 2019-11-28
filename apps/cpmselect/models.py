from django.db import models
# from utils.base_model import BaseModel
# Create your models here.

class ImageUploadModel(models.Model):
    image = models.ImageField(upload_to="%Y/%m/%d/")

    # 重写上传保存的文件扩展名
    def generate_filename(self, instance, filename):
        if callable(self.upload_to):
            filename = self.upload_to(instance, filename)
            print('aaa')
            print('aaa')
            print('aaa')
        else:
            dirname = datetime.datetime.now().strftime(self.upload_to)
            filename = posixpath.join(dirname, filename)
        return self.storage.generate_filename(filename)





    