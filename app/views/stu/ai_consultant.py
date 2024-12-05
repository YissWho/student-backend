from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from ...utils.ernie_bot import ErnieBot

ernie_bot = ErnieBot(
    api_key=settings.ERNIE_BOT['API_KEY'],
    secret_key=settings.ERNIE_BOT['SECRET_KEY']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_ai(request):
    """与AI进行对话"""
    try:
        # 获取用户消息
        message = request.data.get('message')
        if not message:
            return Response({
                'status': 'error',
                'message': '消息不能为空',
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)

        # 构造消息格式
        messages = [
            {
                "role": "user",
                "content": message
            }
        ]
        
        # 调用API
        response = ernie_bot.chat(messages)
            
        # 处理API响应
        if 'result' in response:
            return Response({
                'status': 'success',
                'code': 200,
                'data': {
                    'reply': response['result']
                }
            })
        else:
            return Response({
                'status': 'error',
                'message': '获取回复失败',
                'code': 500,
                'error': response.get('error_msg', '未知错误')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e),
            'code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 