import requests
from app.api.core.config import settings

async def call_coze_agent(query: str):
    headers = {
        "Authorization": f"Bearer {settings.COZE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "bot_id": settings.COZE_BOT_ID,
        "user": "user",
        "stream": False,
        "messages": [
            {"role": "user", "content": query}
        ]
    }

    try:
        resp = requests.post(settings.COZE_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"智能问答服务异常：{str(e)}"