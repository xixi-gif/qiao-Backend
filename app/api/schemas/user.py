from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=16, description="用户名")
    phone: str = Field(description="手机号")
    password: str = Field(min_length=6, description="密码")
    confirm_password: str = Field(description="确认密码")
    role: str = Field(default="visitor", description="角色")

    @validator("phone")
    def validate_phone(cls, v):
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("请输入正确的11位手机号")
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values,** kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("两次输入的密码不一致")
        return v

class UserLogin(BaseModel):
    phone: str = Field(description="手机号")
    password: str = Field(description="密码")
    role: str = Field(default="visitor", description="角色")
    remember: Optional[bool] = Field(default=True, description="记住我")

    @validator("phone")
    def validate_phone(cls, v):
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("请输入正确的11位手机号")
        return v

class VerifyCodeRequest(BaseModel):
    phone: str = Field(description="手机号")
    type: str = Field(default="forgot_password", description="验证码类型")

    @validator("phone")
    def validate_phone(cls, v):
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("请输入正确的11位手机号")
        return v

class ResetPasswordRequest(BaseModel):
    phone: str = Field(description="手机号")
    code: str = Field(min_length=6, max_length=6, description="验证码")
    password: str = Field(min_length=6, description="新密码")
    confirm_password: str = Field(description="确认新密码")

    @validator("phone")
    def validate_phone(cls, v):
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("请输入正确的11位手机号")
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("两次输入的密码不一致")
        return v

class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: dict

class UserProfileResponse(BaseModel):
    id: int
    username: str
    avatar: Optional[str] = None
    phone: str
    role: str

    class Config:
        from_attributes = True