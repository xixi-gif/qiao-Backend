from sqlalchemy.orm import Session
from app.api.models.user import User, VerifyCode, UserRole, VerifyCodeType
from app.api.schemas.user import UserCreate, ResetPasswordRequest
from app.api.utils.security import get_password_hash, verify_password
from app.api.utils.verify_code import generate_verify_code, get_expire_time
from datetime import datetime

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