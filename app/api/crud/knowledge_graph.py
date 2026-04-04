from sqlalchemy.orm import Session
from app.api.models.knowledge_graph import Entity, Relationship, EntityType

def get_knowledge_graph_data(db: Session):
    relationships = db.query(
        Relationship.start_entity_id,
        Relationship.end_entity_id,
        Relationship.rel_type
    ).filter(
        Relationship.start_entity_id.isnot(None),
        Relationship.end_entity_id.isnot(None)
    ).limit(300).all()

    related_ids = set()
    for r in relationships:
        related_ids.add(str(r.start_entity_id))
        related_ids.add(str(r.end_entity_id))

    related_ids = list(related_ids)

    entities = db.query(
        Entity.entity_id,
        Entity.name,
        Entity.summary,
        EntityType.type_name
    ).join(EntityType, Entity.type_id == EntityType.type_id
    ).filter(
        Entity.entity_id.in_(related_ids)
    ).limit(300).all()

    nodes = [
        {
            "entity_id": str(e.entity_id),
            "name": e.name,
            "type_name": e.type_name,
            "summary": e.summary
        } for e in entities
    ]

    links = [
        {
            "start_entity_id": str(r.start_entity_id),
            "end_entity_id": str(r.end_entity_id),
            "rel_type": r.rel_type
        } for r in relationships
    ]

    return {"nodes": nodes, "links": links}