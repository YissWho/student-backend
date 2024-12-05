from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ...models import Survey, SurveyResponse, Student
from ...serializers.survey import SurveySerializer, SurveyResponseSerializer
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_survey(request):
    """获取问卷信息"""
    try:
        # 获取学生信息（使用学号）
        student = Student.objects.get(student_no=request.user.username)
        
        # 获取所有激活的问卷
        surveys = Survey.objects.filter(is_active=True)
        
        # 如果指定了问卷ID，则获取特定问卷
        survey_id = request.query_params.get('survey_id')
        if survey_id:
            survey = surveys.filter(id=survey_id).first()
            if not survey:
                return Response({
                    'status': 'false',
                    'message': '问卷不存在',
                    'code': 404
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # 否则获取默认问卷
            survey = surveys.filter(is_default=True).first()
            if not survey:
                # 如果没有默认问卷，则获取最新的问卷
                survey = surveys.first()
                
        if not survey:
            return Response({
                'status': 'false',
                'message': '暂无可用的问卷',
                'code': 404
            }, status=status.HTTP_404_NOT_FOUND)
            
        # 获取所有可用问卷的简要信息
        available_surveys = [{
            'id': s.id,
            'title': s.title,
            'is_default': s.is_default,
            'status': s.status,
            'has_submitted': SurveyResponse.objects.filter(student=student, survey=s).exists()
        } for s in surveys]
        
        data = {
            'available_surveys': available_surveys
        }
        
        return Response({
            'status': 'success',
            'message': '获取成功',
            'code': 200,
            'data': data
        })
        
    except Student.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '学生信息不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'false',
            'message': str(e),
            'code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_survey(request):
    """提交问卷"""
    try:
        # 获取问卷ID
        survey_id = request.data.get('survey_id')
        if not survey_id:
            return Response({
                'status': 'false',
                'message': '问卷ID不能为空',
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # 获取问卷
        survey = Survey.objects.filter(id=survey_id, is_active=True).first()
        if not survey:
            return Response({
                'status': 'false',
                'message': '问卷不存在或未激活',
                'code': 404
            }, status=status.HTTP_404_NOT_FOUND)
            
        # 检查问卷是否可以提交
        if not survey.can_submit:
            return Response({
                'status': 'false',
                'message': f'问卷当前状态为：{survey.status}，无法提交',
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # 获取学生信息（使用学号）
        student = Student.objects.get(student_no=request.user.username)
        
        # 检查是否已提交
        if SurveyResponse.objects.filter(student=student, survey=survey).exists():
            return Response({
                'status': 'false',
                'message': '您已提交过该问卷',
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # 创建问卷回答
        response = SurveyResponse.objects.create(
            survey=survey,
            student=student,
            name=student.username,
            student_no=student.student_no,
            class_name=student.classs.name,
            phone=student.phone,
            future_plan=request.data['future_plan'],
            employment_type=request.data.get('employment_type'),
            city_preference=request.data.get('city_preference'),
            expected_salary=request.data.get('expected_salary'),
            job_market_view=request.data.get('job_market_view'),
            study_type=request.data.get('study_type'),
            target_school=request.data.get('target_school'),
            study_plan_status=request.data.get('study_plan_status')
        )
        
        serializer = SurveyResponseSerializer(response)
        return Response({
            'status': 'success',
            'message': '提交成功',
            'code': 200,
            'data': serializer.data
        })
        
    except Student.DoesNotExist:
        return Response({
            'status': 'false',
            'message': '学生信息不存在',
            'code': 404
        }, status=status.HTTP_404_NOT_FOUND)
    except KeyError as e:
        return Response({
            'status': 'false',
            'message': f'缺少必要字段：{str(e)}',
            'code': 400
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'false',
            'message': str(e),
            'code': 500,
            'detail': {
                'error': str(e),
                'user': request.user.username if request.user else None,
                'auth': str(request.auth) if hasattr(request, 'auth') else None
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 