from rest_framework import serializers

from database.models import FileInfo, AnalyseFileRef
from database.models import StreamKeyInfo


class FileInfoSerializer(serializers.ModelSerializer):
    opposite_file_id = serializers.SerializerMethodField()
    is_analysed = serializers.SerializerMethodField()

    class Meta:
        model = FileInfo
        fields = '__all__'

    def get_opposite_file_id(self, obj):
        try:
            file_ref = AnalyseFileRef.objects.get(file_id=obj.id)
            return file_ref.opposite_file_id
        except AnalyseFileRef.DoesNotExist:
            return None

    def get_is_analysed(self, obj):
        try:
            file_ref = AnalyseFileRef.objects.get(file_id=obj.id)
            return file_ref.is_analysed
        except AnalyseFileRef.DoesNotExist:
            return None



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
    def validate(self, data):
        auth_type = data.get('auth_type')
        auth_user_emails = data.get('auth_user_emails')
        if auth_type == 2 and not auth_user_emails:
            raise serializers.ValidationError("当 指定范围时，邮箱列表不能为空。")
        return super().validate(data)
