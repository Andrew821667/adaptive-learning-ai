import pytest
from fastapi import status
from httpx import AsyncClient
import uuid

from app.main import app
from app.models.user import User, LearningProfile
from app.services.auth_service import get_password_hash

# Вспомогательная функция для создания пользователя и получения токена
async def create_user_and_get_token(async_db_session, username="testuser", role="student"):
    # Создание тестового пользователя
    user = User(
        id=uuid.uuid4(),
        username=username,
        email=f"{username}@example.com",
        password_hash=get_password_hash("password123"),
        role=role
    )
    async_db_session.add(user)
    await async_db_session.commit()
    
    # Вход в систему и получение токена
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/token", data={
            "username": username,
            "password": "password123"
        })
        
        token = response.json()["access_token"]
    
    return user, token

# Тесты для API профилей обучения
@pytest.mark.asyncio
async def test_create_profile(async_db_session):
    """Тест создания профиля обучения."""
    user, token = await create_user_and_get_token(async_db_session)
    
    # Создание профиля
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/profiles", 
            json={
                "learning_style": {"visual": 0.7, "auditory": 0.3, "kinesthetic": 0.5},
                "cognitive_profile": {"attention_span": "medium", "memory_type": "visual"},
                "preferences": {"interests": ["programming", "music"]}
            },
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["user_id"] == str(user.id)
    assert data["learning_style"] == {"visual": 0.7, "auditory": 0.3, "kinesthetic": 0.5}
    
    # Проверка, что профиль сохранен в БД
    profile = await async_db_session.query(LearningProfile).filter(LearningProfile.user_id == user.id).first()
    assert profile is not None
    assert profile.learning_style == {"visual": 0.7, "auditory": 0.3, "kinesthetic": 0.5}

@pytest.mark.asyncio
async def test_get_profile(async_db_session):
    """Тест получения профиля обучения."""
    user, token = await create_user_and_get_token(async_db_session, "getprofileuser")
    
    # Создание профиля в БД
    profile = LearningProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        learning_style={"visual": 0.8, "auditory": 0.2, "kinesthetic": 0.4},
        cognitive_profile={"attention_span": "high"},
        preferences={"interests": ["math", "science"]}
    )
    async_db_session.add(profile)
    await async_db_session.commit()
    
    # Получение профиля через API
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/profiles/{user.id}", 
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["user_id"] == str(user.id)
    assert data["learning_style"] == {"visual": 0.8, "auditory": 0.2, "kinesthetic": 0.4}
    assert data["preferences"]["interests"] == ["math", "science"]

@pytest.mark.asyncio
async def test_update_profile(async_db_session):
    """Тест обновления профиля обучения."""
    user, token = await create_user_and_get_token(async_db_session, "updateprofileuser")
    
    # Создание профиля в БД
    profile = LearningProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        learning_style={"visual": 0.5, "auditory": 0.5, "kinesthetic": 0.5},
        cognitive_profile={},
        preferences={"interests": ["history"]}
    )
    async_db_session.add(profile)
    await async_db_session.commit()
    
    # Обновление профиля через API
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.patch(f"/api/profiles/{user.id}", 
            json={
                "learning_style": {"visual": 0.9},
                "preferences": {"interests": ["history", "art"]}
            },
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["learning_style"]["visual"] == 0.9
    assert data["learning_style"]["auditory"] == 0.5  # Сохранено из исходного профиля
    assert "art" in data["preferences"]["interests"]
    
    # Проверка обновления в БД
    updated_profile = await async_db_session.query(LearningProfile).filter(LearningProfile.user_id == user.id).first()
    assert updated_profile.learning_style["visual"] == 0.9
    assert "art" in updated_profile.preferences["interests"]
