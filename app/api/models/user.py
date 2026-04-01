from sqlalchemy import Column, BigInteger, String, Enum, Boolean, DateTime
from sqlalchemy.sql import func
from app.api.db.base import Base
from sqlalchemy.orm import relationship
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
    username = Column(String(16), unique=True, nullable=False)
    avatar = Column(String(500), nullable=True)
    phone = Column(String(11), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.visitor, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_delete = Column(Boolean, default=False, nullable=False)
    create_time = Column(DateTime, default=func.now(), nullable=False)
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    shop_name = Column(String(100), nullable=True)
    shop_address = Column(String(255), nullable=True)
    projects = relationship("Project", back_populates="merchant")
    checkins = relationship("Checkin", back_populates="user", cascade="all, delete-orphan")

class VerifyCode(Base):
    __tablename__ = "verify_code"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(11), nullable=False)
    code = Column(String(6), nullable=False)
    type = Column(Enum(VerifyCodeType), nullable=False)
    expire_time = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    create_time = Column(DateTime, default=func.now(), nullable=False)