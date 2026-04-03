from pydantic import BaseModel
from typing import List, Optional

class GraphNode(BaseModel):
    id: int
    name: str
    category: str
    summary: Optional[str] = None

class GraphLink(BaseModel):
    source: int
    target: int
    relation: str

class KnowledgeGraphResponse(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]

    class Config:
        orm_mode = True