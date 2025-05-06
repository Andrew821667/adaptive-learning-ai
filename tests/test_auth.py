import pytest
from fastapi import status
from httpx import AsyncClient
import uuid

from app.main import app
from app.models.user import User
from app.services.auth_service import get_password_hash

# Тесты для API аутентификации
@pytest.mark.asyncio
async def test_create_user(async_db_session):
    """Тест создания пользователя."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/users", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "role": "student"
        })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "password" not in data
    
    # Проверка, что пользователь сохранен в БД
    user = await async_db_session.get(User, uuid.UUID(data["id"]))
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"

@pytest.mark.asyncio
async def test_login(async_db_session):
    """Тест входа в систему и получения токена."""
    # Создание тестового пользователя
    user = User(
        id=uuid.uuid4(),
        username="logintest",
        email="login@example.com",
        password_hash=get_password_hash("password123"),
        role="student"
    )
    async_db_session.add(user)
    await async_db_session.commit()
    
    # Попытка входа
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/token", data={
            "username": "logintest",
            "password": "password123"
        })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_get_current_user(async_db_session):
    """Тест получения информации о текущем пользователе."""
    # Создание тестового пользователя
    user = User(
        id=uuid.uuid4(),
        username="currentuser",
        email="current@example.com",
        password_hash=get_password_hash("password123"),
        role="student"
    )
    async_db_session.add(user)
    await async_db_session.commit()
    
    # Вход в систему и получение токена
    async with AsyncClient(app=app, base_url="http://test") as ac:
        login_response = await ac.post("/api/token", data={
            "username": "currentuser",
            "password": "password123"
        })
        
        token = login_response.json()["access_token"]
        
        # Использование токена для получения информации о пользователе
        response = await ac.get("/api/users/me", headers={
            "Authorization": f"Bearer {token}"
        })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "currentuser"
    assert data["email"] == "current@example.com"
