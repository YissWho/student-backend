from rest_framework import serializers
from ..models import Notice

class NoticeSerializer(serializers.ModelSerializer):
    """通知序列化器"""
    teacher_name = serializers.CharField(
        source='teacher.username',
        read_only=True,
        help_text="发布通知的教师姓名"
    )
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S",
        read_only=True,
        help_text="通知创建时间"
    )
    is_read = serializers.SerializerMethodField(
        help_text="通知是否已读"
    )

    class Meta:
        model = Notice
        fields = ['id', 'title', 'content', 'teacher_name', 'created_at', 'is_read']
        read_only_fields = ['id', 'title', 'content', 'teacher_name', 'created_at']

    def get_is_read(self, obj):
        student = self.context.get('student')
        if student:
            return student.read_notices.filter(id=obj.id).exists()
        return False