from celery import Celery
import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import Dict, Any, List, Optional
import uuid

# Настройка логирования
logger = logging.getLogger(__name__)

# Настройка Celery
celery_app = Celery(
    "adaptive_learning",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

# Импорт будет осуществляться после определения приложения Celery
# для избежания циклических импортов
from app.db.database import async_session
from app.services import profile_service, content_service, assessment_service

# Utility для запуска асинхронных функций в Celery
def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

@celery_app.task
def update_profile_from_interaction_task(user_id: str, interaction_data: Dict[str, Any]):
    """Задача для асинхронного обновления профиля на основе взаимодействия."""
    try:
        # Создание асинхронной сессии
        async def update_profile():
            async with async_session() as session:
                await profile_service.update_profile_from_interaction(
                    session, 
                    uuid.UUID(user_id),
                    interaction_data
                )
        
        # Запуск асинхронной функции
        run_async(update_profile())
        logger.info(f"Successfully updated profile for user {user_id}")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error updating profile for user {user_id}: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def generate_learning_plan_task(user_id: str, concept_ids: List[str], plan_params: Optional[Dict[str, Any]] = None):
    """Задача для асинхронной генерации плана обучения."""
    try:
        # Создание асинхронной сессии
        async def generate_plan():
            async with async_session() as session:
                plan_request = {
                    "user_id": uuid.UUID(user_id),
                    "concept_ids": [uuid.UUID(concept_id) for concept_id in concept_ids],
                    "plan_params": plan_params or {}
                }
                return await content_service.create_learning_plan(session, plan_request)
        
        # Запуск асинхронной функции
        plan = run_async(generate_plan())
        logger.info(f"Successfully generated learning plan for user {user_id}")
        return {"status": "success", "plan": plan}
    except Exception as e:
        logger.error(f"Error generating learning plan for user {user_id}: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def adapt_content_task(content_id: str, user_id: str, adaptation_params: Optional[Dict[str, Any]] = None):
    """Задача для асинхронной адаптации контента."""
    try:
        # Создание асинхронной сессии
        async def adapt():
            async with async_session() as session:
                adaptation_request = {
                    "content_id": uuid.UUID(content_id),
                    "user_id": uuid.UUID(user_id),
                    "adaptation_params": adaptation_params or {}
                }
                return await content_service.adapt_content(session, adaptation_request)
        
        # Запуск асинхронной функции
        adapted_content = run_async(adapt())
        logger.info(f"Successfully adapted content {content_id} for user {user_id}")
        return {"status": "success", "content": adapted_content}
    except Exception as e:
        logger.error(f"Error adapting content {content_id} for user {user_id}: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def create_assessment_task(user_id: str, concept_ids: List[str], difficulty_level: float = 0.5, 
                          assessment_type: str = "adaptive", max_questions: int = 5):
    """Задача для асинхронного создания оценки."""
    try:
        # Создание асинхронной сессии
        async def create_assessment():
            async with async_session() as session:
                assessment_request = {
                    "user_id": uuid.UUID(user_id),
                    "concept_ids": [uuid.UUID(concept_id) for concept_id in concept_ids],
                    "difficulty_level": difficulty_level,
                    "assessment_type": assessment_type,
                    "max_questions": max_questions
                }
                return await assessment_service.create_assessment(session, assessment_request)
        
        # Запуск асинхронной функции
        assessment = run_async(create_assessment())
        logger.info(f"Successfully created assessment for user {user_id}")
        return {"status": "success", "assessment": assessment}
    except Exception as e:
        logger.error(f"Error creating assessment for user {user_id}: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def submit_assessment_task(assessment_id: str, user_id: str, responses: List[Dict[str, Any]]):
    """Задача для асинхронной обработки ответов на оценку."""
    try:
        # Создание асинхронной сессии
        async def submit():
            async with async_session() as session:
                submission = {"responses": responses}
                return await assessment_service.submit_assessment(
                    session, 
                    uuid.UUID(assessment_id), 
                    uuid.UUID(user_id), 
                    submission
                )
        
        # Запуск асинхронной функции
        result = run_async(submit())
        logger.info(f"Successfully processed assessment {assessment_id} for user {user_id}")
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Error processing assessment {assessment_id} for user {user_id}: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def analyze_learning_interactions_task(user_id: str, time_range: str = "week"):
    """Задача для анализа взаимодействий пользователя и выработки рекомендаций."""
    try:
        # Создание асинхронной сессии
        async def analyze():
            async with async_session() as session:
                # В реальной реализации здесь будет вызов к сервису аналитики
                # для анализа взаимодействий и генерации рекомендаций
                
                # Упрощенная заглушка для примера
                recommendations = [
                    {
                        "type": "concept",
                        "id": str(uuid.uuid4()),
                        "name": "Рекомендуемая концепция",
                        "reason": "Основано на истории взаимодействий"
                    },
                    {
                        "type": "content",
                        "id": str(uuid.uuid4()),
                        "title": "Рекомендуемый контент",
                        "reason": "Соответствует вашему стилю обучения"
                    }
                ]
                
                return recommendations
        
        # Запуск асинхронной функции
        recommendations = run_async(analyze())
        logger.info(f"Successfully analyzed interactions for user {user_id}")
        return {"status": "success", "recommendations": recommendations}
    except Exception as e:
        logger.error(f"Error analyzing interactions for user {user_id}: {e}")
        return {"status": "error", "message": str(e)}
