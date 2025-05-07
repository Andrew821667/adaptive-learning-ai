from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Float, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.database import Base

class Assessment(Base):
    """Модель оценки знаний."""
    __tablename__ = "assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assessment_type = Column(String(50), nullable=False)
    metadata = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class AssessmentQuestion(Base):
    """Модель вопроса оценки."""
    __tablename__ = "assessment_questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    question_type = Column(String(50), nullable=False)
    content = Column(JSON, nullable=False)
    difficulty = Column(Float, nullable=False)
    metadata = Column(JSON, nullable=False, default={})

class AssessmentResponse(Base):
    """Модель ответа на вопрос оценки."""
    __tablename__ = "assessment_responses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("assessment_questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    response = Column(JSON, nullable=False)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    response_time_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class LearningInteraction(Base):
    """Модель взаимодействия с системой обучения."""
    __tablename__ = "learning_interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(UUID(as_uuid=True), nullable=True)
    interaction_type = Column(String(50), nullable=False)
    content = Column(JSON, nullable=False)
    metadata = Column(JSON, nullable=False, default={})
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class LearningSession(Base):
    """Модель сессии обучения."""
    __tablename__ = "learning_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    session_type = Column(String(50), nullable=False)
    metadata = Column(JSON, nullable=False, default={})

class LearningPlan(Base):
    """Модель плана обучения."""
    __tablename__ = "learning_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    plan_data = Column(JSON, nullable=False)
    status = Column(String(50), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
