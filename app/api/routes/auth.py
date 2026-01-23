from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.api.schemas.user import UserCreate, UserLogin, VerifyCodeRequest, ResetPasswordRequest, Token, UserProfileResponse
from app.api.crud.user import (
    get_user_by_phone, get_user_by_username, create_user,
    authenticate_user, create_verify_code, verify_code, reset_password, get_user_by_id
)
from app.api.services.auth import create_token_response, get_current_user, oauth2_scheme
from app.api.services.sms import send_sms
from app.api.db.database import get_db
from app.api.core.logging_config import logger

router = APIRouter()

@router.post("/register", summary="用户注册")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_phone(db, user.phone):
        raise HTTPException(status_code=400, detail="手机号已注册")
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = create_user(db, user)
    return {"code": 200, "message": "注册成功",
            "data": {"username": user.username, "phone": user.phone, "role": user.role.value}}

@router.post("/login", response_model=Token, summary="用户登录")
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_login.phone, user_login.password)
    if not user:
        raise HTTPException(status_code=401, detail="手机号或密码错误")
    if user.role.value != user_login.role:
        raise HTTPException(status_code=403, detail="角色不匹配")

    return create_token_response(user)

@router.post("/send-verify-code", summary="发送验证码（功能待定）")
def send_verify_code(request: VerifyCodeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if request.type == "forgot_password":
        if not get_user_by_phone(db, request.phone):
            raise HTTPException(status_code=400, detail="手机号未注册")

    db_code = create_verify_code(db, request.phone, request.type)
    background_tasks.add_task(send_sms, request.phone, db_code.code)

    return {"code": 200, "message": "验证码发送成功"}

@router.post("/reset-password", summary="重置密码")
def reset_password_api(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    if not verify_code(db, request.phone, request.code, "forgot_password"):
        raise HTTPException(status_code=400, detail="验证码无效或已过期")

    if not reset_password(db, request):
        raise HTTPException(status_code=400, detail="重置密码失败")

    return {"code": 200, "message": "密码重置成功"}

# @router.get("/profile", response_model=UserProfileResponse, summary="获取当前用户个人信息")
# def get_user_profile(current_user = Depends(get_current_user)):
#       return current_user

@router.get("/profile", response_model=UserProfileResponse, summary="获取当前用户个人信息")
def get_user_profile(current_user = Depends(get_current_user)):

    return {
        "id": current_user.id,
        "username": current_user.username,
        "phone": current_user.phone,
        "role": current_user.role.value,
    }