import requests
from datetime import datetime, timedelta
import json

class ErnieBot:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None
        self.token_expires = None
        self.base_url = "https://aip.baidubce.com"

    def get_access_token(self):
        """获取access_token"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token

        url = f"{self.base_url}/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }

        response = requests.post(url, params=params)
        result = response.json()

        if 'access_token' in result:
            self.access_token = result['access_token']
            # 设置token过期时间（提前5分钟过期）
            self.token_expires = datetime.now() + timedelta(seconds=result.get('expires_in', 2592000) - 300)
            return self.access_token
        else:
            raise Exception("获取access_token失败")

    def chat(self, messages):
        """调用对话接口"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={access_token}"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        payload = {
            "messages": messages
        }

        response = requests.post(url, headers=headers, json=payload)
        return response.json()

    def get_job_advice(self, student_info):
        """获取就业建议"""
        messages = [
            {
                "role": "user",
                "content": f"我是一名大学生，以下是我的基本情况：\n"
                          f"专业：{student_info.get('major', '计算机科学')}\n"
                          f"意向就业地区：{student_info.get('province', '未指定')}\n"
                          f"请给我一些就业建议，包括：\n"
                          f"1. 适合的职业方向\n"
                          f"2. 需要准备的技能\n"
                          f"3. 就业市场分析\n"
                          f"4. 薪资水平预估"
            }
        ]
        return self.chat(messages)

    def get_study_advice(self, student_info):
        """获取升学建议"""
        messages = [
            {
                "role": "user",
                "content": f"我是一名大学生，以下是我的基本情况：\n"
                          f"专业：{student_info.get('major', '计算机科学')}\n"
                          f"意向升学地区：{student_info.get('province', '未指定')}\n"
                          f"意向院校：{student_info.get('school', '未指定')}\n"
                          f"请给我一些升学建议，包括：\n"
                          f"1. 院校选择建议\n"
                          f"2. 专业方向建议\n"
                          f"3. 考研准备建议\n"
                          f"4. 未来发展前景"
            }
        ]
        return self.chat(messages) 