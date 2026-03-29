
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.api.core.config import settings
from app.api.db.base import Base


engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():

    Base.metadata.create_all(bind=engine)
    Base.registry.configure()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()