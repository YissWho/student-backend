from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from ...models import Teacher
from ...serializers.teacher import TeacherProfileSerializer, TeacherUpdateSerializer, TeacherChangePasswordSerializer


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def teacher_profile(request):
    """
    GET: 获取教师个人信息
    PUT: 更新教师个人信息
    """
    try:
        # 通过token中的phone获取教师信息
        phone = request.user.username  # JWT token中存储的是phone作为username
        teacher = Teacher.objects.get(phone=phone)
        
        if request.method == 'GET':
            serializer = TeacherProfileSerializer(teacher)
            return Response({
                'status': 'success',
                'message': '获取成功',
                'code': 200,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        # PUT 请求处理更新
        data = request.data
        if request.FILES and 'avatar' in request.FILES:
            if teacher.avatar:
                teacher.avatar.delete(save=False)
            data['avatar'] = request.FILES['avatar']
            
        serializer = TeacherUpdateSerializer(teacher, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # 返回更新后的完整信息
            profile_serializer = TeacherProfileSerializer(teacher)
            return Response({
                'status': 'success',
                'message': '更新成功',
                'code': 200,
                'data': profile_serializer.data
            }, status=status.HTTP_200_OK)
            
        return Response({
            'status': 'false',
            'message': serializer.errors,
            'code': 400
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Teacher.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '教师不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'false',
            'message': '服务器内部错误',
            'code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    修改密码
    需要提供原密码、新密码和确认密码
    """
    try:
        teacher = Teacher.objects.get(phone=request.user.username)
        serializer = TeacherChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            # 验证原密码
            if not teacher.check_password(serializer.validated_data['old_password']):
                return Response({
                    'status': 'false',
                    'message': '原密码错误',
                    'code': 400
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # 设置新密码
            teacher.set_password(serializer.validated_data['new_password'])
            teacher.save()
            
            return Response({
                'status': 'success',
                'message': '密码修改成功',
                'code': 200
            }, status=status.HTTP_200_OK)
            
        return Response({
            'status': 'false',
            'message': serializer.errors,
            'code': 400
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Teacher.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '教师不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'false',
            'message': '服务器内部错误',
            'code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)