from venv import logger

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from app.serializers.notice import NoticeSerializer
from app.models import Notice, Student
from django.db.models import Q

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
        }, status=status.HTTP_200_OK)
        
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notice_list(request):
    """
    获取通知列表
    支持分页和已读/未读筛选
    """
    try:
        # 获取当前学生
        student = Student.objects.get(student_no=request.user.username)
        
        # 获取筛选参数
        is_read_param = request.query_params.get('is_read')
        
        # 获取该学生所在班级教师发布的通知
        notices = Notice.objects.filter(
            teacher=student.classs.teacher
        ).order_by('-created_at')  # 按创建时间倒序
        
        # 根据学生的已读状态筛选
        if is_read_param is not None:
            try:
                is_read = bool(int(is_read_param))
                if is_read:
                    # 获取已读通知
                    notices = notices.filter(id__in=student.read_notices.all())
                else:
                    # 获取未读通知
                    notices = notices.exclude(id__in=student.read_notices.all())
            except ValueError:
                pass
        
        # 创建分页器实例
        paginator = NoticePagination()
        
        # 进行分页
        paginated_notices = paginator.paginate_queryset(notices, request)
        
        # 序列化
        serializer = NoticeSerializer(paginated_notices, many=True, context={'student': student})
        
        # 返回分页响应
        return paginator.get_paginated_response(serializer.data)
        
    except Student.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '学生不存在',
            'code':404
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'false',
            'message': str(e),
            'code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notice_as_read(request, notice_id=None):
    """
    标记通知为已读
    支持单个通知和批量通知
    """
    try:
        student = Student.objects.get(student_no=request.user.username)
        
        # 批量标记
        if not notice_id:
            notice_ids = request.data.get('notice_ids', [])
            if not notice_ids:
                return Response({
                    'status': 'error',
                    'message': '请提供通知ID',
                    'code': 400
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取该学生班级教师的所有指定ID的通知
            notices = Notice.objects.filter(
                id__in=notice_ids,
                teacher=student.classs.teacher
            )
            
            # 批量添加到已读
            student.read_notices.add(*notices)
            
            return Response({
                'status': 'success',
                'message': f'成功标记 {notices.count()} 条通知为已读',
                'code': 200
            })
            
        # 单个标记
        else:
            notice = get_object_or_404(
                Notice,
                id=notice_id,
                teacher=student.classs.teacher
            )
            student.read_notices.add(notice)
            
            return Response({
                'status': 'success',
                'message': '通知已标记为已读',
                'code': 200
            })
        
    except Student.DoesNotExist:
        return Response({
            'status': 'error',
            'message': '学生不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)