import os
import uuid
from pathlib import Path

BASE = Path("./app/api/storage")
MD_DIR = BASE / "markdown"
IMG_DIR = BASE / "chat_files"
MD_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR.mkdir(parents=True, exist_ok=True)

def save_md(title: str, content: str):
    name = f"{uuid.uuid4().hex}_{title.replace(' ','_')}.md"
    path = MD_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return str(path)

def save_image(file_bytes: bytes, suffix: str):
    name = f"{uuid.uuid4().hex}.{suffix}"
    path = IMG_DIR / name
    with open(path, "wb") as f:
        f.write(file_bytes)
    return f"http://127.0.0.1:8090/storage/chat_files/{name}"
def save_file(data: bytes, suffix: str) -> str:
    name = f"{uuid.uuid4().hex}.{suffix}"
    path = IMG_DIR / name
    with open(path, "wb") as f:
        f.write(data)
    # ✅ 只返回相对路径！！！（关键）
    return f"/storage/chat_files/{name}"