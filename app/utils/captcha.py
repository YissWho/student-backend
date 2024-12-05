import random
import string
from captcha.image import ImageCaptcha
import base64
from io import BytesIO
from django.core.cache import cache

class CaptchaHelper:
    @staticmethod
    def generate_code(length=6):
        """生成指定长度的随机数字验证码"""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def generate_captcha(code):
        """生成验证码图片"""
        image = ImageCaptcha(width=160, height=60)
        # 生成图片数据
        data = image.generate(code)
        # 转换为base64
        image_bytes = BytesIO()
        image.write(code, image_bytes, 'png')
        image_base64 = base64.b64encode(image_bytes.getvalue()).decode()
        return f"data:image/png;base64,{image_base64}"
    
    @staticmethod
    def save_code(key, code, timeout=300):  # 5分钟过期
        """保存验证码到缓存"""
        cache.set(f"captcha_{key}", code, timeout)
    
    @staticmethod
    def verify_code(key, code):
        """验证验证码"""
        if not code:
            return False
        saved_code = cache.get(f"captcha_{key}")
        if not saved_code:
            return False
        # 验证成功后删除缓存
        cache.delete(f"captcha_{key}")
        """ 验证码不区分大小写 """
        return saved_code.lower() == code.lower()
    
    @classmethod
    def generate_and_save(cls, key, timeout=300):
        """生成验证码并保存到缓存"""
        code = cls.generate_code()
        """ 生成验证码图片 """
        image = cls.generate_captcha(code)
        cls.save_code(key, code, timeout)
        return {
            'key': key,
            'image': image
        } 