from rest_framework import serializers

from directory.models import FileInfo


class FileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileInfo
        fields = '__all__'
