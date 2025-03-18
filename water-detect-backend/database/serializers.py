from rest_framework import serializers

from database.models import FileInfo
from database.models import StreamKeyInfo


class FileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileInfo
        fields = '__all__'
        function = '__all__'



class StreamKeyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamKeyInfo
        fields = '__all__'
        extra_kwargs = {
            'user_id': {'read_only': True},
            'create_time': {'read_only': True},
            'update_time': {'read_only': True},
            'stream_key': {'read_only': True}
        }