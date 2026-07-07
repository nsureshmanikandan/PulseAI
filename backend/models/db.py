from sqlalchemy import create_engine, Column, String, Integer, JSON, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from backend.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    blob_path = Column(String, nullable=False)
    storage_backend = Column(String, nullable=False)
    tab_names = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
    tabs = relationship("TabProfile", back_populates="dataset", cascade="all, delete-orphan")
    relationships = relationship("TabRelationship", back_populates="dataset", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="dataset", cascade="all, delete-orphan")


class TabProfile(Base):
    __tablename__ = "tab_profiles"

    id = Column(String, primary_key=True)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    tab_name = Column(String, nullable=False)
    row_count = Column(Integer)
    column_profiles = Column(JSON)
    dataset = relationship("Dataset", back_populates="tabs")


class TabRelationship(Base):
    __tablename__ = "relationships"

    id = Column(String, primary_key=True)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    tab_a = Column(String, nullable=False)
    tab_b = Column(String, nullable=False)
    column_a = Column(String, nullable=False)
    column_b = Column(String, nullable=False)
    confidence = Column(String)
    dataset = relationship("Dataset", back_populates="relationships")


class SavedQuery(Base):
    __tablename__ = "saved_queries"

    id = Column(String, primary_key=True)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    question = Column(Text, nullable=False)
    chart_config = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    messages = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
    dataset = relationship("Dataset", back_populates="chat_sessions")


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
