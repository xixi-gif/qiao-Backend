import os
import uuid
from fastapi import UploadFile, HTTPException
from app.api.core.config import settings

# 修正：用后缀名而非完整类型，且和config中的配置对齐
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt"}
UPLOAD_DIR = settings.upload_dir or "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload_file(file: UploadFile) -> dict:
    # 校验文件大小
    if file.size > settings.max_file_size:
        raise HTTPException(status_code=400, detail=f"文件大小不能超过{settings.max_file_size / 1024 / 1024}MB")

    # 提取文件后缀（兼容无后缀的情况）
    file_name = file.filename or ""
    file_ext = os.path.splitext(file_name)[1].lower()
    if not file_ext or file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型，仅允许：{', '.join(ALLOWED_EXTENSIONS)}")

    # 生成唯一文件名，避免重复
    unique_name = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    file_path = os.path.abspath(file_path)

    try:
        # 写入文件（异步读取）
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败：{str(e)}")

    # 拼接可访问的文件URL（base_url已在config中定义）
    return {
        "name": file.filename,
        "url": f"{settings.base_url}/{UPLOAD_DIR}/{unique_name}"
    }