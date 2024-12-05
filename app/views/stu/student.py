from venv import logger

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from app.serializers.student import StudentProfileSerializer, StudentSerializer,StudentListSerializer, StudentChangePasswordSerializer
from app.models import Student
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student(request, student_id=None):
    """
    获取学生信息
    如果提供student_id，则获取指定学生信息
    否则获取当前登录学生信息
    """
    try:
        if student_id:
            student = Student.objects.get(id=student_id)
        else:
            student = Student.objects.get(student_no=request.user.username)
            
        serializer = StudentSerializer(student)
        
        # 根据学生状态组织返回数据
        response_data = {
            'status': 'success',
            'code': 200,
            'data': {
                'basic_info': {
                    'id': serializer.data['id'],
                    'student_no': serializer.data['student_no'],
                    'username': serializer.data['username'],
                    'phone': serializer.data['phone'],
                    'avatar': serializer.data['avatar'],
                    'class_name': serializer.data['class_name'],
                    'teacher': serializer.data['teacher'],
                    'unread_notice_count': serializer.data['unread_notice_count']
                },
                'status_info': {
                    'status': serializer.data['status'],
                    'status_display': serializer.data['status_display'],
                    'province': serializer.data['province'],
                    'province_display': serializer.data['province_display'],
                    'province_type': serializer.data['province_type']
                }
            }
        }

        # 如果是升学状态，添加升学信息
        if student.status == 1:
            response_data['data']['study_info'] = {
                'study_school': serializer.data['study_school'],
                'study_major': serializer.data['study_major']
            }

        return Response(response_data, status=status.HTTP_200_OK)

    except Student.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '学生不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT', 'GET'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def update_profile(request):
    """
    学生更新个人信息
    """
    try:
        student = Student.objects.get(student_no=request.user.username)
    except Student.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '学生不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = StudentProfileSerializer(student)
        return Response({
            'status': 'success',
            'data': serializer.data,
            'code': 200
        }, status=status.HTTP_200_OK)

    # 处理文件上传
    data = request.data
    if request.FILES and 'avatar' in request.FILES:
        if student.avatar:
            student.avatar.delete(save=False)
        data['avatar'] = request.FILES['avatar']

    serializer = StudentProfileSerializer(student, data=data, partial=True)
    if serializer.is_valid():
        updated_student = serializer.save()
        updated_student.refresh_from_db()
        serializer = StudentProfileSerializer(updated_student)
        return Response({
            'status': 'success',
            'message': '个人信息更新成功',
            'data': serializer.data,
            'code': 200
        }, status=status.HTTP_200_OK)
    
    return Response({
        'status': 'false',
        'message': serializer.errors,
        'code': 400
    }, status=status.HTTP_400_BAD_REQUEST)


class StudentPagination(PageNumberPagination):
    """学生列表分页器"""
    page_size = 10  # 每页显示10条
    page_size_query_param = 'page_size'  # 允许客户端通过此参数指定每页数量
    max_page_size = 50  # 最大每页数量

    def get_paginated_response(self, data):
        return Response({
            'status': 'success',
            'code': 200,
            'data': {
                'count': self.page.paginator.count,  # 总条数
                'next': self.get_next_link(),  # 下一页链接
                'previous': self.get_previous_link(),  # 上一页链接
                'results': data  # 当前页数据
            }
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_classmates(request):
    """
    获取同班同学列表
    支持分页和多条件查询
    """
    try:
        # 获取当前学生信息
        student = Student.objects.get(student_no=request.user.username)
        
        # 获取查询参数
        search = request.query_params.get('search', '')  # 姓名或学号模糊搜索
        status_param = request.query_params.get('status')      # 就业状态
        province = request.query_params.get('province')  # 意向地区
        
        # 查询同班同学，排除自己
        classmates = Student.objects.filter(
            classs=student.classs  # 同班
        ).exclude(
            id=student.id  # 排除自己
        )
        
        # 按姓名或学号模糊查询
        if search:
            classmates = classmates.filter(
                Q(username__icontains=search) |  # 姓名模糊查询
                Q(student_no__icontains=search)  # 学号模糊查询
            )
        
        # 按就业状态筛选
        if status_param is not None:
            try:
                status_value = int(status_param)
                classmates = classmates.filter(status=status_value)
            except ValueError:
                pass
        
        # 按意向地区筛选
        if province is not None:
            try:
                province = int(province)
                classmates = classmates.filter(province=province)
            except ValueError:
                pass
        
        # 排序
        classmates = classmates.order_by('student_no')
        
        # 分页
        paginator = StudentPagination()
        paginated_classmates = paginator.paginate_queryset(classmates, request)
        serializer = StudentListSerializer(paginated_classmates, many=True)
        
        return paginator.get_paginated_response(serializer.data)
        
    except Student.DoesNotExist:
        return Response({
            'status': 'error',
            'message': '学生不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e),
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
        student = Student.objects.get(student_no=request.user.username)
        serializer = StudentChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            # 验证原密码
            if not student.check_password(serializer.validated_data['old_password']):
                return Response({
                    'status': 'false',
                    'message': '原密码错误',
                    'code': 400
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # 设置新密码
            student.set_password(serializer.validated_data['new_password'])
            student.save()
            
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
        
    except Student.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '学生不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)

