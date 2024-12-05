from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from ...models import Teacher, Class
from ...serializers.teacher_manage import ClassManageSerializer

class ClassPagination(PageNumberPagination):
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
def class_list(request):
    """获取班级列表"""
    try:
        teacher = Teacher.objects.get(phone=request.user.username)
        
        # 获取查询参数
        search = request.query_params.get('search', '')
        
        # 查询该教师的班级
        classes = Class.objects.filter(teacher=teacher)
        
        # 按名称搜索
        if search:
            classes = classes.filter(name__icontains=search)
            
        # 排序
        classes = classes.order_by('created_at')
        
        # 分页
        paginator = ClassPagination()
        paginated_classes = paginator.paginate_queryset(classes, request)
        serializer = ClassManageSerializer(paginated_classes, many=True)
        
        return paginator.get_paginated_response(serializer.data)
        
    except Teacher.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '教师不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_class(request):
    """创建班级"""
    try:
        # 根据用户名(手机号)获取教师对象
        teacher = Teacher.objects.get(phone=request.user.username)
        
        # 创建班级序列化器实例
        # data: 请求数据
        # context: 传入教师对象用于验证班级名称唯一性
        serializer = ClassManageSerializer(
            data=request.data,
            context={'teacher': teacher}
        )
        if serializer.is_valid():
            # 设置教师
            serializer.validated_data['teacher'] = teacher
            class_obj = serializer.save()
            
            return Response({
                'status': 'success',
                'message': '创建成功',
                'code': 200,
                'data': ClassManageSerializer(class_obj).data
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
def class_detail(request, class_id):
    """获取、更新或删除班级"""
    try:
        teacher = Teacher.objects.get(phone=request.user.username)
        class_obj = Class.objects.get(id=class_id, teacher=teacher)
        
        if request.method == 'GET':
            serializer = ClassManageSerializer(class_obj)
            return Response({
                'status': 'success',
                'code': 200,
                'data': serializer.data
            })
            
        elif request.method == 'PUT':
            serializer = ClassManageSerializer(
                class_obj,
                data=request.data,
                context={'teacher': teacher},
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
            # 检查班级是否有学生
            if class_obj.students.exists():
                return Response({
                    'status': 'false',
                    'message': '班级中还有学生，无法删除',
                    'code': 400
                }, status=status.HTTP_400_BAD_REQUEST)
                
            class_obj.delete()
            return Response({
                'status': 'success',
                'message': '删除成功',
                'code': 200
            })
            
    except (Teacher.DoesNotExist, Class.DoesNotExist):
        return Response({
            'status': 'false',
            'message': '资源不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND) 