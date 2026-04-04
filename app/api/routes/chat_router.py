from fastapi import APIRouter, Query
import requests
import time
from app.api.core.config import settings

router = APIRouter()


@router.post("/chat/qiaoxiang_ai")
async def qiaoxiang_ai(query: str = Query(...)):
    try:
        headers = {
            "Authorization": f"Bearer {settings.COZE_API_KEY}",
            "Content-Type": "application/json"
        }

        url = "https://api.coze.cn/v3/chat"
        payload = {
            "bot_id": settings.COZE_BOT_ID,
            "user_id": "user123",
            "stream": False,
            "auto_save_history": True,
            "additional_messages": [
                {"role": "user", "content": query, "content_type": "text"}
            ]
        }

        resp = requests.post(url, json=payload, headers=headers)
        data = resp.json()

        chat_id = data["data"]["id"]
        conversation_id = data["data"]["conversation_id"]

        time.sleep(50)

        msg_url = "https://api.coze.cn/v3/chat/message/list"
        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id
        }

        res = requests.get(msg_url, headers=headers, params=params)
        result = res.json()

        answer = "生成失败"
        for msg in result.get("data", []):
            if msg.get("role") == "assistant" and msg.get("type") == "answer":
                answer = msg.get("content", "生成失败")
                break

        return {"code": 200, "answer": answer}

    except Exception as e:
        return {"code": 500, "answer": "服务异常，请稍后重试"}