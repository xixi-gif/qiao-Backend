from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.api.schemas.user import UserCreate, UserLogin, VerifyCodeRequest, ResetPasswordRequest, Token, UserProfileResponse, UserUpdateRequest
from app.api.crud.user import get_user_by_phone, get_user_by_username, create_user, authenticate_user, create_verify_code, verify_code, reset_password, get_user_by_id, update_user
from app.api.services.auth import create_token_response, get_current_user, get_current_merchant, oauth2_scheme
from app.api.services.sms import send_sms
from app.api.db.database import get_db
from app.api.core.logging_config import logger
from fastapi import File, UploadFile
import os
import uuid
from typing import Optional

router = APIRouter()

@router.post("/register", summary="用户注册")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_phone(db, user.phone):
        raise HTTPException(status_code=400, detail="手机号已注册")
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = create_user(db, user)
    return {"code": 200, "message": "注册成功", "data": {"username": user.username, "phone": user.phone, "role": user.role.value}}

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

@router.get("/profile", response_model=UserProfileResponse, summary="获取当前用户个人信息")
def get_user_profile(current_user=Depends(get_current_user)):
    if hasattr(current_user, 'role') and current_user.role is not None:
        current_user.role = current_user.role.value
    return current_user

@router.put("/profile", response_model=UserProfileResponse, summary="更新当前用户个人信息")
def update_user_profile(
    user_update: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    updated_user = update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户不存在或已被删除")
    logger.info(f"用户{current_user.id}更新个人信息成功")
    updated_user.role = updated_user.role.value
    return updated_user

@router.put("/merchant/profile", response_model=UserProfileResponse, summary="更新商家信息（仅商家）")
def update_merchant_profile(
    user_update: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_merchant=Depends(get_current_merchant)
):
    updated_merchant = update_user(db, current_merchant.id, user_update)
    if not updated_merchant:
        raise HTTPException(status_code=404, detail="商家不存在或已被删除")
    logger.info(f"商家{current_merchant.id}更新店铺信息成功")
    updated_merchant.role = updated_merchant.role.value
    return updated_merchant

@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...),db: Session = Depends(get_db),current_user = Depends(get_current_user)):
    try:
        contents = await file.read()
        if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            raise HTTPException(status_code=400,detail="只支持 png、jpg、jpeg")
        if len(contents) > 2097152:
            raise HTTPException(status_code=400,detail="图片不能超过2MB")
        file_ext = os.path.splitext(file.filename)[-1]
        file_name = f"avatar_{uuid.uuid4().hex}{file_ext}"
        save_dir = "static/avatars"
        os.makedirs(save_dir,exist_ok=True)
        file_path = f"{save_dir}/{file_name}"
        with open(file_path,"wb") as f:
            f.write(contents)
        from app.api.crud.user import update_user_avatar
        avatar_url = f"/{file_path}"
        update_user_avatar(db,current_user.id,avatar_url)
        return {"code":200,"message":"头像上传成功","data":{"avatar":avatar_url}}
    except Exception as e:
        raise HTTPException(status_code=500,detail="上传失败")

@router.get("/admin/users", summary="管理员获取用户列表")
def admin_get_users(
    username: Optional[str] = None,
    phone: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    from app.api.crud.user import get_user_list
    users = get_user_list(db, username=username, phone=phone, role=role, is_active=is_active)
    for user in users:
        if hasattr(user, 'role') and user.role:
            user.role = user.role.value
    return {"code":200,"message":"success","data":users}

@router.put("/admin/users/{user_id}", summary="管理员编辑用户")
def admin_update_user(
    user_id: int,
    user_data: dict,
    db: Session = Depends(get_db)
):
    from app.api.crud.user import admin_update_user
    updated = admin_update_user(db, user_id, user_data)
    if not updated:
        raise HTTPException(status_code=400,detail="更新失败")
    return {"code":200,"message":"更新成功"}

@router.delete("/admin/users/{user_id}", summary="管理员删除用户")
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    from app.api.crud.user import delete_user
    delete_user(db, user_id)
    return {"code":200,"message":"删除成功"}

@router.put("/admin/users/{user_id}/toggle-status", summary="切换用户启用/禁用状态")
def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db)
):
    from app.api.crud.user import toggle_user_status
    user = toggle_user_status(db, user_id)
    if not user:
        raise HTTPException(status_code=404,detail="用户不存在")
    return {"code":200,"message":"状态更新成功","data":{"is_active":user.is_active}}

