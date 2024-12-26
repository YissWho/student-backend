from django.contrib.auth.hashers import make_password, check_password
import os
import time
from django.db import models
from django.utils import timezone

def get_file_path(instance, filename):
    # 获取文件扩展名
    ext = filename.split('.')[-1]
    # 生成时间戳
    timestamp = int(time.time() * 1000)
    # 根据实例类型决定路径
    if isinstance(instance, Student):
        path = 'avatars/student'
    else:
        path = 'avatars/teacher'
    # 返回 'avatars/student/时间戳.jpg' 或 'avatars/teacher/时间戳.jpg'
    return os.path.join(path, f'{timestamp}.{ext}')

role = (
    (0, '老师'),
    (1, '学生'),
)


class Teacher(models.Model):
    username = models.CharField(verbose_name='用户名', max_length=50, unique=True)
    phone = models.CharField(max_length=50, verbose_name='手机号', unique=True)
    password = models.CharField(verbose_name='密码', max_length=100)
    avatar = models.ImageField(upload_to=get_file_path,
                             default='defaults/default_img.png',
                             null=True, blank=True,
                             verbose_name='头像')
    role = models.IntegerField(verbose_name='角色', choices=role, default=0)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "老师"
        verbose_name_plural = "老师"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class Class(models.Model):
    name = models.CharField(verbose_name='班级名', max_length=50, unique=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="负责的老师")
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "班级"
        verbose_name_plural = "班级"


class Notice(models.Model):
    title = models.CharField(verbose_name="标题", max_length=200)
    content = models.TextField(verbose_name="内容")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='notices')
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    is_read = models.BooleanField(verbose_name="是否已读", default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "通知"
        verbose_name_plural = "通知"


provinces = (
    (0, '北京市'),
    (1, '天津市'),
    (2, '河北省'),
    (3, '山西省'),
    (4, '内蒙古自治区'),
    (5, '辽宁省'),
    (6, '吉林省'),
    (7, '黑龙江省'),
    (8, '上海市'),
    (9, '江苏省'),
    (10, '浙江省'),
    (11, '安徽省'),
    (12, '福建省'),
    (13, '江西省'),
    (14, '山东省'),
    (15, '河南省'),
    (16, '湖北省'),
    (17, '湖南省'),
    (18, '广东省'),
    (19, '广西壮族自治区'),
    (20, '海南省'),
    (21, '重庆市'),
    (22, '四川省'),
    (23, '贵州省'),
    (24, '云南省'),
    (25, '西藏自治区'),
    (26, '陕西省'),
    (27, '甘肃省'),
    (28, '青海省'),
    (29, '宁夏回族自治区'),
    (30, '新疆维吾尔自治区'),
    (31, '台湾省'),
    (32, '香港特别行政区'),
    (33, '澳门特别行政区')
)


class Student(models.Model):
    student_no = models.CharField(max_length=50, unique=True, verbose_name='学号')
    username = models.CharField(max_length=50, verbose_name='用户名')
    phone = models.CharField(max_length=50, verbose_name='手机号', unique=True)
    password = models.CharField(max_length=100, verbose_name='密码')
    classs = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students', verbose_name='所在班级')
    avatar = models.ImageField(upload_to=get_file_path,
                             default='defaults/default_img.png',
                             null=True, blank=True,
                             verbose_name='头像')
    status = models.IntegerField(verbose_name="毕业去向", 
                               choices=((0, '就业'), (1, '考研')), 
                               null=True, blank=True)
    province = models.IntegerField(verbose_name="意向地区",
                                 help_text="就业学生填写就业意向地区，升学学生填写升学意向地区",
                                 choices=provinces,
                                 null=True, blank=True)
    study_school = models.CharField(verbose_name="升学院校",
                                  help_text="仅升学学生需填写",
                                  max_length=100,
                                  null=True, blank=True)
    study_major = models.CharField(verbose_name="升学专业",
                                 help_text="仅升学学生需填写",
                                 max_length=100,
                                 null=True, blank=True)
    role = models.IntegerField(verbose_name='角色', choices=role, default=1)
    is_read = models.IntegerField(verbose_name="通知状态", choices=((0, '未读'), (1, '已读')), default=0)
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    read_notices = models.ManyToManyField(Notice, verbose_name="已读通知", blank=True, related_name='read_by_students')

    class Meta:
        verbose_name = '学生'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.username}({self.student_no})'

    @property
    def province_display(self):
        """获取地区显示名称"""
        return dict(provinces).get(self.province, '')

    @property
    def status_display(self):
        """获取状态显示名称"""
        return dict(((0, '就业'), (1, '升学'))).get(self.status, '')

    @property
    def province_type(self):
        """获取地区类型描述"""
        return '就业意向地区' if self.status == 0 else '升学意向地区'

    def clean(self):
        """数据验证"""
        from django.core.exceptions import ValidationError
        # 就业状态时，升学信息必须为空
        if self.status == 0 and (self.study_school or self.study_major):
            raise ValidationError('就业状态下不能填写升学信息')
        # 升学状态时，升学信息必须填写
        elif self.status == 1 and (not self.study_school or not self.study_major):
            raise ValidationError('升学状态下必须填写升学院校和专业')

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class Survey(models.Model):
    """问卷模型"""
    title = models.CharField(verbose_name='标题', max_length=100, default="学生信息调查问卷")
    description = models.TextField(verbose_name='描述', blank=True, null=True)
    is_active = models.BooleanField(verbose_name='是否激活', default=True)
    is_default = models.BooleanField(verbose_name='是否为默认问卷', default=False)
    start_time = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_time = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        verbose_name = '问卷'
        verbose_name_plural = verbose_name
        db_table = 'survey'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # 如果当前问卷被设置为默认问卷，则将其他问卷的默认状态取消
        if self.is_default:
            Survey.objects.exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def status(self):
        """获取问卷状态"""
        now = timezone.now()
        if not self.is_active:
            return '未激活'
        if self.start_time and now < self.start_time:
            return '未开始'
        if self.end_time and now > self.end_time:
            return '已结束'
        return '进行中'

    @property
    def can_submit(self):
        """判断问卷是否可以提交"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        return True


class SurveyResponse(models.Model):
    """问卷回答模型"""    
    PLAN_CHOICES = [
        (0, '就业'),
        (1, '升学深造')
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        (0, '考公'),
        (1, '考编'),
        (2, '企业应聘'),
        (3, '自主创业')
    ]
    
    CITY_PREFERENCE_CHOICES = [
        (0, '一线城市(如北京、上海、广州、深圳)'),
        (1, '二线城市(如杭州、成都、武汉)'),
        (2, '学校附近'),
        (3, '家乡')
    ]
    
    SALARY_RANGE_CHOICES = [
        (0, '5000元以下'),
        (1, '5000-10000元'),
        (2, '10000元以上')
    ]
    
    JOB_MARKET_VIEW_CHOICES = [
        (0, '乐观'),
        (1, '正常'),
        (2, '就业难'),
        (3, '不了解')
    ]
    
    STUDY_TYPE_CHOICES = [
        (0, '保研(已录取院校)'),
        (1, '考研(拟报考院校)'),
        (2, '境外高校(拟申报院校)')
    ]
    
    STUDY_PLAN_STATUS_CHOICES = [
        (0, '已在实施计划'),
        (1, '有计划未实施'),
        (2, '未定计划')
    ]
    
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses', verbose_name='关联问卷')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='survey_responses', verbose_name='学生')
    
    # 基本信息
    name = models.CharField(verbose_name='姓名', max_length=50)
    student_no = models.CharField(verbose_name='学号', max_length=20)
    class_name = models.CharField(verbose_name='班级', max_length=50)
    phone = models.CharField(verbose_name='联系电话', max_length=11)
    
    # 毕业去向
    future_plan = models.IntegerField(verbose_name='毕业去向', choices=PLAN_CHOICES)
    
    # 就业相关信息（如果选择就业）
    employment_type = models.IntegerField(
        verbose_name='就业方式',
        choices=EMPLOYMENT_TYPE_CHOICES,
        blank=True,
        null=True
    )
    city_preference = models.IntegerField(
        verbose_name='就业城市倾向',
        choices=CITY_PREFERENCE_CHOICES,
        blank=True,
        null=True
    )
    expected_salary = models.IntegerField(
        verbose_name='期望月薪',
        choices=SALARY_RANGE_CHOICES,
        blank=True,
        null=True
    )
    job_market_view = models.IntegerField(
        verbose_name='就业形势看法',
        choices=JOB_MARKET_VIEW_CHOICES,
        blank=True,
        null=True
    )
    
    # 升学相关信息（如果选择升学）
    study_type = models.IntegerField(
        verbose_name='升学方式',
        choices=STUDY_TYPE_CHOICES,
        blank=True,
        null=True
    )
    target_school = models.CharField(
        verbose_name='院校名称',
        max_length=100,
        blank=True,
        null=True
    )
    study_plan_status = models.IntegerField(
        verbose_name='备考计划',
        choices=STUDY_PLAN_STATUS_CHOICES,
        blank=True,
        null=True
    )
    
    submitted_at = models.DateTimeField(verbose_name='提交时间', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        verbose_name = '问卷回答'
        verbose_name_plural = verbose_name
        db_table = 'survey_response'
        # 添加联合唯一约束，确保一个学生只能对一个问卷提交一次回答
        unique_together = ['student', 'survey']

    def __str__(self):
        return f"{self.student.username}的问卷回答"