import re
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

def extract_learning_style_from_text(text: str) -> Dict[str, float]:
    """Извлекает информацию о стиле обучения из текста."""
    # Упрощенная реализация
    styles = {
        "visual": 0.0,
        "auditory": 0.0,
        "kinesthetic": 0.0
    }
    
    # Ключевые слова, указывающие на стили обучения
    visual_keywords = ["смотреть", "видеть", "картинка", "изображение", "визуальный"]
    auditory_keywords = ["слушать", "слышать", "звук", "аудио", "говорить"]
    kinesthetic_keywords = ["делать", "чувствовать", "практика", "опыт", "движение"]
    
    text_lower = text.lower()
    
    # Подсчет упоминаний ключевых слов
    for keyword in visual_keywords:
        if keyword in text_lower:
            styles["visual"] += 0.2
    
    for keyword in auditory_keywords:
        if keyword in text_lower:
            styles["auditory"] += 0.2
    
    for keyword in kinesthetic_keywords:
        if keyword in text_lower:
            styles["kinesthetic"] += 0.2
    
    # Нормализация значений
    total = sum(styles.values())
    if total > 0:
        for style in styles:
            styles[style] = min(1.0, styles[style] / total)
    else:
        # Если нет данных, предполагаем равномерное распределение
        for style in styles:
            styles[style] = 1.0 / len(styles)
    
    return styles

def extract_concepts_from_text(text: str, concept_keywords: List[str]) -> List[str]:
    """Извлекает упоминания концепций из текста."""
    mentions = []
    
    text_lower = text.lower()
    for concept in concept_keywords:
        if concept.lower() in text_lower:
            mentions.append(concept)
    
    return mentions

def format_learning_profile(profile: Dict[str, Any]) -> str:
    """Форматирует профиль обучения для передачи в LLM."""
    formatted = []
    
    if "current_level" in profile:
        formatted.append(f"Текущий уровень знаний: {profile['current_level']:.2f}/1.0")
    
    if "learning_style" in profile:
        styles = profile["learning_style"]
        style_str = ", ".join([f"{style}: {score:.2f}" for style, score in styles.items()])
        formatted.append(f"Предпочтительные стили обучения: {style_str}")
    
    if "concept_mastery" in profile:
        mastery = profile["concept_mastery"]
        # Выбираем топ-5 концепций по уровню владения
        top_concepts = sorted(mastery.items(), key=lambda x: x[1], reverse=True)[:5]
        mastery_str = ", ".join([f"{concept}: {score:.2f}" for concept, score in top_concepts])
        formatted.append(f"Лучшее владение концепциями: {mastery_str}")
    
    if "goals" in profile:
        goals = profile["goals"]
        goals_str = ", ".join(goals)
        formatted.append(f"Цели обучения: {goals_str}")
    
    return "\n".join(formatted)

def safe_json_loads(text: str) -> Dict[str, Any]:
    """Безопасно загружает JSON из текста."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        return {}
