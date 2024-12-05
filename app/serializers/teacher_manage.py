from rest_framework import serializers
from ..models import Student, Class, Notice

class StudentManageSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='classs.name', read_only=True)
    status_display = serializers.CharField(read_only=True)
    province_display = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['role', 'is_read', 'status', 'province', 
                           'study_school', 'study_major', 'created_at', 
                           'updated_at', 'read_notices']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class StudentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['student_no', 'username', 'phone', 'password', 'classs', 'avatar']
        extra_kwargs = {
            'password': {'write_only': True},
            'avatar': {'required': False}
        }

    def validate_student_no(self, value):
        # 获取当前实例（如果是更新操作）
        instance = getattr(self, 'instance', None)
        # 检查学号是否已存在，排除当前实例
        if Student.objects.filter(student_no=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("该学号已存在")
        return value

    def validate_phone(self, value):
        instance = getattr(self, 'instance', None)
        # 检查手机号是否已存在，排除当前实例
        if Student.objects.filter(phone=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("该手机号已被使用")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        student = Student(**validated_data)
        student.set_password(password)
        student.save()
        return student 

class ClassManageSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)

    class Meta:
        model = Class
        fields = ['id', 'name', 'teacher', 'teacher_name', 'student_count', 'created_at']
        read_only_fields = ['teacher', 'created_at']

    def get_student_count(self, obj):
        return obj.students.count()

    def validate_name(self, value):
        """验证班级名称唯一性"""
        teacher = self.context.get('teacher')
        if Class.objects.filter(name=value, teacher=teacher).exists():
            raise serializers.ValidationError("该班级名称已存在")
        return value 

class NoticeManageSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Notice
        fields = ['id', 'title', 'content', 'teacher', 'teacher_name', 'created_at']
        read_only_fields = ['teacher', 'created_at']

class NoticeReadStatusSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    username = serializers.CharField()

    class Meta:
        model = Student
        fields = ['avatar', 'username']

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None