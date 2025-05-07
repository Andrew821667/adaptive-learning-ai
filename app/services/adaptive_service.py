import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json
import logging

from app.models.user import LearningProfile, ConceptMastery
from app.models.content import Concept, EducationalContent, content_concept
from app.services.llm_service import get_llm_provider
from app.services.profile_service import get_profile, get_concept_mastery

logger = logging.getLogger(__name__)

class AdaptiveMechanisms:
    """Класс адаптивных механизмов для персонализации обучения."""
    
    @staticmethod
    async def adapt_content(
        db: AsyncSession,
        content_id: uuid.UUID,
        user_id: uuid.UUID,
        adaptation_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Адаптирует образовательный контент под профиль учащегося."""
        
        # Получение профиля пользователя
        user_profile = await get_profile(db, user_id)
        
        # Получение исходного контента
        content_query = select(EducationalContent).where(EducationalContent.id == content_id)
        content_result = await db.execute(content_query)
        original_content = content_result.scalars().first()
        
        if not original_content:
            raise ValueError(f"Content with id {content_id} not found")
        
        # Получение связанных концепций
        related_concepts_query = select(Concept).join(
            content_concept, content_concept.c.concept_id == Concept.id
        ).where(
            content_concept.c.content_id == content_id
        )
        related_concepts_result = await db.execute(related_concepts_query)
        related_concepts = related_concepts_result.scalars().all()
        
        # Определение параметров адаптации
        params = {
            "target_difficulty": 0.5,
            "preferred_learning_style": "balanced",
            "simplify_language": False,
            "add_examples": True,
            "personalize_examples": True
        }
        
        if adaptation_params:
            params.update(adaptation_params)
        
        # Корректировка целевой сложности на основе профиля
        if related_concepts:
            # Получение уровней владения пользователя релевантными концепциями
            concept_mastery_list = await get_concept_mastery(db, user_id)
            concept_mastery_dict = {
                str(mastery.concept_id): mastery.mastery_level 
                for mastery in concept_mastery_list
            }
            
            # Вычисление среднего уровня владения релевантными концепциями
            relevant_masteries = [
                concept_mastery_dict.get(str(concept.id), 0.0) 
                for concept in related_concepts
                if str(concept.id) in concept_mastery_dict
            ]
            
            if relevant_masteries:
                avg_mastery = sum(relevant_masteries) / len(relevant_masteries)
                # Целевая сложность: немного выше текущего уровня владения 
                # (зона ближайшего развития)
                params["target_difficulty"] = min(1.0, avg_mastery + 0.2)
        
        # Определение предпочтительного стиля обучения
        learning_style = user_profile.learning_style if user_profile else {}
        
        if learning_style:
            # Упрощенное определение преобладающего стиля
            dominant_style = "balanced"
            max_score = 0.5  # Пороговое значение
            
            for style, score in learning_style.items():
                if score > max_score:
                    max_score = score
                    dominant_style = style
            
            params["preferred_learning_style"] = dominant_style
        
        # Получение предпочтений пользователя
        preferences = user_profile.preferences if user_profile else {}
        
        # Использование LLM для адаптации контента
        llm_provider = get_llm_provider()
        
        try:
            # Адаптация контента с использованием LLM
            adapted_body = await llm_provider.adapt_content(
                content=original_content.body,
                target_difficulty=params["target_difficulty"],
                learning_style=learning_style,
                preferences=preferences
            )
            
            # Создание копии исходного контента с адаптированными данными
            adapted_content = {
                "id": str(uuid.uuid4()),
                "original_content_id": str(content_id),
                "user_id": str(user_id),
                "title": original_content.title,
                "content_type": original_content.content_type,
                "body": adapted_body,
                "difficulty": params["target_difficulty"],
                "concepts": [str(concept.id) for concept in related_concepts],
                "created_at": datetime.now().isoformat(),
                "metadata": {
                    "adaptation": {
                        "original_difficulty": original_content.difficulty,
                        "target_difficulty": params["target_difficulty"],
                        "preferred_learning_style": params["preferred_learning_style"],
                        "adaptation_params": params
                    }
                }
            }
            
            return adapted_content
            
        except Exception as e:
            logger.error(f"Error adapting content: {e}")
            # В случае ошибки возвращаем оригинальный контент
            return {
                "id": str(content_id),
                "title": original_content.title,
                "content_type": original_content.content_type,
                "body": original_content.body,
                "difficulty": original_content.difficulty,
                "concepts": [str(concept.id) for concept in related_concepts],
                "created_at": original_content.created_at.isoformat(),
                "updated_at": original_content.updated_at.isoformat(),
                "metadata": {
                    "error": f"Failed to adapt content: {str(e)}",
                    "original_metadata": original_content.metadata
                }
            }
    
    @staticmethod
    async def generate_adaptive_feedback(
        db: AsyncSession,
        assessment_result: Dict[str, Any],
        user_id: uuid.UUID,
        feedback_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Генерирует адаптивную обратную связь по результатам оценки."""
        
        # Получение профиля пользователя
        user_profile = await get_profile(db, user_id)
        
        # Определение параметров обратной связи
        params = {
            "feedback_style": "constructive",
            "motivational_tone": True,
            "include_next_steps": True,
            "detail_level": "moderate"
        }
        
        if feedback_params:
            params.update(feedback_params)
        
        # Адаптация стиля обратной связи на основе профиля
        learning_style = user_profile.learning_style if user_profile else {}
        preferences = user_profile.preferences if user_profile else {}
        
        feedback_style = params["feedback_style"]
        
        if preferences and "feedback_preferences" in preferences:
            feedback_preferences = preferences.get("feedback_preferences", {})
            
            # Учет предпочтений по стилю обратной связи
            if "preferred_style" in feedback_preferences:
                feedback_style = feedback_preferences["preferred_style"]
        
        # Получение мотивационного профиля (если есть)
        motivation_profile = preferences.get("motivation_profile", {})
        
        # Создание промпта для генерации обратной связи
        llm_provider = get_llm_provider()
        
        try:
            # Подготовка промпта для LLM
            prompt = f"""
            Сгенерируйте персонализированную образовательную обратную связь для учащегося на основе результатов оценки.
            
            Результаты оценки:
            - Оценка: {assessment_result.get('total_score', 0.0):.2f} из 1.0
            - Сильные стороны: {', '.join(assessment_result.get('strengths', ['Не указано']))}
            - Области для улучшения: {', '.join(assessment_result.get('areas_for_improvement', ['Не указано']))}
            
            Профиль учащегося:
            - Стиль обучения: {json.dumps(learning_style)}
            - Мотивационный профиль: {json.dumps(motivation_profile)}
            
            Параметры обратной связи:
            - Стиль: {feedback_style}
            - Мотивационный тон: {params['motivational_tone']}
            - Включать следующие шаги: {params['include_next_steps']}
            - Уровень детализации: {params['detail_level']}
            
            Сгенерируйте персонализированную обратную связь, которая:
            1. Обращается к конкретным сильным и слабым сторонам в ответе учащегося
            2. Адаптирована к его стилю обучения и мотивационному профилю
            3. Предоставляет конкретные предложения по улучшению
            4. Использует {feedback_style} тон, который будет хорошо воспринят учащимся
            5. {"Включает конкретные следующие шаги или предложения по практике" if params['include_next_steps'] else "Фокусируется только на текущем ответе"}
            
            Верните обратную связь как связный абзац без метакомментариев или заголовков разделов.
            """
            
            # Генерация обратной связи с помощью LLM
            response = await llm_provider.generate(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.5,
                metadata={"system_prompt": "Вы - опытный педагог, который предоставляет полезную и мотивирующую обратную связь учащимся."}
            )
            
            # Формирование итогового объекта обратной связи
            feedback = {
                "feedback_id": str(uuid.uuid4()),
                "assessment_id": assessment_result.get("result_id", "unknown"),
                "content": response.text.strip(),
                "type": "adaptive",
                "metadata": {
                    "feedback_style": feedback_style,
                    "score_context": assessment_result.get("total_score", 0.0),
                    "generation_params": params,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating adaptive feedback: {e}")
            # В случае ошибки возвращаем базовую обратную связь
            return {
                "feedback_id": str(uuid.uuid4()),
                "assessment_id": assessment_result.get("result_id", "unknown"),
                "content": f"Ваш общий результат: {assessment_result.get('total_score', 0.0):.2f} из 1.0. Продолжайте практиковаться для улучшения понимания.",
                "type": "basic",
                "metadata": {
                    "error": f"Failed to generate adaptive feedback: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    @staticmethod
    async def optimize_learning_path(
        db: AsyncSession,
        user_id: uuid.UUID,
        concept_ids: List[uuid.UUID],
        path_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Оптимизирует путь обучения на основе профиля учащегося и целевых концепций."""
        
        # Получение профиля пользователя
        user_profile = await get_profile(db, user_id)
        
        # Определение параметров оптимизации
        params = {
            "target_difficulty_curve": "gradual",  # gradual, challenging, adaptive
            "max_concepts_per_session": 3,
            "spaced_repetition": True,
            "include_assessments": True
        }
        
        if path_params:
            params.update(path_params)
        
        # Получение данных о концепциях
        concept_data = {}
        for concept_id in concept_ids:
            concept_query = select(Concept).where(Concept.id == concept_id)
            concept_result = await db.execute(concept_query)
            concept = concept_result.scalars().first()
            
            if concept:
                # Получение предварительных требований для концепции
                prereq_query = select(Concept).join(
                    # Здесь предполагается наличие таблицы связей concept_prerequisites
                    # В реальном приложении эту таблицу нужно создать
                    # content_prerequisites, content_prerequisites.c.target_concept_id == Concept.id
                ).where(
                    # content_prerequisites.c.source_concept_id == concept_id
                    Concept.id != concept_id  # Временная заглушка
                ).limit(3)  # Для примера ограничиваем количество предварительных требований
                
                prereq_result = await db.execute(prereq_query)
                prerequisites = prereq_result.scalars().all()
                
                concept_data[str(concept_id)] = {
                    "name": concept.name,
                    "difficulty": concept.difficulty,
                    "prerequisites": [str(prereq.id) for prereq in prerequisites],
                    "domain": concept.domain
                }
        
        # Получение уровней владения концепциями
        concept_mastery_list = await get_concept_mastery(db, user_id)
        mastery_levels = {
            str(mastery.concept_id): mastery.mastery_level 
            for mastery in concept_mastery_list
        }
        
        # Добавление уровней владения для концепций, которых нет в профиле
        for concept_id in concept_ids:
            if str(concept_id) not in mastery_levels:
                mastery_levels[str(concept_id)] = 0.0
        
        # Создание графа зависимостей концепций
        dependency_graph = {}
        for concept_id, data in concept_data.items():
            dependency_graph[concept_id] = data["prerequisites"]
        
        # Топологическая сортировка для определения базового порядка
        def topological_sort(graph):
            """Выполняет топологическую сортировку графа."""
            visited = set()
            temp = set()
            order = []
            
            def dfs(node):
                if node in temp:
                    # В случае циклической зависимости продолжаем с другими узлами
                    return
                if node in visited:
                    return
                
                temp.add(node)
                for neighbor in graph.get(node, []):
                    if neighbor in graph:  # Проверка наличия соседа в графе
                        dfs(neighbor)
                
                temp.remove(node)
                visited.add(node)
                order.append(node)
            
            for node in graph:
                if node not in visited:
                    dfs(node)
            
            return order[::-1]  # Обратный порядок для получения правильной последовательности
        
        # Получение базового порядка концепций с учетом зависимостей
        try:
            base_sequence = topological_sort(dependency_graph)
            
            # Фильтрация только до запрошенных концепций с сохранением порядка
            base_sequence = [c for c in base_sequence if c in [str(cid) for cid in concept_ids]]
            
            # Добавление концепций, которые не попали в сортировку
            missing_concepts = [str(c) for c in concept_ids if str(c) not in base_sequence]
            base_sequence.extend(missing_concepts)
        except Exception as e:
            logger.error(f"Error in topological sort: {e}")
            # В случае ошибки используем исходный порядок концепций
            base_sequence = [str(c) for c in concept_ids]
        
        # Оптимизация последовательности на основе параметров
        optimized_sequence = []
        
        if params["target_difficulty_curve"] == "gradual":
            # Сортировка по сложности (с учетом текущего уровня владения)
            weighted_difficulty = {
                c: concept_data.get(c, {}).get("difficulty", 0.5) * (1 - mastery_levels.get(c, 0.0)) 
                for c in base_sequence
            }
            optimized_sequence = sorted(base_sequence, key=lambda c: weighted_difficulty.get(c, 0.5))
            
        elif params["target_difficulty_curve"] == "challenging":
            # Сначала базовые зависимости, затем по убыванию сложности
            levels = []
            remaining = set(base_sequence)
            
            while remaining:
                # Находим концепции, чьи все зависимости уже в уровнях
                level_concepts = []
                for concept in list(remaining):
                    if all(prereq not in remaining for prereq in dependency_graph.get(concept, [])):
                        level_concepts.append(concept)
                        remaining.remove(concept)
                
                if not level_concepts and remaining:
                    # Если не можем добавить ни одной концепции, но остались концепции,
                    # добавляем оставшиеся (возможно, из-за циклических зависимостей)
                    level_concepts = list(remaining)
                    remaining.clear()
                
                # Сортируем уровень по сложности (от сложного к простому)
                level_concepts.sort(
                    key=lambda c: concept_data.get(c, {}).get("difficulty", 0.5), 
                    reverse=True
                )
                levels.append(level_concepts)
            
            # Соединяем все уровни
            for level in levels:
                optimized_sequence.extend(level)
            
        else:  # "adaptive" или другое
            # Адаптивный подход - чередуем разные уровни сложности
            difficulty_bands = {
                "low": [],
                "medium": [],
                "high": []
            }
            
            for concept in base_sequence:
                # Эффективная сложность: сложность * (1 - уровень владения)
                effective_difficulty = concept_data.get(concept, {}).get("difficulty", 0.5) * (1 - mastery_levels.get(concept, 0.0))
                
                if effective_difficulty < 0.3:
                    difficulty_bands["low"].append(concept)
                elif effective_difficulty < 0.7:
                    difficulty_bands["medium"].append(concept)
                else:
                    difficulty_bands["high"].append(concept)
            
            # Формирование последовательности - сначала простые, затем средние, потом сложные
            optimized_sequence = (
                difficulty_bands["low"] + 
                difficulty_bands["medium"] + 
                difficulty_bands["high"]
            )
        
        # Разбиение на учебные сессии
        max_per_session = params["max_concepts_per_session"]
        sessions = []
        
        for i in range(0, len(optimized_sequence), max_per_session):
            session_concepts = optimized_sequence[i:i+max_per_session]
            
            # Создание сессии
            session = {
                "session_id": str(uuid.uuid4()),
                "concepts": [
                    {
                        "concept_id": concept_id,
                        "name": concept_data.get(concept_id, {}).get("name", f"Concept {concept_id}"),
                        "difficulty": concept_data.get(concept_id, {}).get("difficulty", 0.5),
                        "current_mastery": mastery_levels.get(concept_id, 0.0)
                    }
                    for concept_id in session_concepts
                ],
                "estimated_duration_minutes": 30 * len(session_concepts),
                "activities": []
            }
            
            # Добавление активностей для каждой концепции
            for concept_id in session_concepts:
                # Основное изучение
                session["activities"].append({
                    "activity_id": str(uuid.uuid4()),
                    "activity_type": "learn",
                    "concept_id": concept_id,
                    "difficulty": concept_data.get(concept_id, {}).get("difficulty", 0.5),
                    "duration_minutes": 15
                })
                
                # Добавление оценки, если требуется
                if params["include_assessments"]:
                    session["activities"].append({
                        "activity_id": str(uuid.uuid4()),
                        "activity_type": "assess",
                        "concept_id": concept_id,
                        "difficulty": concept_data.get(concept_id, {}).get("difficulty", 0.5),
                        "duration_minutes": 10
                    })
            
            sessions.append(session)
        
        # Если включено интервальное повторение, добавляем повторения в последующие сессии
        if params["spaced_repetition"] and len(sessions) > 1:
            for i in range(1, len(sessions)):
                # Получаем концепции из предыдущих сессий для повторения
                repeat_candidates = []
                
                # Из предыдущей сессии повторяем все
                for concept in sessions[i-1]["concepts"]:
                    repeat_candidates.append(concept["concept_id"])
                
                # Из более ранних сессий повторяем выборочно
                if i > 1:
                    for j in range(0, i-1):
                        for concept in sessions[j]["concepts"]:
                            # Повторяем только концепции с низким уровнем владения
                            if mastery_levels.get(concept["concept_id"], 0.0) < 0.6:
                                repeat_candidates.append(concept["concept_id"])
                
                # Ограничиваем количество повторений
                repeat_candidates = repeat_candidates[:2]  # Не более 2 повторений
                
                # Добавляем активности повторения
                for concept_id in repeat_candidates:
                    sessions[i]["activities"].append({
                        "activity_id": str(uuid.uuid4()),
                        "activity_type": "review",
                        "concept_id": concept_id,
                        "difficulty": concept_data.get(concept_id, {}).get("difficulty", 0.5),
                        "duration_minutes": 5
                    })
        
        # Формирование итогового плана обучения
        learning_plan = {
            "plan_id": str(uuid.uuid4()),
            "user_id": str(user_id),
            "created_at": datetime.now().isoformat(),
            "concepts": [str(cid) for cid in concept_ids],
            "sessions": sessions,
            "metadata": {
                "target_difficulty_curve": params["target_difficulty_curve"],
                "spaced_repetition": params["spaced_repetition"],
                "total_concepts": len(concept_ids),
                "total_sessions": len(sessions),
                "estimated_total_duration_minutes": sum(session["estimated_duration_minutes"] for session in sessions)
            }
        }
        
        return learning_plan
