from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class EntityType(Base):
    __tablename__ = "entity_type"
    type_id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))

class Entity(Base):
    __tablename__ = "entity"
    entity_id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    time = Column(DateTime)
    summary = Column(Text)
    source_table = Column(String(50), nullable=False)

class Relationship(Base):
    __tablename__ = "relationship"
    rel_id = Column(Integer, primary_key=True, autoincrement=True)
    start_entity_id = Column(Integer, nullable=False)
    end_entity_id = Column(Integer, nullable=False)
    rel_type = Column(String(50), nullable=False)
    description = Column(Text)