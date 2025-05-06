from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.models.assessment import LearningInteraction, LearningSession
from app.api.schemas import ChatRequest, ChatResponse
from app.services.llm_service import get_llm_provider
from app.services.rag_service import get_educational_context
from app.services.profile_service import get_profile

async def process_message(db: AsyncSession, request: ChatRequest) -> ChatResponse:
    """Обрабатывает сообщение чата и генерирует ответ."""
    # Создание или получение сессии
    session_id = request.session_id or uuid.uuid4()
    
    if not request.session_id:
        # Создание новой сессии
        session = LearningSession(
            id=session_id,
            user_id=request.user_id,
            session_type="chat",
            metadata=request.context or {}
        )
        db.add(session)
        await db.commit()
    
    # Сохранение сообщения пользователя
    user_message = LearningInteraction(
        id=uuid.uuid4(),
        user_id=request.user_id,
        session_id=session_id,
        interaction_type="chat_message",
        content={"role": "user", "message": request.message},
        metadata=request.context or {},
        timestamp=datetime.now()
    )
    
    db.add(user_message)
    await db.commit()
    
    # Получение профиля пользователя
    try:
        profile = await get_profile(db, request.user_id)
    except ValueError:
        # Если профиль не найден, используем базовые настройки
        profile = {"learning_style": {}, "cognitive_profile": {}, "preferences": {}}
    
    # Получение образовательного контекста
    context = await get_educational_context(db, request.message, profile)
    
    # Получение LLM для генерации ответа
    llm_provider = get_llm_provider()
    
    # Составление промпта для LLM
    prompt = f"""
    Вы - адаптивный образовательный ассистент, помогающий пользователю в обучении.
    
    Сообщение пользователя: {request.message}
    
    Образовательный контекст:
    {context["educational_context"]}
    
    Профиль пользователя:
    {context["user_profile"]}
    
    Отвечайте в соответствии с профилем пользователя и предоставленным образовательным контекстом.
    Будьте полезны, точны и адаптивны - подстраивайте объяснения под стиль обучения и уровень пользователя.
    """
    
    # Генерация ответа с помощью LLM
    llm_response = await llm_provider.generate(
        prompt=prompt,
        max_tokens=1500,
        temperature=0.7,
        metadata={
            "system_prompt": "Вы - адаптивный образовательный ассистент, который персонализирует ответы под профиль конкретного учащегося."
        }
    )
    
    # Создание ответа
    response = ChatResponse(
        message_id=uuid.uuid4(),
        role="assistant",
        content=llm_response.text,
        session_id=session_id,
        timestamp=datetime.now(),
        metadata={
            "concepts_referenced": context.get("concepts_referenced", []),
            "adaptive_context": True
        }
    )
    
    # Сохранение ответа ассистента
    assistant_message = LearningInteraction(
        id=uuid.uuid4(),
        user_id=request.user_id,
        session_id=session_id,
        interaction_type="chat_message",
        content={"role": "assistant", "message": response.content},
        metadata=response.metadata,
        timestamp=response.timestamp
    )
    
    db.add(assistant_message)
    await db.commit()
    
    return response
