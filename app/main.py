from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.auth import router as auth_router
from app.api.db.base import Base
from app.api.db.database import engine
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="南桥遗梦 - 认证接口")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"请求 {request.url} 发生异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "服务器内部错误",
            "error_type": str(type(exc).__name__),
            "error_msg": str(exc)
        },
        headers={"Content-Type": "application/json"}
    )


app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

@app.get("/")
def root():
    return {"message": "欢迎使用南桥遗梦后端接口"}