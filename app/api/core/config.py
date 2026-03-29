from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:linjiaxin040219@127.0.0.1:3306/qiaoxiang_platform?charset=utf8mb4"

    # 新增 Neo4j 配置
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "linjiaxin")

    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-keep-it-safe")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 7  # 7天

    # 文件上传配置
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024
    base_url: str = os.getenv("BASE_URL", "http://127.0.0.1:8090")  # 新增base_url配置

    # 验证码配置
    VERIFY_CODE_EXPIRE_MINUTES: int = 5
    VERIFY_CODE_LENGTH: int = 6

settings = Settings()