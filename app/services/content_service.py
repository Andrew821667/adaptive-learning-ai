from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.models.content import Concept, ConceptRelationship, EducationalContent, AdaptedContent, content_concept
from app.models.user import LearningProfile
from app.api.schemas import ConceptCreate, ContentCreate, AdaptationRequest, LearningPlanRequest
from app.services.llm_service import get_llm_provider

async def create_concept(db: AsyncSession, concept_create: ConceptCreate):
    """Создает новую образовательную концепцию."""
    concept = Concept(
        id=uuid.uuid4(),
        name=concept_create.name,
        description=concept_create.description,
        domain=concept_create.domain,
        difficulty=concept_create.difficulty,
        taxonomy_tags=concept_create.taxonomy_tags
    )
    
    db.add(concept)
    await db.commit()
    await db.refresh(concept)
    
    return concept

async def get_concepts(db: AsyncSession, domain: Optional[str] = None, skip: int = 0, limit: int = 100):
    """Получает список концепций с возможностью фильтрации по домену."""
    query = select(Concept)
    if domain:
        query = query.where(Concept.domain == domain)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    concepts = result.scalars().all()
    
    return concepts

async def create_concept_relationship(db: AsyncSession, source_id: uuid.UUID, target_id: uuid.UUID, relationship_type: str, strength: float):
    """Создает связь между концепциями."""
    relationship = ConceptRelationship(
        id=uuid.uuid4(),
        source_concept_id=source_id,
        target_concept_id=target_id,
        relationship_type=relationship_type,
        strength=strength
    )
    
    db.add(relationship)
    await db.commit()
    await db.refresh(relationship)
    
    return relationship

async def create_content(db: AsyncSession, content_create: ContentCreate):
    """Создает новый образовательный контент."""
    # Создание контента
    content = EducationalContent(
        id=uuid.uuid4(),
        title=content_create.title,
        content_type=content_create.content_type,
        body=content_create.body,
        difficulty=content_create.difficulty,
        metadata=content_create.metadata
    )
    
    db.add(content)
    await db.commit()
    await db.refresh(content)
    
    # Связывание контента с концепциями
    for concept_id in content_create.concepts:
        await db.execute(
            insert(content_concept).values(
                content_id=content.id,
                concept_id=concept_id,
                relevance=1.0
            )
        )
    
    await db.commit()
    await db.refresh(content)
    
    return content

async def adapt_content(db: AsyncSession, adaptation_request: AdaptationRequest):
    """Адаптирует образовательный контент под профиль учащегося."""
    # Получение исходного контента
    content_query = select(EducationalContent).where(EducationalContent.id == adaptation_request.content_id)
    content_result = await db.execute(content_query)
    original_content = content_result.scalars().first()
    if not original_content:
        raise ValueError(f"Content with id {adaptation_request.content_id} not found")
    
    # Получение профиля учащегося
    profile_query = select(LearningProfile).where(LearningProfile.user_id == adaptation_request.user_id)
    profile_result = await db.execute(profile_query)
    learner_profile = profile_result.scalars().first()
    if not learner_profile:
        raise ValueError(f"Profile for user {adaptation_request.user_id} not found")
    
    # Параметры адаптации
    params = adaptation_request.adaptation_params or {}
    
    # LLM провайдер для адаптации контента
    llm_provider = get_llm_provider()
    
    # Адаптация контента с помощью LLM
    # 1. Адаптация сложности
    target_difficulty = params.get("target_difficulty")
    if target_difficulty is None:
        # Если целевая сложность не указана, вычисляем ее на основе профиля
        # Например, немного выше текущего уровня пользователя
        # Упрощенная логика для примера
        concepts_query = select(Concept).join(
            content_concept, content_concept.c.concept_id == Concept.id
        ).where(content_concept.c.content_id == original_content.id)
        concepts_result = await db.execute(concepts_query)
        concepts = concepts_result.scalars().all()
        
        # В реальной системе здесь будет более сложная логика определения
        # целевой сложности на основе профиля и концепций
        target_difficulty = original_content.difficulty
    
    # 2. Получение предпочтительного стиля обучения
    learning_style = learner_profile.learning_style
    
    # Вызов LLM для адаптации контента
    adapted_body = await llm_provider.adapt_content(
        original_content.body,
        target_difficulty,
        learning_style,
        learner_profile.preferences
    )
    
    # Создание адаптированного контента
    adapted_content = AdaptedContent(
        id=uuid.uuid4(),
        original_content_id=original_content.id,
        user_id=adaptation_request.user_id,
        title=original_content.title,
        body=adapted_body,
        difficulty=target_difficulty,
        adaptation_params=params
    )
    
    db.add(adapted_content)
    await db.commit()
    await db.refresh(adapted_content)
    
    # Преобразование AdaptedContent в ContentResponse
    return {
        "id": adapted_content.id,
        "title": adapted_content.title,
        "content_type": original_content.content_type,
        "body": adapted_content.body,
        "difficulty": adapted_content.difficulty,
        "concepts": [concept.id for concept in concepts],
        "metadata": {
            **original_content.metadata,
            "adaptation": {
                "original_content_id": original_content.id,
                "adapted_for_user": adaptation_request.user_id,
                "adaptation_params": params
            }
        },
        "created_at": adapted_content.created_at,
        "updated_at": adapted_content.updated_at
    }

async def create_learning_plan(db: AsyncSession, plan_request: LearningPlanRequest):
    """Создает план обучения для учащегося."""
    # В реальной реализации здесь будет вызов к адаптивным механизмам
    # для построения оптимального плана обучения
    
    # Пример плана обучения
    plan = {
        "plan_id": str(uuid.uuid4()),
        "user_id": str(plan_request.user_id),
        "created_at": datetime.now().isoformat(),
        "concepts": [str(concept_id) for concept_id in plan_request.concept_ids],
        "sessions": [
            {
                "session_id": str(uuid.uuid4()),
                "concepts": [
                    {
                        "concept_id": str(concept_id),
                        "name": f"Concept {i+1}",
                        "difficulty": 0.5,
                        "current_mastery": 0.0
                    }
                    for i, concept_id in enumerate(plan_request.concept_ids[:3])
                ],
                "estimated_duration_minutes": 30,
                "activities": [
                    {
                        "activity_id": str(uuid.uuid4()),
                        "activity_type": "learn",
                        "concept_id": str(plan_request.concept_ids[0]),
                        "difficulty": 0.5,
                        "duration_minutes": 15
                    },
                    {
                        "activity_id": str(uuid.uuid4()),
                        "activity_type": "assess",
                        "concept_id": str(plan_request.concept_ids[0]),
                        "difficulty": 0.5,
                        "duration_minutes": 10
                    }
                ]
            }
        ],
        "metadata": {
            "target_difficulty_curve": plan_request.plan_params.get("target_difficulty_curve", "gradual") if plan_request.plan_params else "gradual",
            "spaced_repetition": plan_request.plan_params.get("spaced_repetition", True) if plan_request.plan_params else True,
            "total_concepts": len(plan_request.concept_ids),
            "total_sessions": 1,
            "estimated_total_duration_minutes": 30
        }
    }
    
    return plan
