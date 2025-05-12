from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from app.models import Student
from app.serializers.student import StudentRegisterSerializer, StudentLoginSerializer
from django.contrib.auth.models import User
from app.utils.captcha import CaptchaHelper


@api_view(["POST"])
@permission_classes([AllowAny])
def student_register(request):
    serializer = StudentRegisterSerializer(data=request.data)
    try:
        if serializer.is_valid():
            # 移除确认密码字段w
            validated_data = serializer.validated_data
            validated_data.pop("confirm_password")

            # 创建新学生
            student = Student(**validated_data)
            student.set_password(validated_data["password"])
            student.save()

            # 创建对应的 Django User
            User.objects.create(username=student.student_no, is_active=True)

            return Response(
                {"code": 200, "status": "success", "message": "注册成功"},
                status=status.HTTP_201_CREATED,
            )

        # 处理验证错误
        error_msg = ""
        if "student_no" in serializer.errors:
            error_msg = serializer.errors["student_no"][0]
        elif "phone" in serializer.errors:
            error_msg = serializer.errors["phone"][0]
        elif "password" in serializer.errors:
            error_msg = serializer.errors["password"][0]
        elif "confirm_password" in serializer.errors:
            error_msg = serializer.errors["confirm_password"][0]
        elif "non_field_errors" in serializer.errors:
            error_msg = serializer.errors["non_field_errors"][0]
        else:
            error_msg = "注册信息有误，请检查"

        return Response(
            {"code": 400, "status": "false", "message": error_msg},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        return Response(
            {"code": 500, "status": "false", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def student_login(request):
    """学生登录"""
    try:
        student_no = request.data.get("student_no")
        password = request.data.get("password")
        captcha_key = request.data.get("captcha_key")
        captcha_code = request.data.get("captcha_code")

        # 验证参数完整性
        if not all([student_no, password, captcha_key, captcha_code]):
            return Response(
                {"status": "false", "message": "请填写完整的登录信息", "code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 验证验证码
        if not CaptchaHelper.verify_code(captcha_key, captcha_code):
            return Response(
                {"status": "false", "message": "验证码错误或已过期", "code": 400},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            student = Student.objects.get(student_no=student_no)
        except Student.DoesNotExist:
            return Response(
                {"status": "false", "message": "学生不存在", "code": 404},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not student.check_password(password):
            return Response(
                {"status": "false", "message": "密码错误", "code": 401},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # 获取或创建对应的Django User对象
        # 使用get_or_create方法,如果用户不存在则创建新用户
        # username使用学生学号,email默认为空字符串
        user, created = User.objects.get_or_create(
            username=student.student_no, defaults={"email": ""}
        )

        # 如果是新创建的用户,需要设置密码并保存
        if created:
            user.set_password(password)  # 设置密码(会自动加密)
            user.save()  # 保存用户信息到数据库

        # 生成JWT token
        refresh = RefreshToken.for_user(user)
        # 添加自定义信息到token
        refresh["student_no"] = student.student_no
        refresh["role"] = student.role

        return Response(
            {
                "status": "success",
                "message": "登录成功",
                "code": 200,
                "data": {
                    "role": student.role,
                    "token": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": student.id,
                        "student_no": student.student_no,
                        "username": student.username,
                        "avatar": student.avatar.url if student.avatar else None,
                    },
                },
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"status": "false", "message": str(e), "code": 500},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
