from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import traceback

# 1. 保持原有的导入
from app.api.routes.auth import router as auth_router
from app.api.db.base import Base
from app.api.db.database import engine

# 2. 新增路径规划路由的导入
from app.api.routes.planner import router as planner_router
from app.api.routes.announcement import router as announcement_router

# ========== 修复日志配置（关键！）==========
# 配置根日志器，覆盖所有模块（包括FastAPI、路由、CRUD）
logging.basicConfig(
    level=logging.DEBUG,  # 最低级别，确保所有日志都能输出
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # 控制台输出
        # 可选：加文件日志，防止控制台没看到
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)
# 获取根logger，确保所有模块共用
logger = logging.getLogger()
# 强制开启FastAPI自身的DEBUG日志
logging.getLogger("fastapi").setLevel(logging.DEBUG)
logging.getLogger("uvicorn").setLevel(logging.DEBUG)

# 执行 SQL 数据库建表 (MySQL)
Base.metadata.create_all(bind=engine)

# 初始化 FastAPI
app = FastAPI(title="南桥遗梦 - 后端接口服务", debug=True)  # 开启debug模式

# ========== 修复CORS（兼容所有前端地址）==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # 兼容两个地址
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

# --- 注册路由模块 ---
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(planner_router, prefix="/api/v1/planner", tags=["研学路径规划"])
app.include_router(announcement_router, prefix="/api/announcements", tags=["announcements"])

@app.get("/")
def root():
    logger.info("根路径被访问了！")  # 测试日志是否生效
    return {
        "message": "欢迎使用南桥遗梦后端接口",
        "modules": ["auth", "path-planner"],
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    # 强制开启uvicorn的debug和日志
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8090,
        reload=True,
        log_level="debug",  # uvicorn日志级别
        access_log=True     # 打印访问日志（能看到请求是否到达后端）
    )