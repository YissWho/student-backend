from rest_framework import serializers
from ..models import Teacher, Class, Student
from django.db.models import Count

class TeacherLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField()

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'username', 'phone', 'avatar', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class ClassInfoSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = ['id', 'name', 'student_count']

    def get_student_count(self, obj):
        return obj.students.count()

class TeacherProfileSerializer(serializers.ModelSerializer):
    classes = ClassInfoSerializer(source='class_set', many=True, read_only=True)
    total_students = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ['id', 'username', 'phone', 'avatar', 'classes', 'total_students']

    def get_total_students(self, obj):
        return Student.objects.filter(classs__teacher=obj).count()

class TeacherUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['username', 'phone', 'avatar']
        extra_kwargs = {
            'username': {'required': False},
            'phone': {'required': False},
            'avatar': {'required': False}
        }

    def validate_phone(self, value):
        """验证手机号唯一性"""
        if Teacher.objects.exclude(id=self.instance.id).filter(phone=value).exists():
            raise serializers.ValidationError("该手机号已被使用")
        return value

    def validate_username(self, value):
        """验证用户名唯一性"""
        if Teacher.objects.exclude(id=self.instance.id).filter(username=value).exists():
            raise serializers.ValidationError("该用户名已被使用")
        return value

class TeacherChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        """验证新密码和确认密码是否一致"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("新密码和确认密码不一致")
        return data

class TeacherManageStudentSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='classs.name', read_only=True)
    province_display = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = '__all__'  # 包含所有字段
        read_only_fields = ['role', 'is_read', 'status', 'province', 
                          'study_school', 'study_major', 'created_at', 
                          'updated_at', 'read_notices']  # 这些字段不允许修改

    def validate_student_no(self, value):
        """验证学号唯一性"""
        if Student.objects.exclude(id=self.instance.id if self.instance else None)\
                         .filter(student_no=value).exists():
            raise serializers.ValidationError("该学号已被使用")
        return value

    def validate_phone(self, value):
        """验证手机号唯一性"""
        if Student.objects.exclude(id=self.instance.id if self.instance else None)\
                         .filter(phone=value).exists():
            raise serializers.ValidationError("该手机号已被使用")
        return value