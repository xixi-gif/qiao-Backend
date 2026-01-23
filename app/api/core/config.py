from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:linjiaxin040219@localhost:3306/qiaoxiang_platform")

    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-keep-it-safe")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 7  # 7天

    # 验证码配置
    VERIFY_CODE_EXPIRE_MINUTES: int = 5
    VERIFY_CODE_LENGTH: int = 6


settings = Settings()