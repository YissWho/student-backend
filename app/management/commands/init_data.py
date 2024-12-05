# from django.core.management.base import BaseCommand
# from django.db import transaction
# from app.models import Teacher, Class, Student, Notice
# import random

# class Command(BaseCommand):
#     help = '初始化数据库数据'

#     def handle(self, *args, **options):
#         self.stdout.write('开始初始化数据...')
        
#         try:
#             with transaction.atomic():
#                 # 创建教师
#                 self.stdout.write('创建教师...')
#                 teacher1 = Teacher.objects.create(
#                     username='张老师',
#                     phone='13800138001',
#                     role=0
#                 )
#                 teacher1.set_password('123456')
#                 teacher1.save()

#                 teacher2 = Teacher.objects.create(
#                     username='李老师',
#                     phone='13800138002',
#                     role=0
#                 )
#                 teacher2.set_password('123456')
#                 teacher2.save()

#                 # 创建班级
#                 self.stdout.write('创建班级...')
#                 class1 = Class.objects.create(
#                     name='计算机科学1班',
#                     teacher=teacher1
#                 )
                
#                 class2 = Class.objects.create(
#                     name='软件工程1班',
#                     teacher=teacher2
#                 )

#                 # 创建学生
#                 self.stdout.write('创建学生...')
#                 for i in range(1, 11):  # 创建10个学生
#                     student = Student.objects.create(
#                         student_no=f'2024{str(i).zfill(3)}',  # 学号格式：2024001-2024010
#                         username=f'学生{i}',
#                         phone=f'1380013{str(i).zfill(4)}',
#                         classs=class1 if i <= 5 else class2,  # 前5个分配到class1，后5个分配到class2
#                         status=random.choice([0, 1]),  # 随机分配就业或升学状态
#                         province=random.randint(0, 33),  # 随机分配意向省份
#                         study_school='示例大学' if i % 2 == 0 else None,
#                         study_major='计算机科学' if i % 2 == 0 else None
#                     )
#                     student.set_password('123456')
#                     student.save()

#                 # 创建通知
#                 self.stdout.write('创建通知...')
#                 Notice.objects.create(
#                     title='关于举办2024届毕业生就业双选会的通知',
#                     content='为促进2024届毕业生就业工作，学校定于2024年3月举办春季就业双选会...',
#                     teacher=teacher1
#                 )
                
#                 Notice.objects.create(
#                     title='2024届毕业生档案办理通知',
#                     content='请各位2024届毕业生于本月底前完成档案材料提交...',
#                     teacher=teacher2
#                 )

#                 self.stdout.write(self.style.SUCCESS('数据初始化成功！'))
                
#                 self.stdout.write('\n测试账号信息：')
#                 self.stdout.write('教师账号：')
#                 self.stdout.write('  手机号：13800138001  密码：123456')
#                 self.stdout.write('  手机号：13800138002  密码：123456')
#                 self.stdout.write('学生账号：')
#                 self.stdout.write('  学号：2024001-2024010  密码：123456')

#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f'初始化失败：{str(e)}'))
# import os
# import shutil
# from django.core.management.base import BaseCommand
# from django.conf import settings
# from app.models import Teacher, Class, Student, Notice


# class Command(BaseCommand):
#     help = '初始化基础数据'

#     def handle(self, *args, **options):
#         # 创建媒体文件夹结构
#         media_dirs = [
#             os.path.join(settings.MEDIA_ROOT, 'defaults'),
#             os.path.join(settings.MEDIA_ROOT, 'avatars'),
#             os.path.join(settings.MEDIA_ROOT, 'avatars/student'),
#             os.path.join(settings.MEDIA_ROOT, 'avatars/teacher'),
#         ]
#         for dir_path in media_dirs:
#             os.makedirs(dir_path, exist_ok=True)

#         # 复制默认头像
#         static_dir = os.path.join(settings.BASE_DIR, 'app', 'static', 'defaults')
#         os.makedirs(static_dir, exist_ok=True)

#         # 创建默认头像文件路径
#         default_avatar_path = os.path.join(static_dir, 'default_avatar.jpg')
#         default_teacher_avatar_path = os.path.join(static_dir, 'default_teacher_avatar.jpg')

#         # 如果默认头像不存在，创建简单的纯色头像
#         try:
#             from PIL import Image, ImageDraw

#             # 创建学生默认头像（蓝色）
#             if not os.path.exists(default_avatar_path):
#                 img = Image.new('RGB', (200, 200), color='#4A90E2')
#                 ImageDraw.Draw(img).text((70, 90), 'Student', fill='white')
#                 img.save(default_avatar_path)

#             # 创建教师默认头像（绿色）
#             if not os.path.exists(default_teacher_avatar_path):
#                 img = Image.new('RGB', (200, 200), color='#2ECC71')
#                 ImageDraw.Draw(img).text((70, 90), 'Teacher', fill='white')
#                 img.save(default_teacher_avatar_path)

#             # 复制到media目录
#             shutil.copy(default_avatar_path,
#                         os.path.join(settings.MEDIA_ROOT, 'defaults', 'default_avatar.jpg'))
#             shutil.copy(default_teacher_avatar_path,
#                         os.path.join(settings.MEDIA_ROOT, 'defaults', 'default_teacher_avatar.jpg'))

#         except Exception as e:
#             self.stdout.write(self.style.WARNING(f'创建默认头像失败: {str(e)}'))
from django.core.management.base import BaseCommand
from app.models import Teacher, Class, Student
import random
from faker import Faker
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '初始化基础数据'

    def __init__(self):
        super().__init__()
        self.fake = Faker(['zh_CN'])  # 使用中文faker

    def handle(self, *args, **kwargs):
        self.stdout.write('开始初始化数据...')
        
        try:
            # 创建教师
            teachers_data = [
                {
                    'username': '张明',
                    'phone': '13800138001',
                    'password': '123456',
                    'role': 0
                },
                {
                    'username': '李红',
                    'phone': '13800138002',
                    'password': '123456',
                    'role': 0
                },
                {
                    'username': '王建国',
                    'phone': '13800138003',
                    'password': '123456',
                    'role': 0
                }
            ]
            
            teachers = []
            for teacher_data in teachers_data:
                teacher, created = Teacher.objects.get_or_create(
                    phone=teacher_data['phone'],
                    defaults={
                        'username': teacher_data['username'],
                        'role': teacher_data['role']
                    }
                )
                if created:
                    teacher.set_password(teacher_data['password'])
                    teacher.save()
                teachers.append(teacher)
                self.stdout.write(f'教师 {teacher.username} {"创建" if created else "已存在"}')

            # 创建班级
            class_names = [
                '软件2101班', '软件2102班', '软件2103班',
                '计科2101班', '计科2102班',
                '物联网2101班', '物联网2102班', '物联网2103班',
                '大数据2101班'
            ]
            
            # 为每个教师分配2-3个班级
            teacher_classes = {
                teachers[0]: class_names[:3],  # 第一个老师管理3个班
                teachers[1]: class_names[3:6],  # 第二个老师管理3个班
                teachers[2]: class_names[6:],   # 第三个老师管理3个班
            }
            
            classes = []
            for teacher, class_list in teacher_classes.items():
                for class_name in class_list:
                    class_obj, created = Class.objects.get_or_create(
                        name=class_name,
                        defaults={'teacher': teacher}
                    )
                    classes.append(class_obj)
                    self.stdout.write(f'班级 {class_name} {"创建" if created else "已存在"}')

            # 生成学生
            # 常用姓氏列表
            surnames = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴', 
                       '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗']
            
            # 省份选择权重，使分布更真实
            province_weights = [
                (16, 30),  # 湖北省权重最高
                (15, 20),  # 河南省次之
                (9, 15),   # 江苏省
                (18, 15),  # 广东省
                (22, 10),  # 四川省
                (0, 5),    # 北京市
                (8, 5),    # 上海市
            ]
            
            # 为每个班级创建20-30个学生
            for class_obj in classes:
                # 决定这个班级的学生数量
                student_count = random.randint(20, 30)
                
                # 生成学号前缀（基于班级名称）
                year = '2021'  # 根据班级名称中的年份
                major_code = '01' if '软件' in class_obj.name else ('02' if '计科' in class_obj.name else '03')
                class_num = class_obj.name[-2:-1]  # 获取班级序号
                
                for i in range(student_count):
                    # 生成学号
                    student_no = f"{year}{major_code}{class_num}{str(i+1).zfill(2)}"
                    
                    # 生成姓名
                    surname = random.choice(surnames)
                    name = self.fake.name().replace(surname, '')  # 避免重复姓氏
                    username = surname + name[-2:]  # 取最后两个字
                    
                    # 生成手机号
                    phone = f"138{str(random.randint(0, 99999999)).zfill(8)}"
                    
                    # 决定学生去向
                    status = random.choices([0, 1], weights=[70, 30])[0]  # 70%就业，30%升学
                    
                    # 选择省份（使用权重）
                    province_choice = random.choices(
                        [p[0] for p in province_weights],
                        weights=[p[1] for p in province_weights]
                    )[0]
                    
                    # 如果是升学，生成学校和专业信息
                    study_school = None
                    study_major = None
                    if status == 1:
                        universities = [
                            '武汉大学', '华中科技大学', '浙江大学', '南京大学',
                            '上海交通大学', '复旦大学', '中国科学技术大学',
                            '北京大学', '清华大学', '同济大学'
                        ]
                        majors = [
                            '计算机科学与技术', '软件工程', '人工智能',
                            '数据科学与大数据技术', '网络空间安全',
                            '信息与通信工程', '电子信息工程'
                        ]
                        study_school = random.choice(universities)
                        study_major = random.choice(majors)
                    
                    student, created = Student.objects.get_or_create(
                        student_no=student_no,
                        defaults={
                            'username': username,
                            'phone': phone,
                            'password': '123456',  # 默认密码
                            'classs': class_obj,
                            'status': status,
                            'province': province_choice,
                            'study_school': study_school,
                            'study_major': study_major,
                            'role': 1
                        }
                    )
                    
                    if created:
                        student.set_password('123456')
                        student.save()
                        self.stdout.write(f'学生 {username}（{student_no}）创建成功')
                        
            self.stdout.write(self.style.SUCCESS('数据初始化完成！'))
            
        except Exception as e:
            logger.error(f"初始化数据时发生错误: {str(e)}", exc_info=True)
            self.stdout.write(self.style.ERROR(f'初始化数据失败: {str(e)}'))