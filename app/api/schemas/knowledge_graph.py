from pydantic import BaseModel
from typing import List, Optional

class GraphNode(BaseModel):
    entity_id: str
    name: str
    type_name: str
    summary: Optional[str] = None

class GraphLink(BaseModel):
    start_entity_id: str
    end_entity_id: str
    rel_type: str

class KnowledgeGraphResponse(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]