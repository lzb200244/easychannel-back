# -*- coding: utf-8 -*-
"""
    @Time：2023/8/19
    @Author：斑斑砖
    Description：
        
"""
import logging
import os

import requests
import json

API_KEY = "DkwQvlaU7UCC1AjePmP8WM9m"
SECRET_KEY = "BI7ZAygnQ6ZSnKTw8YDUZhGeHp40k4jq"

logger = logging.getLogger('chat')


class BaiDuGPT:
    # 模型
    MODELS = {
        # 0.012元/千tokens
        "ERNIE-Bot": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=",
        # 0.008元/千tokens
        "ERNIE-Bot-turbo": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token="
    }
    session = requests.Session()  # 创建一个会话,连接复用

    def __init__(self, model="ERNIE-Bot-turbo"):
        self.api_key = os.getenv('BAIDU_API_KEY', API_KEY)
        self.secret_key = os.getenv('BAIDU_API_SECRET', SECRET_KEY)
        self.model = model

    def get_access_token(self):
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": self.api_key, "client_secret": self.secret_key}
        return str(self.session.post(url, params=params).json().get("access_token"))

    def chat(self, message) -> dict:
        payload = json.dumps({
            "messages": [

                {
                    "role": "user",
                    "content": f"我给你命名你叫AI慧聊，以下是我的问题：{message}"
                },
            ]
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = self.session.request(
            "POST", self.MODELS.get(self.model) + self.get_access_token(),
            headers=headers, data=payload)

        aso = response.text
        results = json.loads(aso)
        # print(results)
        try:

            """
                        
                {
                  "id": "as-bcmt5ct4iy",
                  "object": "chat.completion",
                  "created": 1680167072,
                  "result": "您好，我是百度研发的知识增强大语言模型，中文名是文心一言，英文名是ERNIE Bot。我能够与人对话互动，回答问题，协助创作，高效便捷地帮助人们获取信息、知识和灵感。",
                  "is_truncated":false,
                  "need_clear_history": false,
                  "usage": {
                    "prompt_tokens": 7,
                    "completion_tokens": 67,
                    "total_tokens": 74
                  }
                }
            """
            # print(results)
            result = results['result']
            total_tokens = results['usage']['total_tokens']
        except Exception as e:
            logger.warning(e)
            """
                {
                  "error_code": 110,
                  "error_msg": "Access token invalid or no longer valid"
                }
            """
            return {
                "result": "gpt次数用尽",
                "total_tokens": 0
            }

        return {
            "result": result,
            "total_tokens": total_tokens
        }

    def chat_mul(self, message, question):
        """交流式调用"""

        payload = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": "我叫AI慧聊"
                },
                {
                    "role": "assistant",
                    "content": message
                },
                {
                    "role": "user",
                    "content": question
                },

            ]
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = self.session.request(
            "POST", self.MODELS.get(self.model) + self.get_access_token(),
            headers=headers, data=payload)
        aso = response.text
        results = json.loads(aso)
        try:
            result = results['result']
            total_tokens = results['usage']['total_tokens']
        except Exception as e:
            logger.warning(e)

            return {
                "result": "gpt次数用尽",
                "total_tokens": 0
            }

        return {
            "result": result,
            "total_tokens": total_tokens
        }


GPT = BaiDuGPT()
if __name__ == '__main__':
    print(GPT.chat("你要询问AI的内容"))
