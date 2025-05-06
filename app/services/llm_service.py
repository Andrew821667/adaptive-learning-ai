import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
import json
import logging
from pydantic import BaseModel
import asyncio

logger = logging.getLogger(__name__)

class LLMResponse(BaseModel):
    text: str
    model: str
    metadata: Dict[str, Any] = {}

class LLMProvider(ABC):
    """Абстрактный класс для провайдера LLM."""
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        max_tokens: int = 1000, 
        temperature: float = 0.7,
        stop_sequences: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """Генерирует текст с помощью LLM."""
        pass
    
    @abstractmethod
    async def adapt_content(
        self,
        content: str,
        target_difficulty: float,
        learning_style: Dict[str, float],
        preferences: Dict[str, Any]
    ) -> str:
        """Адаптирует образовательный контент."""
        pass

class AnthropicProvider(LLMProvider):
    """Провайдер для работы с API Anthropic Claude."""
    
    def __init__(
        self, 
        api_key: str, 
        default_model: str = "claude-3-opus-20240229",
        timeout: int = 30
    ):
        self.api_key = api_key
        self.default_model = default_model
        self.timeout = timeout
        self.api_url = "https://api.anthropic.com/v1/messages"
    
    async def generate(
        self, 
        prompt: str, 
        max_tokens: int = 1000, 
        temperature: float = 0.7,
        stop_sequences: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """Генерирует текст с помощью Claude."""
        system_prompt = metadata.get("system_prompt", "")
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": metadata.get("model", self.default_model),
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        if stop_sequences:
            data["stop_sequences"] = stop_sequences
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=data
                )
                
                response.raise_for_status()
                response_data = response.json()
                
                return LLMResponse(
                    text=response_data.get("content", [{"text": ""}])[0]["text"],
                    model=response_data.get("model", self.default_model),
                    metadata={
                        "usage": response_data.get("usage", {}),
                        "id": response_data.get("id", "")
                    }
                )
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {e}")
            raise
    
    async def adapt_content(
        self,
        content: str,
        target_difficulty: float,
        learning_style: Dict[str, float],
        preferences: Dict[str, Any]
    ) -> str:
        """Адаптирует образовательный контент с помощью Claude."""
        # Определение доминирующего стиля обучения
        dominant_style = max(learning_style.items(), key=lambda x: x[1])[0] if learning_style else "balanced"
        
        # Создание стилевых рекомендаций для промпта
        style_guidance = ""
        if dominant_style == "visual":
            style_guidance = "Включите визуальные описания, используйте пространственные метафоры и визуальную лексику."
        elif dominant_style == "auditory":
            style_guidance = "Используйте ритмичный язык, включайте диалоги и обсуждения. Подчеркивайте звуковые аспекты."
        elif dominant_style == "kinesthetic":
            style_guidance = "Используйте примеры, связанные с движением и физическим взаимодействием. Включайте практические приложения."
        else:
            style_guidance = "Сбалансированно используйте различные стили представления информации."
        
        # Учет интересов пользователя
        interests = preferences.get("interests", [])
        background = preferences.get("background", "general")
        
        # Формирование промпта для адаптации
        prompt = f"""
        Адаптируйте следующий образовательный контент под уровень сложности {target_difficulty:.2f} (от 0.0 до 1.0, где 0.0 - очень простой, 1.0 - очень сложный).
        
        Используйте следующие рекомендации по стилю обучения:
        {style_guidance}
        
        {"Учитывайте следующие интересы пользователя: " + ", ".join(interests) if interests else ""}
        {"Учитывайте образовательный/профессиональный фон пользователя: " + background if background != "general" else ""}
        
        Исходный контент:
        {content}
        
        При адаптации:
        1. Сохраните ключевые концепции и цели обучения
        2. Отрегулируйте сложность языка, глубину объяснений и уровень детализации
        3. Адаптируйте стиль представления и примеры под предпочтения пользователя
        4. Сохраните общую структуру, сходную с исходным контентом
        
        Верните только адаптированный контент без пояснений или метакомментариев.
        """
        
        # Вызов LLM для адаптации
        response = await self.generate(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.4,
            metadata={"system_prompt": "Вы - эксперт по адаптивному обучению, который помогает персонализировать образовательный контент под нужды конкретных учащихся."}
        )
        
        return response.text

class OpenAIProvider(LLMProvider):
    """Провайдер для работы с API OpenAI."""
    
    def __init__(
        self, 
        api_key: str, 
        default_model: str = "gpt-4",
        timeout: int = 30
    ):
        self.api_key = api_key
        self.default_model = default_model
        self.timeout = timeout
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    async def generate(
        self, 
        prompt: str, 
        max_tokens: int = 1000, 
        temperature: float = 0.7,
        stop_sequences: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """Генерирует текст с помощью модели OpenAI."""
        system_prompt = metadata.get("system_prompt", "Вы - полезный образовательный ассистент.")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": metadata.get("model", self.default_model),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if stop_sequences:
            data["stop"] = stop_sequences
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=data
                )
                
                response.raise_for_status()
                response_data = response.json()
                
                return LLMResponse(
                    text=response_data["choices"][0]["message"]["content"],
                    model=response_data.get("model", self.default_model),
                    metadata={
                        "usage": response_data.get("usage", {}),
                        "id": response_data.get("id", "")
                    }
                )
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise
    
    async def adapt_content(
        self,
        content: str,
        target_difficulty: float,
        learning_style: Dict[str, float],
        preferences: Dict[str, Any]
    ) -> str:
        """Адаптирует образовательный контент с помощью модели OpenAI."""
        # Реализация аналогична методу для Claude
        dominant_style = max(learning_style.items(), key=lambda x: x[1])[0] if learning_style else "balanced"
        
        # Создание стилевых рекомендаций
        style_guidance = ""
        if dominant_style == "visual":
            style_guidance = "Включите визуальные описания, используйте пространственные метафоры и визуальную лексику."
        elif dominant_style == "auditory":
            style_guidance = "Используйте ритмичный язык, включайте диалоги и обсуждения. Подчеркивайте звуковые аспекты."
        elif dominant_style == "kinesthetic":
            style_guidance = "Используйте примеры, связанные с движением и физическим взаимодействием. Включайте практические приложения."
        else:
            style_guidance = "Сбалансированно используйте различные стили представления информации."
        
        # Учет интересов пользователя
        interests = preferences.get("interests", [])
        background = preferences.get("background", "general")
        
        # Формирование промпта для адаптации
        prompt = f"""
        Адаптируйте следующий образовательный контент под уровень сложности {target_difficulty:.2f} (от 0.0 до 1.0, где 0.0 - очень простой, 1.0 - очень сложный).
        
        Используйте следующие рекомендации по стилю обучения:
        {style_guidance}
        
        {"Учитывайте следующие интересы пользователя: " + ", ".join(interests) if interests else ""}
        {"Учитывайте образовательный/профессиональный фон пользователя: " + background if background != "general" else ""}
        
        Исходный контент:
        {content}
        
        При адаптации:
        1. Сохраните ключевые концепции и цели обучения
        2. Отрегулируйте сложность языка, глубину объяснений и уровень детализации
        3. Адаптируйте стиль представления и примеры под предпочтения пользователя
        4. Сохраните общую структуру, сходную с исходным контентом
        
        Верните только адаптированный контент без пояснений или метакомментариев.
        """
        
        # Вызов LLM для адаптации
        response = await self.generate(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.4,
            metadata={"system_prompt": "Вы - эксперт по адаптивному обучению, который помогает персонализировать образовательный контент под нужды конкретных учащихся."}
        )
        
        return response.text

def get_llm_provider() -> LLMProvider:
    """Возвращает экземпляр провайдера LLM в зависимости от настроек."""
    provider_type = os.getenv("LLM_PROVIDER", "anthropic")
    
    if provider_type == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        return AnthropicProvider(api_key=api_key)
    elif provider_type == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        return OpenAIProvider(api_key=api_key)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_type}")
