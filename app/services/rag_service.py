from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import uuid

from app.models.content import Concept, EducationalContent, content_concept

async def get_educational_context(db: AsyncSession, query: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Получает образовательный контекст на основе запроса и профиля пользователя."""
    # В реальной реализации здесь должен быть алгоритм поиска релевантного контента
    # с использованием векторных баз данных для семантического поиска
    
    # Упрощенная реализация - поиск по ключевым словам
    search_terms = query.lower().split()
    
    # Поиск релевантных концепций
    concepts_query = select(Concept).where(
        func.lower(Concept.name).in_(search_terms) | 
        func.lower(Concept.description).contains(query.lower())
    ).limit(3)
    
    concepts_result = await db.execute(concepts_query)
    concepts = concepts_result.scalars().all()
    
    # Поиск релевантного контента
    if concepts:
        # Если найдены концепции, ищем связанный контент
        concept_ids = [concept.id for concept in concepts]
        content_query = select(EducationalContent).join(
            content_concept, content_concept.c.content_id == EducationalContent.id
        ).where(
            content_concept.c.concept_id.in_(concept_ids)
        ).limit(5)
    else:
        # Если концепции не найдены, ищем контент напрямую
        content_query = select(EducationalContent).where(
            func.lower(EducationalContent.title).contains(query.lower()) | 
            func.lower(EducationalContent.body).contains(query.lower())
        ).limit(5)
    
    content_result = await db.execute(content_query)
    content_items = content_result.scalars().all()
    
    # Адаптация контекста под уровень и стиль пользователя
    # В реальной реализации здесь будет более сложная логика адаптации
    learning_style = user_profile.get("learning_style", {})
    preferences = user_profile.get("preferences", {})
    
    # Построение образовательного контекста
    educational_context = ""
    if content_items:
        for i, item in enumerate(content_items):
            educational_context += f"Document {i+1}: {item.title}\n{item.body}\n\n"
    else:
        educational_context = "Релевантный образовательный контент не найден."
    
    # Формирование профиля пользователя для передачи в LLM
    user_profile_text = "Профиль пользователя:\n"
    
    if learning_style:
        user_profile_text += "Стили обучения: " + ", ".join([f"{style}: {score:.2f}" for style, score in learning_style.items()]) + "\n"
    
    if "interests" in preferences:
        user_profile_text += "Интересы: " + ", ".join(preferences["interests"]) + "\n"
    
    # Формирование контекста
    context = {
        "educational_context": educational_context,
        "user_profile": user_profile_text,
        "concepts_referenced": [concept.name for concept in concepts]
    }
    
    return context
