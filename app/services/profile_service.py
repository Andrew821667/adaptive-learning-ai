from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.models.user import LearningProfile, User, ConceptMastery
from app.models.content import Concept
from app.api.schemas import LearningProfileBase

async def create_profile(db: AsyncSession, user_id: uuid.UUID, profile_data: LearningProfileBase):
    """Создает профиль обучения для пользователя."""
    # Проверка, что пользователь существует
    user_query = select(User).where(User.id == user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalars().first()
    if not user:
        raise ValueError(f"User with id {user_id} not found")
    
    # Проверка, что профиль еще не существует
    profile_query = select(LearningProfile).where(LearningProfile.user_id == user_id)
    profile_result = await db.execute(profile_query)
    existing_profile = profile_result.scalars().first()
    if existing_profile:
        raise ValueError(f"Profile for user {user_id} already exists")
    
    # Создание нового профиля
    profile = LearningProfile(
        id=uuid.uuid4(),
        user_id=user_id,
        learning_style=profile_data.learning_style,
        cognitive_profile=profile_data.cognitive_profile,
        preferences=profile_data.preferences
    )
    
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    
    return profile

async def get_profile(db: AsyncSession, user_id: uuid.UUID):
    """Получает профиль обучения пользователя."""
    query = select(LearningProfile).where(LearningProfile.user_id == user_id)
    result = await db.execute(query)
    profile = result.scalars().first()
    if not profile:
        raise ValueError(f"Profile for user {user_id} not found")
    return profile

async def update_profile(db: AsyncSession, user_id: uuid.UUID, profile_updates: LearningProfileBase):
    """Обновляет профиль обучения пользователя."""
    # Получение текущего профиля
    profile = await get_profile(db, user_id)
    
    # Обновление полей
    for key, value in profile_updates.dict(exclude_unset=True).items():
        if hasattr(profile, key):
            current_value = getattr(profile, key)
            if isinstance(current_value, dict) and isinstance(value, dict):
                # Для словарей выполняем глубокое обновление
                current_value.update(value)
            else:
                setattr(profile, key, value)
    
    profile.updated_at = datetime.now()
    await db.commit()
    await db.refresh(profile)
    
    return profile

async def get_concept_mastery(db: AsyncSession, user_id: uuid.UUID, concept_id: Optional[uuid.UUID] = None):
    """Получает информацию о владении концепциями."""
    query = select(ConceptMastery).where(ConceptMastery.user_id == user_id)
    if concept_id:
        query = query.where(ConceptMastery.concept_id == concept_id)
    
    result = await db.execute(query)
    masteries = result.scalars().all()
    return masteries

async def update_concept_mastery(db: AsyncSession, user_id: uuid.UUID, concept_id: uuid.UUID, assessment_result: Dict[str, Any]):
    """Обновляет уровень владения концепцией на основе результатов оценки."""
    # Проверка существования концепции
    concept_query = select(Concept).where(Concept.id == concept_id)
    concept_result = await db.execute(concept_query)
    concept = concept_result.scalars().first()
    if not concept:
        raise ValueError(f"Concept with id {concept_id} not found")
    
    # Получение текущего уровня владения
    mastery_query = select(ConceptMastery).where(
        (ConceptMastery.user_id == user_id) & 
        (ConceptMastery.concept_id == concept_id)
    )
    mastery_result = await db.execute(mastery_query)
    current_mastery = mastery_result.scalars().first()
    
    # Извлечение данных оценки
    score = assessment_result.get("score", 0.0)
    confidence = assessment_result.get("confidence", 0.5)
    
    # Вес новой оценки в зависимости от уверенности
    weight = min(0.8, confidence * 0.5 + 0.3)
    
    if current_mastery:
        # Обновление существующего уровня владения
        new_level = current_mastery.mastery_level * (1 - weight) + score * weight
        new_confidence = current_mastery.confidence * (1 - weight) + confidence * weight
        
        current_mastery.mastery_level = new_level
        current_mastery.confidence = new_confidence
        current_mastery.last_assessed_at = datetime.now()
        current_mastery.updated_at = datetime.now()
    else:
        # Создание нового уровня владения
        new_mastery = ConceptMastery(
            id=uuid.uuid4(),
            user_id=user_id,
            concept_id=concept_id,
            mastery_level=score,
            confidence=confidence,
            last_assessed_at=datetime.now()
        )
        db.add(new_mastery)
    
    await db.commit()
    
    # Получение обновленного уровня владения
    updated_mastery_query = select(ConceptMastery).where(
        (ConceptMastery.user_id == user_id) & 
        (ConceptMastery.concept_id == concept_id)
    )
    updated_mastery_result = await db.execute(updated_mastery_query)
    updated_mastery = updated_mastery_result.scalars().first()
    
    return updated_mastery

async def update_profile_from_interaction(db: AsyncSession, user_id: uuid.UUID, interaction_data: Dict[str, Any]):
    """Обновляет профиль на основе взаимодействия."""
    # Реализация обновления профиля на основе взаимодействия
    # Это может включать обновление когнитивного профиля, стиля обучения и т.д.
    
    # Пример: обновление предпочтений на основе взаимодействия
    profile = await get_profile(db, user_id)
    
    interaction_type = interaction_data.get("type")
    content = interaction_data.get("content")
    
    if interaction_type == "chat":
        # Анализ текстового взаимодействия для выявления предпочтений
        # Это может быть реализовано с помощью NLP или правил
        pass
    
    await db.commit()
    
    return profile
