from sqlalchemy import Column, BigInteger, String, Enum, Boolean, DateTime
from sqlalchemy.sql import func
from app.api.db.base import Base
import enum

class UserRole(enum.Enum):
    visitor = "visitor"
    admin = "admin"
    merchant = "merchant"

class VerifyCodeType(enum.Enum):
    forgot_password = "forgot_password"

class User(Base):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    username = Column(String(16), unique=True, nullable=False, comment="用户名")
    avatar = Column(String(500), nullable=True, comment="用户头像路径/URL")
    phone = Column(String(11), unique=True, nullable=False, comment="手机号")
    password = Column(String(255), nullable=False, comment="加密后的密码")
    role = Column(Enum(UserRole), default=UserRole.visitor, nullable=False, comment="用户角色")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    is_delete = Column(Boolean, default=False, nullable=False, comment="逻辑删除标识")
    create_time = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

class VerifyCode(Base):
    __tablename__ = "verify_code"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(11), nullable=False, comment="手机号")
    code = Column(String(6), nullable=False, comment="验证码")
    type = Column(Enum(VerifyCodeType), nullable=False, comment="验证码类型")
    expire_time = Column(DateTime, nullable=False, comment="过期时间")
    is_used = Column(Boolean, default=False, nullable=False, comment="是否使用")
    create_time = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")