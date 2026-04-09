from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.db.database import get_db
from app.api.crud.knowledge_graph import get_knowledge_graph_data
from app.api.schemas.knowledge_graph import KnowledgeGraphResponse

router = APIRouter()

@router.get("/graph", response_model=KnowledgeGraphResponse)
def get_graph(db: Session = Depends(get_db)):

    data = get_knowledge_graph_data(db)
    return data