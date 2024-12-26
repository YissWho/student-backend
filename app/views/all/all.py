from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.models import User
from ...models import Class, Teacher, Student
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

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """刷新token"""
    try:
        # 获取refresh token
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                'status': 'false',
                'message': '请提供refresh token',
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证并刷新token
        refresh = RefreshToken(refresh_token)
        
        # 获取用户信息
        # 用户名可能是手机号或学号
        username = refresh.payload.get('phone') or refresh.payload.get('student_no')  
        
        # 尝试获取教师信息
        teacher = Teacher.objects.filter(phone=username).first()
        if teacher:
            # 添加教师相关信息到token
            new_refresh = RefreshToken.for_user(User.objects.get(username=username))
            new_refresh['phone'] = teacher.phone
            new_refresh['role'] = teacher.role
            
            return Response({
                'status': 'success',
                'message': '刷新成功',
                'code': 200,
                'data': {
                    'token': str(new_refresh.access_token),
                    'refresh': str(new_refresh),
                    'role': teacher.role,
                    'user': {
                        'id': teacher.id,
                        'phone': teacher.phone,
                        'username': teacher.username,
                        'avatar': teacher.avatar.url if teacher.avatar else None
                    }
                }
            })
        
        # 尝试获取学生信息
        student = Student.objects.filter(student_no=username).first()
        if student:
            # 添加学生相关信息到token
            new_refresh = RefreshToken.for_user(User.objects.get(username=username))
            new_refresh['student_no'] = student.student_no
            new_refresh['role'] = student.role
            
            return Response({
                'status': 'success',
                'message': '刷新成功',
                'code': 200,
                'data': {
                    'token': str(new_refresh.access_token),
                    'refresh': str(new_refresh),
                    'role': student.role,
                    'user': {
                        'id': student.id,
                        'student_no': student.student_no,
                        'username': student.username,
                        'avatar': student.avatar.url if student.avatar else None
                    }
                }
            })
            
        return Response({
            'status': 'false',
            'message': '用户不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)
        
    except TokenError:
        return Response({
            'status': 'false',
            'message': 'Token已失效或不合法',
            'code': 401
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({
            'status': 'false',
            'message': str(e),
            'code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
