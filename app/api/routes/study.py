from fastapi import APIRouter, HTTPException
import os
from pathlib import Path

router = APIRouter(prefix="/study", tags=["研学手册"])

STUDY_DIR = Path("static/study")

@router.get("/images")
async def get_study_images():
    if not STUDY_DIR.exists():
        raise HTTPException(status_code=404, detail="研学手册目录不存在")
    files = []
    for f in os.listdir(STUDY_DIR):
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            files.append(f)
    files.sort(key=lambda x: int(''.join([c for c in x if c.isdigit()])))
    images = [f"/static/study/{f}" for f in files]
    return {"images": images}