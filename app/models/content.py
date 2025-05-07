from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Float, Table, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.database import Base

# Таблица связей между контентом и концепциями
content_concept = Table(
    "content_concept",
    Base.metadata,
    Column("content_id", UUID(as_uuid=True), ForeignKey("educational_content.id", ondelete="CASCADE"), primary_key=True),
    Column("concept_id", UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), primary_key=True),
    Column("relevance", Float, nullable=False, default=1.0)
)

class Concept(Base):
    """Модель образовательной концепции."""
    __tablename__ = "concepts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    domain = Column(String(100), nullable=False)
    difficulty = Column(Float, nullable=False)
    taxonomy_tags = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    educational_content = relationship("EducationalContent", secondary=content_concept, back_populates="concepts")

class ConceptRelationship(Base):
    """Модель связи между концепциями."""
    __tablename__ = "concept_relationships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    target_concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(String(50), nullable=False)
    strength = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class EducationalContent(Base):
    """Модель образовательного контента."""
    __tablename__ = "educational_content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False)
    body = Column(Text, nullable=False)
    difficulty = Column(Float, nullable=False)
    metadata = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    concepts = relationship("Concept", secondary=content_concept, back_populates="educational_content")

class AdaptedContent(Base):
    """Модель адаптированного образовательного контента."""
    __tablename__ = "adapted_content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_content_id = Column(UUID(as_uuid=True), ForeignKey("educational_content.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    difficulty = Column(Float, nullable=False)
    adaptation_params = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
