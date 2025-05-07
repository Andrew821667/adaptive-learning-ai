from pydantic import BaseModel, EmailStr, Field, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Базовые схемы пользователей
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID4
    created_at: datetime
    
    class Config:
        orm_mode = True

class LearningProfileBase(BaseModel):
    learning_style: Dict[str, float] = Field(default_factory=dict)
    cognitive_profile: Dict[str, Any] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)

class LearningProfileResponse(LearningProfileBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Схемы концепций и контента
class ConceptBase(BaseModel):
    name: str
    description: str
    domain: str
    difficulty: float
    taxonomy_tags: Dict[str, List[str]] = Field(default_factory=dict)

class ConceptCreate(ConceptBase):
    pass

class ConceptResponse(ConceptBase):
    id: UUID4
    created_at: datetime
    
    class Config:
        orm_mode = True

class ContentBase(BaseModel):
    title: str
    content_type: str
    body: str
    difficulty: float
    concepts: List[UUID4] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ContentCreate(ContentBase):
    pass

class ContentResponse(ContentBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Схемы для оценки
class AssessmentRequest(BaseModel):
    user_id: UUID4
    concept_ids: List[UUID4]
    difficulty_level: float = 0.5
    assessment_type: str = "adaptive"
    max_questions: int = 5

class QuestionBase(BaseModel):
    question_id: UUID4
    concept_id: UUID4
    text: str
    options: List[Dict[str, Any]] = Field(default_factory=list)
    difficulty: float
    
class AssessmentResponse(BaseModel):
    assessment_id: UUID4
    user_id: UUID4
    questions: List[QuestionBase]
    concept_ids: List[UUID4]
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        orm_mode = True

class AssessmentSubmission(BaseModel):
    responses: List[Dict[str, Any]]

class AssessmentResult(BaseModel):
    result_id: UUID4
    assessment_id: UUID4
    user_id: UUID4
    concept_results: Dict[str, Dict[str, Any]]
    total_score: float
    feedback: Dict[str, Any]
    created_at: datetime
    
    class Config:
        orm_mode = True

# Схемы для адаптивного контента
class AdaptationRequest(BaseModel):
    content_id: UUID4
    user_id: UUID4
    adaptation_params: Optional[Dict[str, Any]] = None

# Схемы для чата
class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatRequest(BaseModel):
    user_id: UUID4
    message: str
    session_id: Optional[UUID4] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message_id: UUID4
    role: str
    content: str
    session_id: UUID4
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
