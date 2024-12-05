from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ...models import Class, Teacher
from ...utils.captcha import CaptchaHelper
import uuid

@api_view(['GET'])
@permission_classes([AllowAny])
def get_captcha(request):
    """获取验证码"""
    try:
        # 生成唯一key
        key = str(uuid.uuid4())
        # 生成验证码
        captcha_data = CaptchaHelper.generate_and_save(key)
        
        return Response({
            'status': 'success',
            'code': 200,
            'data': captcha_data
        })
    except Exception as e:
        return Response({
            'status': 'false',
            'message': str(e),
            'code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_classes(request):
    """获取所有班级列表"""
    try:
        classes = Class.objects.all().values('id', 'name')
        return Response({
            'status': 'success',
            'code': 200,
            'data': list(classes)
        })
    except Exception as e:
        return Response({
            'status': 'false',
            'message': str(e),
            'code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_teachers(request):
    """获取所有教师列表"""
    try:
        teachers = Teacher.objects.all().values('id', 'username')
        return Response({
            'status': 'success',
            'code': 200,
            'data': [
                {'id': teacher['id'], 'name': teacher['username']}
                for teacher in teachers
            ]
        })
    except Exception as e:
        return Response({
            'status': 'false',
            'message': str(e),
            'code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_teacher_classes(request, teacher_id):
    """获取指定教师管理的班级列表"""
    try:
        classes = Class.objects.filter(
            teacher_id=teacher_id
        ).values('id', 'name')
        
        if not classes.exists():
            return Response({
                'status': 'success',
                'code': 200,
                'data': [],
                'message': '该教师暂未管理任何班级'
            })
        
        return Response({
            'status': 'success',
            'code': 200,
            'data': list(classes)
        })
    except Exception as e:
        return Response({
            'status': 'false',
            'message': str(e),
            'code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
