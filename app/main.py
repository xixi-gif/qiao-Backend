from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

# 1. 保持原有的导入
from app.api.routes.auth import router as auth_router
from app.api.db.base import Base
from app.api.db.database import engine

# 2. 新增路径规划路由的导入
from app.api.routes.planner import router as planner_router

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 执行 SQL 数据库建表 (MySQL)
Base.metadata.create_all(bind=engine)

# 初始化 FastAPI
app = FastAPI(title="南桥遗梦 - 后端接口服务")

# 跨域配置 (如果你前端端口变了，可以在这里添加)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,  # 必须为 True
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理逻辑
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

# 原有的认证路由
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

# 3. 新增的研学路径规划路由
app.include_router(planner_router, prefix="/api/v1/planner", tags=["研学路径规划"])

@app.get("/")
def root():
    # 稍微修改一下提示信息，确认两个功能都加载了
    return {
        "message": "欢迎使用南桥遗梦后端接口",
        "modules": ["auth", "path-planner"],
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8090, reload=True)