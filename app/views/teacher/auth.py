from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from ...models import Teacher
from ...utils.captcha import CaptchaHelper
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    operation_summary='教师登录',
    operation_description='使用手机号和密码登录系统',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='手机号'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='密码'),
            'captcha_key': openapi.Schema(type=openapi.TYPE_STRING, description='验证码key'),
            'captcha_code': openapi.Schema(type=openapi.TYPE_STRING, description='验证码')
        }
    )
)
@api_view(['POST'])
@permission_classes([AllowAny])
def teacher_login(request):
    """教师登录"""
    try:
        phone = request.data.get('phone')
        password = request.data.get('password')
        captcha_key = request.data.get('captcha_key')
        captcha_code = request.data.get('captcha_code')
        
        # 验证参数完整性
        if not all([phone, password, captcha_key, captcha_code]):
            return Response({
                'status': 'false',
                'message': '请填写完整的登录信息',
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # 验证验证码
        if not CaptchaHelper.verify_code(captcha_key, captcha_code):
            return Response({
                'status': 'false',
                'message': '验证码错误或已过期',
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            teacher = Teacher.objects.get(phone=phone)
        except Teacher.DoesNotExist:
            return Response({
                'status': 'false',
                'message': '教师不存在',
                'code': 404
            }, status=status.HTTP_404_NOT_FOUND)
            
        if not teacher.check_password(password):
            return Response({
                'status': 'false',
                'message': '密码错误',
                'code': 401
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        # 获取或创建对应的Django User对象
        user, created = User.objects.get_or_create(
            username=teacher.phone,
            defaults={'email': teacher.phone}
        )
        
        if created:
            user.set_password(password)
            user.save()
            
        # 生成JWT token
        refresh = RefreshToken.for_user(user)
        # 添加自定义信息到token
        refresh['phone'] = teacher.phone
        refresh['role'] = teacher.role
        
        return Response({
            'status': 'success',
            'message': '登录成功',
            'code': 200,
            'data': {
                'role': teacher.role,
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                "user":{
                    "id": teacher.id,
                    "phone": teacher.phone,
                    "username": teacher.username,
                    "avatar": teacher.avatar.url if teacher.avatar else None,
                }
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'false',
            'message': str(e),
            'code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)