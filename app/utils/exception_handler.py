from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import NotAuthenticated

def custom_exception_handler(exc, context):
    # 首先调用 REST framework 默认的异常处理
    response = exception_handler(exc, context)

    if response is None:
        # 如果 REST framework 没有处理这个异常，我们自己处理
        if isinstance(exc, Exception):
            return Response({
                'status': 'false',
                'message': str(exc),
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response

    # 处理认证相关的异常
    if isinstance(exc, (NotAuthenticated, InvalidToken, TokenError)):
        response.data = {
            'status': 'false',
            'message': '身份认证信息未提供或已过期',
            'code': response.status_code
        }
    else:
        # 统一响应格式
        response.data = {
            'status': 'false',
            'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
            'code': response.status_code
        }

    return response