# Backend — архитектура

FastAPI + async SQLAlchemy 2.0 + PostgreSQL. Слои сверху, файл на сущность внутри.

```
backend/
├── app/
│   ├── main.py          сборка приложения, подключение роутеров
│   ├── config.py        единственная точка чтения окружения
│   ├── database.py      движок, фабрика сессий, get_session
│   ├── models/          SQLAlchemy — форма данных в БД
│   ├── schemas/         Pydantic — контракт API
│   ├── services/        бизнес-логика
│   └── routers/         HTTP-слой
├── alembic/             миграции
├── requirements.txt
└── Dockerfile
```

## Правило зависимостей

Зависимости идут в одну сторону, снаружи внутрь:

```
routers  →  services  →  models
   ↓                        ↓
schemas                 database
```

Обратных стрелок нет. Практически это значит:

- `models` не импортирует ничего из `schemas`, `services`, `routers`;
- `services` не импортирует `routers` и не знает слова HTTP;
- `routers` не трогает БД напрямую — только через `services`.

Если потянуло импортировать «вверх» — логика лежит не в том слое.

## Поток запроса

```
HTTP → router → схема Create (валидация входа)
              → service (логика + БД, здесь же commit)
              → ORM-модель
              → схема Read (что отдаём наружу) → HTTP
```

Схемы и модели разделены намеренно: колонку в БД можно переименовать,
не сломав контракт API, и наоборот.

## Как добавить сущность

Например, заявку на обучение. Четыре файла, по одному на слой:

1. `models/application.py` — таблица, наследник `Base`
2. `schemas/application.py` — `ApplicationCreate`, `ApplicationRead`
3. `services/application.py` — `create_application(session, payload)`
4. `routers/application.py` — `APIRouter`, ручки

Затем:

- импортировать модель в `models/__init__.py`, иначе Alembic её не увидит;
- подключить роутер в `main.py` через `include_router`;
- сгенерировать миграцию.

## Границы слоёв — что где не должно оказаться

| Слой | Нельзя |
|---|---|
| `models` | Pydantic, FastAPI, бизнес-правила |
| `schemas` | SQLAlchemy, запросы к БД |
| `services` | `HTTPException`, `Request`, `Response`, создание сессии |
| `routers` | запросы к БД, вычисления, работа с ORM |

Ошибки бизнес-уровня — свои исключения в `services`, роутер переводит их
в HTTP-коды. Так сервис можно вызвать из cron-задачи или CLI, где никакого
HTTP нет.

## Транзакции

Сессию создаёт `get_session` (одна на запрос), а `commit` делает сервис —
он единственный знает, где заканчивается бизнес-операция. Роутер за
транзакции не отвечает.

## Миграции

Alembic ещё не инициализирован:

```bash
cd backend
alembic init -t async alembic
```

Затем в `alembic/env.py` подставить `target_metadata = Base.metadata`
и брать URL из `app.config`. Дальше:

```bash
alembic revision --autogenerate -m "add applications"
alembic upgrade head
```

Автогенерация видит только те модели, что импортированы в
`models/__init__.py`.

## Запуск

Локально:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Документация — `/api/docs`, живость — `/api/health`.

В составе стека — `docker compose up -d --build` из корня репозитория.
