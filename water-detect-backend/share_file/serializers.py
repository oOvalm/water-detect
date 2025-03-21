from rest_framework import serializers

from database.models import FileInfo
from database.serializers import FileInfoSerializer
from share_file.models import FileShare


class FileShareSerializer(serializers.ModelSerializer):
    file_info = serializers.SerializerMethodField()

    class Meta:
        model = FileShare
        fields = '__all__'

    def get_file_info(self, obj):
        try:
            file_info = FileInfo.objects.get(id=obj.file_id)
            return FileInfoSerializer(file_info).data
        except FileInfo.DoesNotExist:
            return None