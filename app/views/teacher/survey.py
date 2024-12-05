from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q
from ...models import Survey, SurveyResponse, Teacher, Class, Student
from ...serializers.survey import SurveySerializer, SurveyResponseSerializer, SurveyResponseListSerializer

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    def get_paginated_response(self, data):
        return Response({
            'status': 'success',
            'code': 200,
            'message': '获取成功',
            'data': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'list': data
            }
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_survey_stats(request):
    """获取问卷统计信息"""
    try:
        # 获取教师信息
        teacher = Teacher.objects.get(phone=request.user.username)
        
        # 获取该教师管理的所有班级
        class_ids = Class.objects.filter(teacher=teacher).values_list('id', flat=True)
        
        # 获取这些班级的所有学生
        total_students = Student.objects.filter(classs_id__in=class_ids)
        total_count = total_students.count()
        
        # 获取问卷ID（如果有）
        survey_id = request.query_params.get('survey_id')
        
        # 查询问卷
        surveys = Survey.objects.all()
        if survey_id:
            surveys = surveys.filter(id=survey_id)
        
        # 设置分页
        paginator = CustomPagination()
        paginated_surveys = paginator.paginate_queryset(surveys, request)
        
        # 准备返回数据
        survey_stats = []
        for survey in paginated_surveys:
            # 获取已完成该问卷的学生数量
            completed_count = SurveyResponse.objects.filter(
                survey=survey,
                student__classs_id__in=class_ids
            ).count()
            
            # 计算未完成数量
            uncompleted_count = total_count - completed_count
            
            survey_stats.append({
                'id': survey.id,
                'title': survey.title,
                'description': survey.description,
                'is_active': survey.is_active,
                'is_default': survey.is_default,
                'start_time': survey.start_time,
                'end_time': survey.end_time,
                'status': survey.status,
                'completed_count': completed_count,
                'uncompleted_count': uncompleted_count,
                'total_count': total_count,
                'completion_rate': round(completed_count / total_count * 100, 2) if total_count > 0 else 0
            })
        
        return paginator.get_paginated_response(survey_stats)
        
    except Teacher.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '教师信息不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'false',
            'message': str(e),
            'code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_survey_detail(request, survey_id):
    """获取问卷详情信息"""
    try:
        # 获取教师信息
        teacher = Teacher.objects.get(phone=request.user.username)
        
        # 获取该教师管理的所有班级
        class_ids = Class.objects.filter(teacher=teacher).values_list('id', flat=True)
        
        # 获取问卷
        survey = Survey.objects.get(id=survey_id)
        
        # 获取所有相关学生
        students = Student.objects.filter(classs_id__in=class_ids)
        
        # 获取已完成问卷的学生数量
        completed_count = SurveyResponse.objects.filter(
            survey=survey,
            student__classs_id__in=class_ids
        ).count()
        
        # 计算未完成数量
        total_count = students.count()
        uncompleted_count = total_count - completed_count
        
        data = {
            'survey': {
                'id': survey.id,
                'title': survey.title,
                'description': survey.description,
                'is_active': survey.is_active,
                'is_default': survey.is_default,
                'start_time': survey.start_time,
                'end_time': survey.end_time,
                'status': survey.status
            },
            'stats': {
                'total_count': total_count,
                'completed_count': completed_count,
                'uncompleted_count': uncompleted_count,
                'completion_rate': round(completed_count / total_count * 100, 2) if total_count > 0 else 0
            }
        }
        
        return Response({
            'status': 'success',
            'message': '获取成功',
            'code': 200,
            'data': data
        })
        
    except Survey.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '问卷不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)
    except Teacher.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '教师信息不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'false',
            'message': str(e),
            'code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_survey_students(request, survey_id):
    """获取问卷的学生列表（已完成/未完成）"""
    try:
        # 获取教师信息
        teacher = Teacher.objects.get(phone=request.user.username)
        
        # 获取该教师管理的所有班级
        class_ids = Class.objects.filter(teacher=teacher).values_list('id', flat=True)
        
        # 获取问卷
        survey = Survey.objects.get(id=survey_id)
        
        # 获取状态参数（0：未完成，1：已完成）
        status_param = request.query_params.get('status', '0')
        
        # 获取所有相关学生
        students = Student.objects.filter(classs_id__in=class_ids)
        
        # 获取已完成问卷的学生ID列表
        completed_student_ids = SurveyResponse.objects.filter(
            survey=survey,
            student__classs_id__in=class_ids
        ).values_list('student_id', flat=True)
        
        # 根据状态筛选学生
        if status_param == '1':  # 已完成
            students = students.filter(id__in=completed_student_ids)
        else:  # 未完成
            students = students.exclude(id__in=completed_student_ids)
            
        # 设置分页
        paginator = CustomPagination()
        paginated_students = paginator.paginate_queryset(students, request)
        
        # 准备返回数据
        student_data = []
        for student in paginated_students:
            response = None
            if status_param == '1':
                response = SurveyResponse.objects.filter(
                    survey=survey,
                    student=student
                ).first()
                
            student_info = {
                'id': student.id,
                'username': student.username,
                'student_no': student.student_no,
                'avatar': student.avatar.url if student.avatar else None,
                'class_name': student.classs.name,
                'submitted_at': response.submitted_at if response else None
            }
            student_data.append(student_info)
        
        return paginator.get_paginated_response(student_data)
        
    except Survey.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '问卷不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)
    except Teacher.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '教师信息不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'false',
            'message': str(e),
            'code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_survey_response(request, survey_id, student_no):
    """获取特定学生的问卷填写情况"""
    try:
        # 获取教师信息
        teacher = Teacher.objects.get(phone=request.user.username)
        
        # 获取该教师管理的所有班级
        class_ids = Class.objects.filter(teacher=teacher).values_list('id', flat=True)
        
        # 验证学生是否属于该教师的班级
        student = Student.objects.filter(
            student_no=student_no,
            classs_id__in=class_ids
        ).first()
        
        if not student:
            return Response({
                'status': 'false',
                'message': '无权查看该学生信息',
                'code': 403
            }, status=status.HTTP_403_FORBIDDEN)
            
        # 获取问卷回答
        response = SurveyResponse.objects.filter(
            survey_id=survey_id,
            student=student
        ).first()
        
        if not response:
            return Response({
                'status': 'success',
                'message': '获取成功',
                'code': 200,
                'data': {
                    'student': {
                        'id': student.id,
                        'username': student.username,
                        'student_no': student.student_no,
                        'avatar': student.avatar.url if student.avatar else None,
                        'class_name': student.classs.name
                    },
                    'status': 'uncompleted',
                    'response': None
                }
            })
            
        # 序列化问卷回答
        serializer = SurveyResponseSerializer(response)
        
        return Response({
            'status': 'success',
            'message': '获取成功',
            'code': 200,
            'data': {
                'status': 'completed',
                'response': serializer.data
            }
        })
        
    except Teacher.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '教师信息不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'false',
            'message': str(e),
            'code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 