from rest_framework import serializers
from ..models import Student, Notice, Teacher
from django.middleware.csrf import logger


# 学生注册序列化器
class StudentRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = ['student_no', 'username', 'phone', 'password', 'confirm_password', 'classs']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        # 验证密码
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("两次输入的密码不一致")
        return data

    def validate_student_no(self, value):
        """验证学号唯一性"""
        if Student.objects.filter(student_no=value).exists():
            raise serializers.ValidationError("学号已被使用")
        return value
    
    def validate_phone(self, value):
        """验证手机号唯一性（包括学生和教师）"""
        if Student.objects.filter(phone=value).exists():
            raise serializers.ValidationError("该手机号已被学生使用")
        if Teacher.objects.filter(phone=value).exists():
            raise serializers.ValidationError("该手机号已被教师使用")
        return value

# 学生登录序列化器
class StudentLoginSerializer(serializers.Serializer):
    student_no = serializers.CharField()
    password = serializers.CharField()


# 学生基础序列化器
class StudentSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='classs.name', read_only=True)
    province_display = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    province_type = serializers.CharField(read_only=True)
    unread_notice_count = serializers.SerializerMethodField()
    teacher = serializers.CharField(source='classs.teacher.username', read_only=True)
    class Meta:
        model = Student
        fields = [
            'id', 'student_no', 'username', 'phone', 'classs', 'class_name',
            'avatar', 'status', 'status_display', 'role', 'province', 
            'province_display', 'province_type', 'unread_notice_count',
            'study_school', 'study_major', 'teacher'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'study_school': {'required': False},
            'study_major': {'required': False}
        }

    def get_unread_notice_count(self, obj):
        """获取未读通知数量"""
        # 获取该学生班级教师发布的所有通知
        all_notices = Notice.objects.filter(teacher=obj.classs.teacher)
        # 获取学生已读的通知
        read_notices = obj.read_notices.all()
        # 返回未读通知数量
        return all_notices.exclude(id__in=read_notices.values_list('id', flat=True)).count()

    def to_representation(self, instance):
        """自定义数据展示"""
        data = super().to_representation(instance)
        
        # 如果是就业状态，移除升学相关字段
        if instance.status == 0:
            data.pop('study_school', None)
            data.pop('study_major', None)
        
        return data


# 学生个人信息序列化器
class StudentProfileSerializer(serializers.ModelSerializer):
    province_display = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    province_type = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = ['username', 'phone', 'avatar', 'status', 'province',
                  'study_school', 'study_major', 'province_display','study_school','study_major',
                  'status_display', 'province_type']
        extra_kwargs = {
                'phone': {'required': False},
                'avatar': {'required': False},
                'status': {'required': False},
                'province': {'required': False},
                'study_school': {'required': False},
                'study_major': {'required': False}
            }
            
    def validate(self, data):
        # 获取当前状态，如果没有更新则使用实例的状态
        status = data.get('status', self.instance.status if self.instance else 0)

        # 就业状态的验证
        if status == 0:
            if data.get('study_school') or data.get('study_major'):
                raise serializers.ValidationError('就业状态下不能填写升学信息')
            # 清除升学信息
            data['study_school'] = None
            data['study_major'] = None
            
        # 升学状态的验证
        elif status == 1:
            # 检查升学院校
            if not data.get('study_school') and not getattr(self.instance, 'study_school', None):
                raise serializers.ValidationError('升学状态下必须填写升学院校')
            # 检查升学专业
            if not data.get('study_major') and not getattr(self.instance, 'study_major', None):
                raise serializers.ValidationError('升学状态下必须填写升学专业')

        return data

    def update(self, instance, validated_data):
        """更新学生信息"""
        # 记录更新前的值
        logger.info(f"更新前的实例数据: phone={instance.phone}")
        logger.info(f"要更新的数据: {validated_data}")
        
        # 遍历验证后的数据，更新实例
        for attr, value in validated_data.items():
            # 确保值不为 None 且与当前值不同时才更新
            if value is not None and getattr(instance, attr) != value:
                logger.info(f"更新字段 {attr}: {getattr(instance, attr)} -> {value}")
                setattr(instance, attr, value)
        
        # 保存实例
        instance.save()
        logger.info(f"更新后的实例数据: phone={instance.phone}")
        
        return instance

# 学生列表展示序列化器
class StudentListSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='classs.name', read_only=True)

    class Meta:
        model = Student
        fields = ['student_no', 'username', 'avatar', 'status', 
                 'province', 'class_name',]

# 学生修改密码序列化器
class StudentChangePasswordSerializer(serializers.Serializer):
    """学生修改密码序列化器"""
    old_password = serializers.CharField(
        required=True,
        help_text="原密码"
    )
    new_password = serializers.CharField(
        required=True,
        min_length=6,
        help_text="新密码，最少6个字符"
    )
    confirm_password = serializers.CharField(
        required=True,
        help_text="确认新密码"
    )

    def validate(self, data):
        """验证新密码和确认密码是否一致"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("新密码和确认密码不一致")
        return data