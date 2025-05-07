from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import uuid

from app.db.database import get_db
from app.api import schemas
from app.services.adaptive_service import AdaptiveMechanisms

router = APIRouter()

@router.post("/content/adapt", response_model=Dict[str, Any])
async def adapt_content(
    request: schemas.AdaptationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Адаптирует образовательный контент под профиль учащегося.
    """
    try:
        content_id = request.content_id
        user_id = request.user_id
        adaptation_params = request.adaptation_params
        
        adapted_content = await AdaptiveMechanisms.adapt_content(
            db=db,
            content_id=content_id,
            user_id=user_id,
            adaptation_params=adaptation_params
        )
        
        return adapted_content
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error adapting content: {str(e)}")

@router.post("/feedback/generate", response_model=Dict[str, Any])
async def generate_adaptive_feedback(
    assessment_result: Dict[str, Any],
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Генерирует адаптивную обратную связь по результатам оценки.
    """
    try:
        feedback = await AdaptiveMechanisms.generate_adaptive_feedback(
            db=db,
            assessment_result=assessment_result,
            user_id=user_id
        )
        
        return feedback
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generating feedback: {str(e)}")

@router.post("/learning/path", response_model=Dict[str, Any])
async def optimize_learning_path(
    user_id: uuid.UUID,
    concept_ids: List[uuid.UUID],
    path_params: Dict[str, Any] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Оптимизирует путь обучения на основе профиля учащегося и целевых концепций.
    """
    try:
        learning_path = await AdaptiveMechanisms.optimize_learning_path(
            db=db,
            user_id=user_id,
            concept_ids=concept_ids,
            path_params=path_params
        )
        
        return learning_path
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error optimizing learning path: {str(e)}")
