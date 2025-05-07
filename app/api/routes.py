from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Path, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta

from app.db.database import get_db
from app.api import schemas
from app.services import auth_service, profile_service, content_service, assessment_service, chat_service

# Инициализация OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Создание основного роутера API
api_router = APIRouter(prefix="/api")

# Аутентификация
@api_router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Зависимость для получения текущего пользователя
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await auth_service.get_current_user(db, token)

# Пользователи и профили
@api_router.post("/users", response_model=schemas.UserResponse)
async def create_user(
    user_create: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await auth_service.create_user(db, user_create)

@api_router.get("/users/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    return current_user

@api_router.post("/profiles", response_model=schemas.LearningProfileResponse)
async def create_profile(
    profile_data: schemas.LearningProfileBase,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await profile_service.create_profile(db, current_user.id, profile_data)

@api_router.get("/profiles/{user_id}", response_model=schemas.LearningProfileResponse)
async def get_profile(
    user_id: uuid.UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Проверка прав доступа
    if current_user.role not in ["admin", "teacher"] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this profile")
    
    return await profile_service.get_profile(db, user_id)

@api_router.patch("/profiles/{user_id}", response_model=schemas.LearningProfileResponse)
async def update_profile(
    user_id: uuid.UUID,
    profile_updates: schemas.LearningProfileBase,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Проверка прав доступа
    if current_user.role not in ["admin", "teacher"] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    
    return await profile_service.update_profile(db, user_id, profile_updates)

# Контент и концепции
@api_router.post("/concepts", response_model=schemas.ConceptResponse)
async def create_concept(
    concept_create: schemas.ConceptCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Проверка прав доступа
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized to create concepts")
    
    return await content_service.create_concept(db, concept_create)

@api_router.get("/concepts", response_model=List[schemas.ConceptResponse])
async def get_concepts(
    domain: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await content_service.get_concepts(db, domain, skip, limit)

@api_router.post("/content", response_model=schemas.ContentResponse)
async def create_content(
    content_create: schemas.ContentCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Проверка прав доступа
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized to create content")
    
    return await content_service.create_content(db, content_create)

@api_router.post("/content/adapt", response_model=schemas.ContentResponse)
async def adapt_content(
    adaptation_request: schemas.AdaptationRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Проверка прав доступа
    if current_user.id != adaptation_request.user_id and current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized for this adaptation request")
    
    return await content_service.adapt_content(db, adaptation_request)

# Оценки и диагностика
@api_router.post("/assessments", response_model=schemas.AssessmentResponse)
async def create_assessment(
    assessment_request: schemas.AssessmentRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Проверка прав доступа
    if current_user.id != assessment_request.user_id and current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized to create assessment for this user")
    
    return await assessment_service.create_assessment(db, assessment_request)

@api_router.post("/assessments/{assessment_id}/submit", response_model=schemas.AssessmentResult)
async def submit_assessment(
    assessment_id: uuid.UUID,
    submission: schemas.AssessmentSubmission,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await assessment_service.submit_assessment(db, assessment_id, current_user.id, submission)

# Планы обучения
@api_router.post("/learning/plan", response_model=Dict[str, Any])
async def create_learning_plan(
    plan_request: schemas.LearningPlanRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Проверка прав доступа
    if current_user.id != plan_request.user_id and current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized to create learning plan for this user")
    
    return await content_service.create_learning_plan(db, plan_request)

# Чат-интерфейс
@api_router.post("/chat/message", response_model=schemas.ChatResponse)
async def send_chat_message(
    request: schemas.ChatRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Проверка прав доступа
    if current_user.id != request.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to send messages for this user")
    
    # Обработка сообщения
    response = await chat_service.process_message(db, request)
    
    # Асинхронное обновление профиля
    background_tasks.add_task(
        profile_service.update_profile_from_interaction,
        db, 
        request.user_id, 
        {"type": "chat", "content": request.message}
    )
    
    return response

# Импорт и подключение маршрутов адаптивных механизмов
from app.api.adaptive_routes import router as adaptive_router
api_router.include_router(adaptive_router, prefix="/adaptive", tags=["adaptive"])
