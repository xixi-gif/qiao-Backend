from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.db.database import get_db
from app.api.crud.knowledge_graph import get_knowledge_graph_data
from app.api.schemas.knowledge_graph import KnowledgeGraphResponse

router = APIRouter()

@router.get("/graph", response_model=KnowledgeGraphResponse)
def get_graph(db: Session = Depends(get_db)):
    """
    获取完整潮汕侨乡知识图谱数据
    返回格式：{ nodes: [], links: [] }
    前端可直接用于ECharts/G6/AntV等图谱组件渲染
    """
    data = get_knowledge_graph_data(db)
    return data