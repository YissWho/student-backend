from django.urls import path
from .views.stu import auth as student_auth, student, notice, ai_consultant, survey as student_survey
from .views.teacher import auth as teacher_auth, profile as teacher_profile, manage as teacher_manage, manage_class as teacher_manage_class, manage_notice as teacher_manage_notice, statistics as teacher_statistics, survey as teacher_survey
from .views.all import all as all_views

urlpatterns = [
    # 公共接口
    path('common/captcha/', all_views.get_captcha),  # 获取验证码
    path('common/classes/', all_views.get_all_classes),  # 获取所有班级
    path('common/teachers/', all_views.get_all_teachers),  # 获取所有教师
    path('common/teacher/<int:teacher_id>/classes/', all_views.get_teacher_classes),  # 获取教师管理的班级
    # 刷新token,待实现
    path('common/refresh/token/', all_views.refresh_token),  # 刷新token
    # 学生相关
    path('student/login/', student_auth.student_login),
    path('student/register/', student_auth.student_register),
    path('student/profile/', student.update_profile),
    path('student/profile/<int:student_id>/', student.get_student),
    path('student/profile/me/', student.get_student),
    path('student/classmates/', student.get_classmates, name='get_classmates'),
    path('student/change/password/', student.change_password),  # 学生修改密码
    
    # 学生问卷相关
    path('student/survey/', student_survey.get_survey),  # 获取问卷
    path('student/survey/submit/', student_survey.submit_survey),  # 提交问卷
    
    # 学生通知相关
    path('student/notices/', notice.notice_list),
    path('student/notices/read/', notice.mark_notice_as_read),  # 批量标记已读
    path('student/notices/read/<int:notice_id>/', notice.mark_notice_as_read),  # 单个标记已读
    
    path('student/ai/chat/', ai_consultant.chat_with_ai),  # AI聊天
    
    # 教师相关
    path('teacher/login/', teacher_auth.teacher_login),  # 教师登录
    path('teacher/profile/', teacher_profile.teacher_profile),  # 获取/更新教师信息
    path('teacher/change/password/', teacher_profile.change_password),  # 修改密码
    
    # 教师问卷相关
    path('teacher/survey/stats/', teacher_survey.get_survey_stats),  # 获取问卷统计
    path('teacher/survey/<int:survey_id>/detail/', teacher_survey.get_survey_detail),  # 获取问卷详情
    path('teacher/survey/<int:survey_id>/students/', teacher_survey.get_survey_students),  # 获取问卷学生列表
    path('teacher/survey/<int:survey_id>/student/<int:student_no>/', teacher_survey.get_student_survey_response),  # 获取学生问卷情况
    
    path('teacher/students/', teacher_manage.student_list),  # 获取学生列表
    path('teacher/students/create/', teacher_manage.create_student),  # 创建学生
    path('teacher/students/<int:student_id>/', teacher_manage.student_detail),  # 获取/更新/删除学生
    
    path('teacher/classes/', teacher_manage_class.class_list),  # 获取班级列表
    path('teacher/classes/create/', teacher_manage_class.create_class),  # 创建班级
    path('teacher/classes/<int:class_id>/', teacher_manage_class.class_detail),  # 获取/更新/删除班级
    
    path('teacher/notices/', teacher_manage_notice.notice_list),  # 获取通知列表
    path('teacher/notices/create/', teacher_manage_notice.create_notice),  # 创建通知
    path('teacher/notices/<int:notice_id>/', teacher_manage_notice.notice_detail),  # 获取/更新/删除通知
    path('teacher/notices/<int:notice_id>/read/students/', teacher_manage_notice.notice_read_students),  # 获取已读学生列表
    path('teacher/notices/<int:notice_id>/unread/students/', teacher_manage_notice.notice_unread_students),  # 获取未读学生列表
    
    path('teacher/stats/class/count/', teacher_statistics.class_student_count),  # 班级人数统计
    path('teacher/stats/employment/', teacher_statistics.class_employment_stats),  # 就业升学统计
    path('teacher/stats/status/ratio/', teacher_statistics.overall_status_ratio),  # 总体就业升学比例
    path('teacher/stats/province/wordcloud/', teacher_statistics.province_wordcloud),  # 省份词云
    path('teacher/stats/province/map/', teacher_statistics.province_map_data),  # 省份地图数据
]
