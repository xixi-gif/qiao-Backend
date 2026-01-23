import random
import string
from datetime import datetime, timedelta
from app.api.core.config import settings

def generate_verify_code() -> str:
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(settings.VERIFY_CODE_LENGTH))

def get_expire_time() -> datetime:
    return datetime.now() + timedelta(minutes=settings.VERIFY_CODE_EXPIRE_MINUTES)