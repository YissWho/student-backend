from rest_framework import serializers
from ..models import Survey, SurveyResponse

class SurveySerializer(serializers.ModelSerializer):
    """问卷序列化器"""
    status = serializers.CharField(read_only=True)
    can_submit = serializers.BooleanField(read_only=True)
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    end_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Survey
        fields = [
            'id', 'title', 'description', 'is_active', 'is_default',
            'start_time', 'end_time', 'status', 'can_submit',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class SurveyResponseSerializer(serializers.ModelSerializer):
    """问卷回答序列化器"""
    student_name = serializers.CharField(source='student.username', read_only=True)
    class_name = serializers.CharField(source='student.classs.name', read_only=True)
    submitted_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    
    future_plan_display = serializers.CharField(source='get_future_plan_display', read_only=True)
    employment_type_display = serializers.CharField(source='get_employment_type_display', read_only=True)
    city_preference_display = serializers.CharField(source='get_city_preference_display', read_only=True)
    expected_salary_display = serializers.CharField(source='get_expected_salary_display', read_only=True)
    job_market_view_display = serializers.CharField(source='get_job_market_view_display', read_only=True)
    study_type_display = serializers.CharField(source='get_study_type_display', read_only=True)
    study_plan_status_display = serializers.CharField(source='get_study_plan_status_display', read_only=True)

    class Meta:
        model = SurveyResponse
        fields = [
            'id', 'student_name', 'name', 'student_no', 'class_name', 'phone', 
            'future_plan', 'future_plan_display',
            # 就业相关
            'employment_type', 'employment_type_display',
            'city_preference', 'city_preference_display',
            'expected_salary', 'expected_salary_display',
            'job_market_view', 'job_market_view_display',
            # 升学相关
            'study_type', 'study_type_display',
            'target_school',
            'study_plan_status', 'study_plan_status_display',
            'submitted_at'
        ]
        read_only_fields = [
            'id', 'student_name', 'class_name', 'submitted_at',
            'future_plan_display',
            'employment_type_display', 'city_preference_display',
            'expected_salary_display', 'job_market_view_display',
            'study_type_display', 'study_plan_status_display'
        ]

    def validate(self, data):
        """验证数据"""
        future_plan = data.get('future_plan')
        
        # 验证就业相关字段
        if future_plan == 0:  # 就业
            if not all([
                isinstance(data.get('employment_type'), int),
                isinstance(data.get('city_preference'), int),
                isinstance(data.get('expected_salary'), int),
                isinstance(data.get('job_market_view'), int)
            ]):
                raise serializers.ValidationError("选择就业时，必须填写就业相关信息")
                
        # 验证升学相关字段
        elif future_plan == 1:  # 升学深造
            if not all([
                isinstance(data.get('study_type'), int),
                data.get('target_school'),
                isinstance(data.get('study_plan_status'), int)
            ]):
                raise serializers.ValidationError("选择升学时，必须填写升学相关信息")
                
        return data

class SurveyResponseListSerializer(serializers.ModelSerializer):
    """问卷回答列表序列化器（用于教师查看）"""
    student_name = serializers.CharField(source='student.username')
    class_name = serializers.CharField(source='student.classs.name')
    submitted_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    future_plan_display = serializers.CharField(source='get_future_plan_display', read_only=True)
    employment_type_display = serializers.CharField(source='get_employment_type_display', read_only=True)
    study_type_display = serializers.CharField(source='get_study_type_display', read_only=True)

    class Meta:
        model = SurveyResponse
        fields = [
            'id', 'student_name', 'name', 'student_no', 'class_name', 'phone',
            'future_plan', 'future_plan_display',
            'employment_type_display', 'study_type_display',
            'submitted_at'
        ] 