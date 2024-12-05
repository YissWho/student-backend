from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from ...models import Teacher, Class, Student, provinces

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def class_student_count(request):
    """获取每个班级的学生人数（饼图数据）"""
    try:
        teacher = Teacher.objects.get(phone=request.user.username)
        classes = Class.objects.filter(teacher=teacher)
        
        data = []
        for cls in classes:
            data.append({
                'value': cls.students.count(),
                'name': cls.name
            })
        
        return Response({
            'status': 'success',
            'code': 200,
            'data': data  # echarts饼图数据格式
        })
    except Teacher.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '教师不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def class_employment_stats(request):
    """获取每个班级的就业和升学人数（柱状折线图数据）"""
    try:
        teacher = Teacher.objects.get(phone=request.user.username)
        classes = Class.objects.filter(teacher=teacher)
        
        class_names = []
        employment_data = []
        further_study_data = []
        
        for cls in classes:
            class_names.append(cls.name)
            employment_data.append(
                cls.students.filter(status=0).count()  # 就业人数
            )
            further_study_data.append(
                cls.students.filter(status=1).count()  # 升学人数
            )
        
        return Response({
            'status': 'success',
            'code': 200,
            'data': {
                'xAxis': class_names,
                'series': [
                    {
                        'name': '就业人数',
                        'type': 'bar',
                        'data': employment_data
                    },
                    {
                        'name': '升学人数',
                        'type': 'line',
                        'data': further_study_data
                    }
                ]
            }
        })
    except Teacher.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '教师不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def overall_status_ratio(request):
    """获取所有学生的就业升学比例（饼图数据）"""
    try:
        teacher = Teacher.objects.get(phone=request.user.username)
        total_students = Student.objects.filter(classs__teacher=teacher)
        
        employment_count = total_students.filter(status=0).count()
        study_count = total_students.filter(status=1).count()
        
        data = [
            {'value': employment_count, 'name': '就业'},
            {'value': study_count, 'name': '升学'}
        ]
        
        return Response({
            'status': 'success',
            'code': 200,
            'data': data  # echarts饼图数据格式
        })
    except Teacher.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '教师不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def province_wordcloud(request):
    """获取就业意向省份词云数据"""
    try:
        teacher = Teacher.objects.get(phone=request.user.username)
        # 获取就业学生的省份统计
        province_stats = Student.objects.filter(
            classs__teacher=teacher,
            status=0  # 就业学生
        ).values('province').annotate(
            value=Count('id')  # 统计每个省份的人数
        )
        
        # 转换为词云数据格式
        data = []
        for stat in province_stats:
            if stat['province'] is not None:  # 确保省份不为空
                province_name = dict(provinces).get(stat['province'])  # 从choices中获取省份名称
                if province_name:
                    data.append({
                        'name': province_name,
                        'value': stat['value']
                    })
        
        return Response({
            'status': 'success',
            'code': 200,
            'data': data  # echarts词云图数据格式
        })
    except Teacher.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '教师不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def province_map_data(request):
    """获取省份地图数据"""
    try:
        teacher = Teacher.objects.get(phone=request.user.username)
        class_id = request.query_params.get('class_id')  # 可选的班级筛选
        
        # 基础查询
        query = Q(status=0)  # 就业学生
        
        # 根据参数决定是查询所有班级还是特定班级
        if class_id:
            query &= Q(classs_id=class_id)
        query &= Q(classs__teacher=teacher)
        
        # 获取省份统计数据
        province_stats = Student.objects.filter(query).values(
            'province'
        ).annotate(
            value=Count('id')
        )
        
        # 转换为地图数据格式
        data = []
        for stat in province_stats:
            if stat['province'] is not None:
                province_name = dict(provinces).get(stat['province'])
                if province_name:
                    data.append({
                        'name': province_name,
                        'value': stat['value']
                    })
        
        return Response({
            'status': 'success',
            'code': 200,
            'data': data  # echarts地图数据格式
        })
    except Teacher.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '教师不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND) 