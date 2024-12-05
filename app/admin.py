from django.contrib import admin
from django.utils.html import format_html
from .models import Student, Survey, SurveyResponse, Teacher, Class, Notice


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_no', 'username', 'phone', 'classs', 'status_display', 'show_avatar']
    list_filter = ['classs', 'status']
    search_fields = ['student_no', 'username', 'phone']
    list_per_page = 10

    def show_avatar(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50px" height="50px" style="border-radius: 50%;" />',
                               obj.avatar.url)
        return "无头像"

    show_avatar.short_description = '头像'


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['username', 'phone',"show_avatar"]
    search_fields = ['username', 'phone']
    list_per_page = 10
    def show_avatar(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50px" height="50px" style="border-radius: 50%;" />',
                               obj.avatar.url)
        return "无头像"

    show_avatar.short_description = '头像'


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'student_count']
    search_fields = ['name', 'teacher__username']
    list_per_page = 20

    def student_count(self, obj):
        return obj.students.count()  # 使用related_name='students'

    student_count.short_description = '学生数量'


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ["id",'title', 'teacher', 'created_at', 'read_count']
    list_filter = ['teacher', 'created_at']
    search_fields = ['title', 'content', 'teacher__username']
    list_per_page = 20

    def read_count(self, obj):
        return obj.read_by_students.count()  # 使用related_name='read_by_students'

    read_count.short_description = '已读人数'

@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['student', 'submitted_at']
    list_filter = ['submitted_at']
    search_fields = ['student__username']
    list_per_page = 20

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title']
    list_per_page = 20

# 自定义管理站点标题
admin.site.site_header = '学生信息管理系统'
admin.site.site_title = '学生信息管理系统'
admin.site.index_title = '管理面板'