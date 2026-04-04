from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import traceback

from app.api.routes.auth import router as auth_router
from app.api.db.base import Base
from app.api.db.database import engine

from app.api.routes.planner import router as planner_router
from app.api.routes.announcement import router as announcement_router
from app.api.routes.project import router as project_router
from app.api.routes.carousel import router as carousel_router
from app.api.routes import tag, category
from app.api.routes.interaction import router as interaction_router
from app.api.routes.checkin import router as checkin_router
from app.api.routes.markdown import router as md_router
from app.api.routes.chat import router as chat_router
from app.api.routes.knowledge_graph import router as kg_router
from app.api.routes.chat_router import router as aichat_router
from app.api.routes.merchant_analysis import router as analysis_router
from app.api.routes.admin_statistics import router as admin_statistics_router
from app.api.utils.websocket import manager


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)
logger = logging.getLogger()
logging.getLogger("fastapi").setLevel(logging.DEBUG)
logging.getLogger("uvicorn").setLevel(logging.DEBUG)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="南桥遗梦 - 后端接口服务", debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        manager.disconnect(user_id)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/storage", StaticFiles(directory="app/api/storage"), name="storage")

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(planner_router, prefix="/api/v1/planner", tags=["研学路径规划"])
app.include_router(announcement_router, prefix="/api/announcements", tags=["announcements"])
app.include_router(project_router, prefix="/api", tags=["projects"])
app.include_router(carousel_router, prefix="/api")
app.include_router(tag.router, prefix="/api", tags=["tags"])
app.include_router(category.router, prefix="/api", tags=["categories"])
app.include_router(interaction_router, prefix="/api", tags=["interact"])
app.include_router(checkin_router, prefix="/api", tags=["打卡模块"])
app.include_router(kg_router, prefix="/api", tags=["侨文化知识图谱"])
app.include_router(aichat_router, prefix="/api", tags=["侨文化知识问答"])
app.include_router(md_router)
app.include_router(chat_router)
app.include_router(analysis_router)
app.include_router(admin_statistics_router)

@app.get("/")
def root():
    logger.info("根路径被访问了！")
    return {
        "message": "欢迎使用南桥遗梦后端接口",
        "modules": ["auth", "path-planner", "chat"],
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8090,
        reload=True,
        log_level="debug",
        access_log=True
    )