# API ИИ-ассистента адаптивного обучения

## Аутентификация

### Получение токена доступа

```
POST /api/token
```

**Тело запроса:**
```json
{
  "username": "user123",
  "password": "password123"
}
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Создание пользователя

```
POST /api/users
```

**Тело запроса:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "role": "student"
}
```

**Ответ:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "newuser",
  "email": "user@example.com",
  "role": "student",
  "created_at": "2023-10-25T12:34:56.789Z"
}
```

## Профили обучения

### Создание профиля обучения

```
POST /api/profiles
```

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Тело запроса:**
```json
{
  "learning_style": {
    "visual": 0.7,
    "auditory": 0.3,
    "kinesthetic": 0.5
  },
  "cognitive_profile": {
    "attention_span": "medium",
    "memory_type": "visual"
  },
  "preferences": {
    "interests": ["programming", "music"]
  }
}
```

**Ответ:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "learning_style": {
    "visual": 0.7,
    "auditory": 0.3,
    "kinesthetic": 0.5
  },
  "cognitive_profile": {
    "attention_span": "medium",
    "memory_type": "visual"
  },
  "preferences": {
    "interests": ["programming", "music"]
  },
  "created_at": "2023-10-25T12:35:00.000Z",
  "updated_at": "2023-10-25T12:35:00.000Z"
}
```

### Получение профиля обучения

```
GET /api/profiles/{user_id}
```

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Ответ:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "learning_style": {
    "visual": 0.7,
    "auditory": 0.3,
    "kinesthetic": 0.5
  },
  "cognitive_profile": {
    "attention_span": "medium",
    "memory_type": "visual"
  },
  "preferences": {
    "interests": ["programming", "music"]
  },
  "created_at": "2023-10-25T12:35:00.000Z",
  "updated_at": "2023-10-25T12:35:00.000Z"
}
```

### Обновление профиля обучения

```
PATCH /api/profiles/{user_id}
```

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Тело запроса:**
```json
{
  "learning_style": {
    "visual": 0.8
  },
  "preferences": {
    "interests": ["programming", "music", "art"]
  }
}
```

**Ответ:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "learning_style": {
    "visual": 0.8,
    "auditory": 0.3,
    "kinesthetic": 0.5
  },
  "cognitive_profile": {
    "attention_span": "medium",
    "memory_type": "visual"
  },
  "preferences": {
    "interests": ["programming", "music", "art"]
  },
  "created_at": "2023-10-25T12:35:00.000Z",
  "updated_at": "2023-10-25T12:36:00.000Z"
}
```

## Концепции и контент

### Создание концепции

```
POST /api/concepts
```

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Тело запроса:**
```json
{
  "name": "Переменные в Python",
  "description": "Переменные в Python - это именованные ссылки на объекты в памяти.",
  "domain": "programming",
  "difficulty": 0.3,
  "taxonomy_tags": {
    "bloom": ["remember", "understand"],
    "solo": ["unistructural", "multistructural"]
  }
}
```

**Ответ:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "name": "Переменные в Python",
  "description": "Переменные в Python - это именованные ссылки на объекты в памяти.",
  "domain": "programming",
  "difficulty": 0.3,
  "taxonomy_tags": {
    "bloom": ["remember", "understand"],
    "solo": ["unistructural", "multistructural"]
  },
  "created_at": "2023-10-25T12:40:00.000Z"
}
```

### Получение списка концепций

```
GET /api/concepts?domain=programming&skip=0&limit=10
```

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Ответ:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "name": "Переменные в Python",
    "description": "Переменные в Python - это именованные ссылки на объекты в памяти.",
    "domain": "programming",
    "difficulty": 0.3,
    "taxonomy_tags": {
      "bloom": ["remember", "understand"],
      "solo": ["unistructural", "multistructural"]
    },
    "created_at": "2023-10-25T12:40:00.000Z"
  }
]
```

### Создание образовательного контента

```
POST /api/content
```

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Тело запроса:**
```json
{
  "title": "Введение в переменные Python",
  "content_type": "text",
  "body": "# Введение в переменные Python\n\nПеременные в Python служат для хранения данных...",
  "difficulty": 0.3,
  "concepts": ["550e8400-e29b-41d4-a716-446655440002"],
  "metadata": {
    "author": "John Doe",
    "source": "internal"
  }
}
```

**Ответ:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "title": "Введение в переменные Python",
  "content_type": "text",
  "body": "# Введение в переменные Python\n\nПеременные в Python служат для хранения данных...",
  "difficulty": 0.3,
  "concepts": ["550e8400-e29b-41d4-a716-446655440002"],
  "metadata": {
    "author": "John Doe",
    "source": "internal"
  },
  "created_at": "2023-10-25T12:45:00.000Z",
  "updated_at": "2023-10-25T12:45:00.000Z"
}
```

### Адаптация контента

```
POST /api/content/adapt
```

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Тело запроса:**
```json
{
  "content_id": "550e8400-e29b-41d4-a716-446655440003",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "adaptation_params": {
    "target_difficulty": 0.4,
    "preferred_learning_style": "visual"
  }
}
```

**Ответ:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "title": "Введение в переменные Python",
  "content_type": "text",
  "body": "# Введение в переменные Python\n\nПредставьте переменные как контейнеры, в которых хранятся данные...",
  "difficulty": 0.4,
  "concepts": ["550e8400-e29b-41d4-a716-446655440002"],
  "metadata": {
    "author": "John Doe",
    "source": "internal",
    "adaptation": {
      "original_content_id": "550e8400-e29b-41d4-a716-446655440003",
      "adapted_for_user": "550e8400-e29b-41d4-a716-446655440000",
      "adaptation_params": {
        "target_difficulty": 0.4,
        "preferred_learning_style": "visual"
      }
    }
  },
  "created_at": "2023-10-25T12:47:00.000Z",
  "updated_at": "2023-10-25T12:47:00.000Z"
}
```

## Оценка и диагностика

### Создание оценки

```
POST /api/assessments
```

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Тело запроса:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "concept_ids": ["550e8400-e29b-41d4-a716-446655440002"],
  "difficulty_level": 0.5,
  "assessment_type": "adaptive",
  "max_questions": 5
}
```

**Ответ:**
```json
{
  "assessment_id": "550e8400-e29b-41d4-a716-446655440005",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "questions": [
    {
      "question_id": "550e8400-e29b-41d4-a716-446655440006",
      "concept_id": "550e8400-e29b-41d4-a716-446655440002",
      "text": "Как объявить переменную в Python?",
      "options": [
        {"id": "a", "text": "var x = 10;"},
        {"id": "b", "text": "x = 10"},
        {"id": "c", "text": "int x = 10;"},
        {"id": "d", "text": "let x = 10;"}
      ],
      "difficulty": 0.5
    }
  ],
  "concept_ids": ["550e8400-e29b-41d4-a716-446655440002"],
  "created_at": "2023-10-25T12:50:00.000Z",
  "metadata": {
    "difficulty_level": 0.5,
    "max_questions": 5
  }
}
```

### Отправка ответов на оценку

```
POST /api/assessments/{assessment_id}/submit
```

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Тело запроса:**
```json
{
  "responses": [
    {
      "question_id": "550e8400-e29b-41d4-a716-446655440006",
      "answer": "b",
      "response_time_seconds": 15
    }
  ]
}
```

**Ответ:**
```json
{
  "result_id": "550e8400-e29b-41d4-a716-446655440007",
  "assessment_id": "550e8400-e29b-41d4-a716-446655440005",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "concept_results": {
    "550e8400-e29b-41d4-a716-446655440002": {
      "score": 1.0,
      "questions_count": 1,
      "correct_count": 1
    }
  },
  "total_score": 1.0,
  "feedback": {
    "overall_feedback": "Отличная работа! Вы правильно ответили на все вопросы.",
    "concept_feedback": {
      "550e8400-e29b-41d4-a716-446655440002": "Вы показали хорошее понимание концепции переменных в Python."
    }
  },
  "created_at": "2023-10-25T12:52:00.000Z"
}
```

## Планы обучения

### Создание плана обучения

```
POST /api/learning/plan
```

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Тело запроса:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "concept_ids": [
    "550e8400-e29b-41d4-a716-446655440002",
    "550e8400-e29b-41d4-a716-446655440008"
  ],
  "plan_params": {
    "target_difficulty_curve": "gradual",
    "spaced_repetition": true
  }
}
```

**Ответ:**
```json
{
  "plan_id": "550e8400-e29b-41d4-a716-446655440009",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-10-25T13:00:00.000Z",
  "concepts": [
    "550e8400-e29b-41d4-a716-446655440002",
    "550e8400-e29b-41d4-a716-446655440008"
  ],
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440010",
      "concepts": [
        {
          "concept_id": "550e8400-e29b-41d4-a716-446655440002",
          "name": "Переменные в Python",
          "difficulty": 0.3,
          "current_mastery": 0.8
        }
      ],
      "estimated_duration_minutes": 30,
      "activities": [
        {
          "activity_id": "550e8400-e29b-41d4-a716-446655440011",
          "activity_type": "learn",
          "concept_id": "550e8400-e29b-41d4-a716-446655440002",
          "difficulty": 0.5,
          "duration_minutes": 15
        },
        {
          "activity_id": "550e8400-e29b-41d4-a716-446655440012",
          "activity_type": "assess",
          "concept_id": "550e8400-e29b-41d4-a716-446655440002",
          "difficulty": 0.5,
          "duration_minutes": 10
        }
      ]
    }
  ],
  "metadata": {
    "target_difficulty_curve": "gradual",
    "spaced_repetition": true,
    "total_concepts": 2,
    "total_sessions": 1,
    "estimated_total_duration_minutes": 30
  }
}
```

## Чат-интерфейс

### Отправка сообщения

```
POST /api/chat/message
```

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Тело запроса:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Расскажи подробнее о переменных в Python",
  "session_id": "550e8400-e29b-41d4-a716-446655440013",
  "context": {
    "previous_topic": "programming"
  }
}
```

**Ответ:**
```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440014",
  "role": "assistant",
  "content": "Переменные в Python - это способ хранения данных...",
  "session_id": "550e8400-e29b-41d4-a716-446655440013",
  "timestamp": "2023-10-25T13:05:00.000Z",
  "metadata": {
    "concepts_referenced": ["550e8400-e29b-41d4-a716-446655440002"],
    "adaptive_context": true
  }
}
```

### Получение истории чата

```
GET /api/chat/history/{session_id}
```

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Ответ:**
```json
[
  {
    "message_id": "550e8400-e29b-41d4-a716-446655440015",
    "role": "user",
    "content": "Расскажи про Python",
    "session_id": "550e8400-e29b-41d4-a716-446655440013",
    "timestamp": "2023-10-25T13:00:00.000Z",
    "metadata": {}
  },
  {
    "message_id": "550e8400-e29b-41d4-a716-446655440016",
    "role": "assistant",
    "content": "Python - это высокоуровневый язык программирования...",
    "session_id": "550e8400-e29b-41d4-a716-446655440013",
    "timestamp": "2023-10-25T13:00:10.000Z",
    "metadata": {
      "concepts_referenced": ["550e8400-e29b-41d4-a716-446655440017"],
      "adaptive_context": true
    }
  },
  {
    "message_id": "550e8400-e29b-41d4-a716-446655440014",
    "role": "user",
    "content": "Расскажи подробнее о переменных в Python",
    "session_id": "550e8400-e29b-41d4-a716-446655440013",
    "timestamp": "2023-10-25T13:05:00.000Z",
    "metadata": {}
  },
  {
    "message_id": "550e8400-e29b-41d4-a716-446655440015",
    "role": "assistant",
    "content": "Переменные в Python - это способ хранения данных...",
    "session_id": "550e8400-e29b-41d4-a716-446655440013",
    "timestamp": "2023-10-25T13:05:10.000Z",
    "metadata": {
      "concepts_referenced": ["550e8400-e29b-41d4-a716-446655440002"],
      "adaptive_context": true
    }
  }
]
```

## Аналитика обучения

### Получение прогресса обучения

```
GET /api/learning/progress/{user_id}?time_range=month
```

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Ответ:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "time_range": "month",
  "progress_over_time": [
    {
      "date": "2023-10-01",
      "overallProgress": 0.2,
      "masteryLevel": 0.15,
      "engagementScore": 0.3
    },
    {
      "date": "2023-10-25",
      "overallProgress": 0.5,
      "masteryLevel": 0.45,
      "engagementScore": 0.7
    }
  ],
  "concept_progress": [
    {
      "name": "Переменные в Python",
      "start": 0.1,
      "current": 0.8,
      "target": 0.9
    },
    {
      "name": "Функции в Python",
      "start": 0.0,
      "current": 0.3,
      "target": 0.8
    }
  ],
  "insights": [
    {
      "type": "improvement",
      "text": "Ваше понимание переменных в Python улучшилось на 70% за этот месяц.",
      "concept": "Переменные в Python"
    },
    {
      "type": "recommendation",
      "text": "Рекомендуем больше практиковаться в создании функций в Python.",
      "concept": "Функции в Python"
    }
  ]
}
```

### Получение рекомендаций

```
GET /api/recommendations/{user_id}
```

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Ответ:**
```json
[
  {
    "type": "concept",
    "concept_id": "550e8400-e29b-41d4-a716-446655440008",
    "name": "Функции в Python",
    "difficulty": 0.5,
    "relevance_to_goals": 0.9,
    "reason": "Это логическое продолжение изучения переменных в Python"
  },
  {
    "type": "content",
    "content_id": "550e8400-e29b-41d4-a716-446655440018",
    "title": "Практические примеры использования переменных",
    "difficulty": 0.4,
    "relevance_to_goals": 0.8,
    "reason": "Поможет закрепить знания о переменных через практику"
  }
]
```
