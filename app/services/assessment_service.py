from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime
from typing import Dict, Any, List

from app.models.assessment import Assessment, AssessmentQuestion, AssessmentResponse
from app.api.schemas import AssessmentRequest, AssessmentSubmission
from app.services.llm_service import get_llm_provider
from app.services.profile_service import update_concept_mastery

async def create_assessment(db: AsyncSession, assessment_request: AssessmentRequest):
    """Создает новую оценку для учащегося."""
    # Создание оценки
    assessment = Assessment(
        id=uuid.uuid4(),
        user_id=assessment_request.user_id,
        assessment_type=assessment_request.assessment_type,
        metadata={
            "difficulty_level": assessment_request.difficulty_level,
            "max_questions": assessment_request.max_questions
        }
    )
    
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    
    # Получение LLM для генерации вопросов
    llm_provider = get_llm_provider()
    
    # Генерация вопросов
    questions = []
    
    for i, concept_id in enumerate(assessment_request.concept_ids[:assessment_request.max_questions]):
        # В реальной реализации здесь будет более сложная логика генерации вопросов
        question_content = {
            "text": f"Вопрос {i+1} о концепции {concept_id}",
            "options": [
                {"id": "a", "text": "Вариант A"},
                {"id": "b", "text": "Вариант B"},
                {"id": "c", "text": "Вариант C"},
                {"id": "d", "text": "Вариант D"}
            ],
            "correct_answer": "a"
        }
        
        # Создание вопроса
        question = AssessmentQuestion(
            id=uuid.uuid4(),
            assessment_id=assessment.id,
            concept_id=concept_id,
            question_type="multiple_choice",
            content=question_content,
            difficulty=assessment_request.difficulty_level
        )
        
        db.add(question)
        
        # Добавление вопроса в список для ответа
        questions.append({
            "question_id": question.id,
            "concept_id": concept_id,
            "text": question_content["text"],
            "options": question_content["options"],
            "difficulty": question.difficulty
        })
    
    await db.commit()
    
    # Формирование ответа
    return {
        "assessment_id": assessment.id,
        "user_id": assessment_request.user_id,
        "questions": questions,
        "concept_ids": assessment_request.concept_ids[:assessment_request.max_questions],
        "created_at": assessment.created_at,
        "metadata": assessment.metadata
    }

async def submit_assessment(db: AsyncSession, assessment_id: uuid.UUID, user_id: uuid.UUID, submission: AssessmentSubmission):
    """Отправляет ответы на оценку и получает результаты."""
    # Получение оценки
    assessment_query = select(Assessment).where(Assessment.id == assessment_id)
    assessment_result = await db.execute(assessment_query)
    assessment = assessment_result.scalars().first()
    if not assessment:
        raise ValueError(f"Assessment with id {assessment_id} not found")
    
    # Проверка, что оценка принадлежит пользователю
    if assessment.user_id != user_id:
        raise ValueError(f"Assessment {assessment_id} does not belong to user {user_id}")
    
    # Получение вопросов
    questions_query = select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == assessment_id)
    questions_result = await db.execute(questions_query)
    questions = {str(q.id): q for q in questions_result.scalars().all()}
    
    # Обработка ответов
    concept_results = {}
    total_score = 0.0
    
    for response_data in submission.responses:
        question_id = response_data.get("question_id")
        answer = response_data.get("answer")
        
        if question_id not in questions:
            continue
        
        question = questions[question_id]
        correct_answer = question.content.get("correct_answer")
        is_correct = answer == correct_answer
        score = 1.0 if is_correct else 0.0
        
        # Сохранение ответа
        response = AssessmentResponse(
            id=uuid.uuid4(),
            assessment_id=assessment_id,
            question_id=question_id,
            user_id=user_id,
            response={"answer": answer},
            score=score,
            feedback="Correct answer" if is_correct else f"Incorrect answer. The correct answer is {correct_answer}",
            response_time_seconds=response_data.get("response_time_seconds", 0)
        )
        
        db.add(response)
        
        # Обновление результатов для концепции
        concept_id = question.concept_id
        if concept_id not in concept_results:
            concept_results[concept_id] = {
                "score": 0.0,
                "questions_count": 0,
                "correct_count": 0
            }
        
        concept_results[concept_id]["questions_count"] += 1
        if is_correct:
            concept_results[concept_id]["correct_count"] += 1
        
        # Обновление среднего балла для концепции
        concept_results[concept_id]["score"] = (
            concept_results[concept_id]["correct_count"] / concept_results[concept_id]["questions_count"]
        )
        
        total_score += score
    
    # Вычисление среднего общего балла
    if submission.responses:
        total_score /= len(submission.responses)
    
    # Обновление статуса оценки
    assessment.completed_at = datetime.now()
    await db.commit()
    
    # Обновление уровня владения концепциями
    for concept_id, result in concept_results.items():
        await update_concept_mastery(db, user_id, concept_id, {
            "score": result["score"],
            "confidence": 0.8  # Высокая уверенность для прямой оценки
        })
    
    # Генерация обратной связи
    feedback = {
        "overall_feedback": "Хорошая работа! Продолжайте практиковаться для улучшения понимания.",
        "concept_feedback": {
            str(concept_id): f"Вы получили {result['score']:.2f} баллов по вопросам, связанным с этой концепцией."
            for concept_id, result in concept_results.items()
        }
    }
    
    # Формирование результата
    result = {
        "result_id": str(uuid.uuid4()),
        "assessment_id": assessment_id,
        "user_id": user_id,
        "concept_results": concept_results,
        "total_score": total_score,
        "feedback": feedback,
        "created_at": datetime.now()
    }
    
    return result
