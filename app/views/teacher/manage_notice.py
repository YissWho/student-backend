from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from ...models import Teacher, Notice, Student, Class
from ...serializers.teacher_manage import NoticeManageSerializer, NoticeReadStatusSerializer

class NoticePagination(PageNumberPagination):
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

class StudentStatusPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'status': 'success',
            'code': 200,
            'data': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'list': data
            }
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notice_list(request):
    """获取通知列表"""
    try:
        teacher = Teacher.objects.get(phone=request.user.username)
        
        # 获取查询参数
        search = request.query_params.get('search', '')
        
        # 查询该教师的通知
        notices = Notice.objects.filter(teacher=teacher)
        
        # 按标题或内容搜索
        if search:
            notices = notices.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )
            
        # 排序
        notices = notices.order_by('-created_at')
        
        # 分页
        paginator = NoticePagination()
        paginated_notices = paginator.paginate_queryset(notices, request)
        serializer = NoticeManageSerializer(paginated_notices, many=True)
        
        return paginator.get_paginated_response(serializer.data)
        
    except Teacher.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '教师不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_notice(request):
    """创建通知"""
    try:
        teacher = Teacher.objects.get(phone=request.user.username)
        
        serializer = NoticeManageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=teacher)
            
            return Response({
                'status': 'success',
                'message': '创建成功',
                'code': 200,
                'data': serializer.data
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
def notice_detail(request, notice_id):
    """获取、更新或删除通知"""
    try:
        teacher = Teacher.objects.get(phone=request.user.username)
        notice = Notice.objects.get(id=notice_id, teacher=teacher)
        
        if request.method == 'GET':
            serializer = NoticeManageSerializer(notice)
            return Response({
                'status': 'success',
                'code': 200,
                'data': serializer.data
            })
            
        elif request.method == 'PUT':
            serializer = NoticeManageSerializer(
                notice,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': '更新成功',
                    'code': 200,
                    'data': serializer.data
                })
            return Response({
                'status': 'false',
                'message': serializer.errors,
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'DELETE':
            notice.delete()
            return Response({
                'status': 'success',
                'message': '删除成功',
                'code': 200
            })
            
    except (Teacher.DoesNotExist, Notice.DoesNotExist):
        return Response({
            'status': 'false',
            'message': '资源不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notice_read_students(request, notice_id):
    """获取已读该通知的学生列表"""
    try:
        teacher = Teacher.objects.get(phone=request.user.username)
        notice = Notice.objects.get(id=notice_id, teacher=teacher)
        
        # 获取已读学生
        students = Student.objects.filter(
            classs__teacher=teacher,
            read_notices=notice
        ).order_by('student_no')
        
        # 分页
        paginator = StudentStatusPagination()
        paginated_students = paginator.paginate_queryset(students, request)
        serializer = NoticeReadStatusSerializer(paginated_students, many=True)
        
        return paginator.get_paginated_response(serializer.data)
        
    except (Teacher.DoesNotExist, Notice.DoesNotExist):
        return Response({
            'status': 'false',
            'message': '资源不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notice_unread_students(request, notice_id):
    """获取未读该通知的学生列表"""
    try:
        teacher = Teacher.objects.get(phone=request.user.username)
        notice = Notice.objects.get(id=notice_id, teacher=teacher)
        
        # 获取未读学生
        students = Student.objects.filter(
            classs__teacher=teacher
        ).exclude(
            read_notices=notice
        ).order_by('student_no')
        
        # 分页
        paginator = StudentStatusPagination()
        paginated_students = paginator.paginate_queryset(students, request)
        serializer = NoticeReadStatusSerializer(paginated_students, many=True)
        
        return paginator.get_paginated_response(serializer.data)
        
    except (Teacher.DoesNotExist, Notice.DoesNotExist):
        return Response({
            'status': 'false',
            'message': '资源不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND) 