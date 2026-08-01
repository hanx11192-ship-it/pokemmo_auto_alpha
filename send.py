import requests
import os
from datetime import datetime

def get_current_period_str():
    hour = datetime.now().hour
    if 8 <= hour < 14:
        return "8-14"
    elif 14 <= hour < 22:
        return "14-22"
    elif hour >= 22 or hour < 2:
        return "22-2"
    else:
        return "2-8"

def send(content, summary=None):
    """
    发送消息到wxpushee。
    content: 消息正文
    summary: 可选摘要，若不提供则根据当前时段自动生成
    """
    if summary is None:
        t = get_current_period_str()
        if t == "8-14":
            summary = "早头"
        elif t == "14-20":
            summary = "午头"
        elif t == "20-2":
            summary = "晚头"
        else:
            summary = "凌晨头"

    app_token = os.environ.get("WXPUSHER_APP_TOKEN_alpha")
    if not app_token:
        print("错误：环境变量 WXPUSHER_APP_TOKEN 未设置")
        return

    url = "https://wxpusher.zjiecode.com/api/send/message"
    data = {
        "appToken": app_token,
        "content": content,
        "summary": summary,
        "contentType": 1,
        "topicIds": [45385]
    }
    try:
        response = requests.post(url, json=data)
        print("发送结果：", response.json())
    except Exception as e:
        print(f"发送请求失败：{e}")