from rest_framework import serializers
from ..models import Class


class ClassSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)

    class Meta:
        model = Class
        fields = ['id', 'name', 'teacher', 'teacher_name', 'created_at']