from sqlalchemy.orm import Session
from app.api.models.user import User, VerifyCode, UserRole, VerifyCodeType
from app.api.schemas.user import UserCreate, ResetPasswordRequest, UserUpdateRequest
from app.api.utils.security import get_password_hash, verify_password
from app.api.utils.verify_code import generate_verify_code, get_expire_time
from datetime import datetime
from typing import Optional

def get_user_by_phone(db: Session, phone: str) -> User:
    return db.query(User).filter(User.phone == phone, User.is_delete == False).first()

def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username, User.is_delete == False).first()

def get_user_by_id(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.id == user_id, User.is_delete == False).first()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    user_role = UserRole(user.role) if hasattr(user, 'role') and user.role in [r.value for r in UserRole] else UserRole.visitor
    db_user = User(
        username=user.username,
        phone=user.phone,
        password=hashed_password,
        role=user_role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, phone: str, password: str) -> User:
    user = get_user_by_phone(db, phone)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def create_verify_code(db: Session, phone: str, code_type: str) -> VerifyCode:
    db.query(VerifyCode).filter(
        VerifyCode.phone == phone,
        VerifyCode.type == VerifyCodeType(code_type),
        VerifyCode.is_used == False
    ).delete()

    code = generate_verify_code()
    expire_time = get_expire_time()

    db_code = VerifyCode(
        phone=phone,
        code=code,
        type=VerifyCodeType(code_type),
        expire_time=expire_time
    )
    db.add(db_code)
    db.commit()
    db.refresh(db_code)
    return db_code

def verify_code(db: Session, phone: str, code: str, code_type: str) -> bool:
    db_code = db.query(VerifyCode).filter(
        VerifyCode.phone == phone,
        VerifyCode.type == VerifyCodeType(code_type),
        VerifyCode.code == code,
        VerifyCode.is_used == False,
        VerifyCode.expire_time > datetime.now()
    ).first()

    if not db_code:
        return False

    db_code.is_used = True
    db.commit()
    return True

def reset_password(db: Session, request: ResetPasswordRequest) -> bool:
    user = get_user_by_phone(db, request.phone)
    if not user:
        return False

    user.password = get_password_hash(request.password)
    db.commit()
    return True

def update_user(db: Session, user_id: int, user_update: UserUpdateRequest) -> User:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(db_user, key) and key not in ['id', 'password', 'role', 'is_delete', 'create_time']:
            setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_avatar(db: Session, user_id: int, avatar_url: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    user.avatar = avatar_url
    db.commit()
    db.refresh(user)
    return user

def get_user_list(db: Session, username: Optional[str] = None, phone: Optional[str] = None, role: Optional[str] = None, is_active: Optional[bool] = None):
    query = db.query(User).filter(User.is_delete == False)
    if username:
        query = query.filter(User.username.contains(username))
    if phone:
        query = query.filter(User.phone.contains(phone))
    if role:
        query = query.filter(User.role == UserRole(role))
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.all()

def admin_update_user(db: Session, user_id: int, user_data: dict):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    allowed_fields = ['username', 'phone', 'shop_name', 'shop_address']
    for key in allowed_fields:
        if key in user_data and user_data[key] is not None:
            setattr(user, key, user_data[key])
    if 'role' in user_data and user_data['role'] in [r.value for r in UserRole]:
        user.role = UserRole(user_data['role'])
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if user:
        user.is_delete = True
        db.commit()

def toggle_user_status(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user