from django.db import models

# Create your models here.
class Video(models.Model):
    filename = models.CharField(max_length=100, db_comment='用户上传时的文件名')
    owner = models.IntegerField(db_comment='userID')
    uid = models.CharField(max_length=4096, db_comment='url')
    type = models.SmallIntegerField(db_comment='type, 1-分析前, 2-分析后')
    correspond_id = models.IntegerField(db_comment='对应另一个videoID')
    create_time = models.DateTimeField(auto_now_add=True,null=False)
    update_time = models.DateTimeField(auto_now=True,null=False)