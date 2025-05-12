from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from ...models import Teacher, Student
from ...serializers.teacher_manage import StudentManageSerializer, StudentCreateUpdateSerializer

class StudentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            'status': 'success',
            'code': 200,
            'data': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data
            }
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_list(request):
    """获取教师管理的学生列表"""
    try:
        teacher = Teacher.objects.get(phone=request.user.username)

        # 获取查询参数
        classs = request.query_params.get('class')
        status = request.query_params.get('status')
        search = request.query_params.get('search', '')

        # 基础查询：获取该教师所有班级的学生
        students = Student.objects.filter(classs__teacher=teacher)

        # 按班级筛选
        if classs:
            students = students.filter(classs_id=classs)

        # 按状态筛选
        if status is not None:
            students = students.filter(status=status)

        # 模糊查询
        if search:
            students = students.filter(
                Q(student_no__icontains=search) |
                Q(username__icontains=search)
            )

        # 排序
        students = students.order_by('student_no')

        # 分页
        paginator = StudentPagination()
        paginated_students = paginator.paginate_queryset(students, request)
        serializer = StudentManageSerializer(paginated_students, many=True)

        return paginator.get_paginated_response(serializer.data)

    except Teacher.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '教师不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def create_student(request):
    """创建新学生"""
    try:
        teacher = Teacher.objects.get(phone=request.user.username)
        
        # 确保选择的班级属于当前教师
        classs_id = request.data.get('classs')
        if not teacher.class_set.filter(id=classs_id).exists():
            return Response({
                'status': 'false',
                'message': '无权操作此班级',
                'code': 403
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = StudentCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.save()
            return Response({
                'status': 'success',
                'message': '创建成功',
                'code': 200,
                'data': StudentManageSerializer(student).data
            }, status=status.HTTP_201_CREATED)
            
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

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def student_detail(request, student_id):
    """获取、更新或删除学生信息"""
    try:
        teacher = Teacher.objects.get(phone=request.user.username)
        student = Student.objects.get(
            id=student_id,
            classs__teacher=teacher
        )
        
        if request.method == 'GET':
            serializer = StudentManageSerializer(student)
            return Response({
                'status': 'success',
                'code': 200,
                'data': serializer.data
            })
            
        elif request.method == 'PUT':
            # 确保更新的班级属于当前教师
            classs_id = request.data.get('classs')
            if classs_id and not teacher.class_set.filter(id=classs_id).exists():
                return Response({
                    'status': 'false',
                    'message': '无权操作此班级',
                    'code': 403
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = StudentCreateUpdateSerializer(
                student,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                # 如果提供了新密码
                if 'password' in request.data:
                    student.set_password(request.data['password'])
                
                # 处理头像
                if request.FILES and 'avatar' in request.FILES:
                    if student.avatar:
                        student.avatar.delete(save=False)
                    student.avatar = request.FILES['avatar']
                
                student = serializer.save()
                return Response({
                    'status': 'success',
                    'message': '更新成功',
                    'code': 200,
                    'data': StudentManageSerializer(student).data
                })
                
            return Response({
                'status': 'false',
                'message': serializer.errors,
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'DELETE':
            student.delete()
            return Response({
                'status': 'success',
                'message': '删除成功',
                'code': 200
            })
            
    except Student.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '学生不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)
    except Teacher.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '教师不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND) 
