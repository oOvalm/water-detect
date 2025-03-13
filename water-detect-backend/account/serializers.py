import hashlib
from rest_framework import serializers
from database.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        # 计算 MD5 值
        md5_hash = hashlib.md5(password.encode()).hexdigest()
        validated_data['password'] = md5_hash
        user = User.objects.create(**validated_data)
        return user