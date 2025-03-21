from django.db import models

# Create your models here.
class FileShare(models.Model):
    file_id = models.IntegerField(verbose_name='文件ID')
    user_id = models.IntegerField(verbose_name='用户ID')
    share_code = models.CharField(max_length=512, verbose_name='分享码')
    valid_type = models.SmallIntegerField(null=True, blank=True, verbose_name='有效期类型')
    expire_time = models.DateTimeField(null=True, blank=True, verbose_name='失效时间')
    share_time = models.DateTimeField(null=True, blank=True, verbose_name='分享时间')
    code = models.CharField(max_length=5, null=True, blank=True, verbose_name='提取码')
    show_count = models.IntegerField(default=0, verbose_name='浏览次数')

    class Meta:
        db_table = 'water_detect_file_share'
        indexes = [
            models.Index(fields=['file_id'], name='idx_file_id'),
            models.Index(fields=['user_id'], name='idx_user_id'),
            models.Index(fields=['share_time'], name='idx_share_time')
        ]
        verbose_name = '分享信息'
        verbose_name_plural = verbose_name