import requests
import time

# --------------- 你自己填这 3 个信息 ---------------
YOUR_TOKEN = "pat_GvzG7urToB67hUiNrAKECo9HRUtev9VLXo0VcUiX6FRakadcPToU0Y2LPJDdktYs"
YOUR_BOT_ID = "7624531097216630818"
YOUR_USER_ID = "123123"
# ---------------------------------------------------

def test_coze():
    headers = {
        "Authorization": f"Bearer {YOUR_TOKEN}",
        "Content-Type": "application/json"
    }

    # 1. 创建对话（你官方给的，正确）
    url = "https://api.coze.cn/v3/chat"
    payload = {
        "bot_id": YOUR_BOT_ID,
        "user_id": YOUR_USER_ID,
        "stream": False,
        "auto_save_history": True,
        "additional_messages": [{"role": "user", "content": "早上好", "content_type": "text"}]
    }

    print("发送问题中...")
    resp = requests.post(url, json=payload, headers=headers)
    data = resp.json()
    print("创建成功：", data)

    chat_id = data["data"]["id"]
    conversation_id = data["data"]["conversation_id"]

    # 2. 等待生成
    print("\n等待 AI 生成...")
    time.sleep(4)

    # ==============================================
    # ✅ ✅ ✅ 这才是 V3 正确获取答案的接口！！！
    # ==============================================
    result_url = "https://api.coze.cn/v3/chat/message/list"
    params = {
        "conversation_id": conversation_id,
        "chat_id": chat_id
    }

    res = requests.get(result_url, headers=headers, params=params)
    result_data = res.json()

    print("\n===== 最终返回答案 =====")
    print(result_data)

if __name__ == "__main__":
    test_coze()