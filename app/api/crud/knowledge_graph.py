from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.models.knowledge_graph import Entity, Relationship, EntityType

def get_knowledge_graph_data(db: Session):
    # 查询所有节点（实体）
    entities = db.query(
        Entity.entity_id.label("id"),
        Entity.name,
        Entity.summary,
        EntityType.type_name.label("category")
    ).join(EntityType, Entity.type_id == EntityType.type_id).all()

    # 查询所有关系（边）
    relationships = db.query(
        Relationship.start_entity_id.label("source"),
        Relationship.end_entity_id.label("target"),
        Relationship.rel_type.label("relation")
    ).all()

    # 转为字典格式
    nodes = [
        {
            "id": e.id,
            "name": e.name,
            "category": e.category,
            "summary": e.summary
        } for e in entities
    ]

    links = [
        {
            "source": r.source,
            "target": r.target,
            "relation": r.relation
        } for r in relationships
    ]

    return {"nodes": nodes, "links": links}