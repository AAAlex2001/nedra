# Backend — архитектура

FastAPI + async SQLAlchemy 2.0 + PostgreSQL. Слои сверху, домены внутри.

```
backend/
├── app/
│   ├── main.py            сборка приложения, подключение роутеров
│   ├── config.py          единственная точка чтения окружения
│   ├── database.py        движок, фабрика сессий, get_session
│   ├── models/            SQLAlchemy — форма данных в БД, файл на сущность
│   ├── schemas/           Pydantic — контракт API, файл на сущность
│   ├── services/          бизнес-логика, папка на домен
│   │   ├── articles/      repo, tags, stats, content, images, usecases/
│   │   ├── requests/      repo, catalog, letter, usecases/
│   │   ├── users/         repo, validators, usecases/
│   │   ├── payments/      repo, gateway (ЮKassa), usecases/
│   │   ├── mail/          send_email — единственное место с SMTP
│   │   └── security/      bcrypt для паролей, JWT для токенов
│   ├── dependencies/      зависимости роутеров, файл на домен
│   └── routers/           HTTP-слой, файл на ресурс
├── alembic/               миграции
├── tests/                 тесты сценариев без БД
├── requirements.txt
└── Dockerfile
```

Именование: `models` и `schemas` — в единственном числе (`article.py`, `user.py`),
`services`, `dependencies` и `routers` — во множественном (`articles/`, `users.py`).

## Правило зависимостей

Зависимости идут в одну сторону, снаружи внутрь:

```
routers  →  dependencies  →  services  →  models
   ↓                            ↓
schemas                     database
```

Обратных стрелок нет. Практически это значит:

- `models` не импортирует ничего из `schemas`, `services`, `routers`;
- `services` не импортирует `routers` и не знает слова HTTP;
- `routers` не трогает БД напрямую — только через репозитории и сценарии.

Если потянуло импортировать «вверх» — логика лежит не в том слое.

## Устройство домена

Каждая папка в `services/` устроена одинаково:

| Файл | Что внутри | Пример |
|---|---|---|
| `repo.py` | класс-репозиторий: только запросы к одной таблице, без бизнес-правил | `UserRepository.get_by_email` |
| `usecases/*.py` | по классу на действие; репозитории приходят в конструктор | `RegisterUserUseCase.execute` |
| `exceptions.py` | ошибки домена, наследники `LookupError` / `ValueError` / `Exception` | `EmailAlreadyTakenError` |
| остальное | чистые функции и внешние интеграции | `validators.py`, `gateway.py`, `letter.py` |

Простое чтение (список, получить по id) роутер делает через репозиторий.
Всё, где есть правила или несколько шагов, — через сценарий.

## Поток запроса

```
HTTP → router → схема In (валидация входа)
              → dependency (сессия, репозиторий, сценарий, текущий пользователь)
              → usecase (правила, несколько операций, commit внутри репозитория)
              → ORM-модель
              → схема Out (что отдаём наружу) → HTTP
```

Схемы и модели разделены намеренно: колонку в БД можно переименовать,
не сломав контракт API, и наоборот.

Ошибки бизнес-уровня — исключения в `services/<домен>/exceptions.py`,
роутер переводит их в HTTP-коды. Так сценарий можно вызвать из cron-задачи
или CLI, где никакого HTTP нет. «Не найдено» для объекта из пути
(`/articles/{slug}`) решается зависимостью, которая сама отдаёт 404.

## Как добавить домен

Например, экспертизу:

1. `models/expertise.py` — таблица, наследник `Base`, импорт в `models/__init__.py`;
2. `schemas/expertise.py` — схемы In и Out;
3. `services/expertise/` — `repo.py`, `exceptions.py`, `usecases/`;
4. `dependencies/expertise.py` — фабрики репозитория и сценариев;
5. `routers/expertise.py` — ручки, `include_router` в `main.py`;
6. миграция в `alembic/versions/` с номером следующим по порядку;
7. `tests/test_expertise.py` — сценарии с фейковым репозиторием.

## Пользователи и вход

Пароли хешируются bcrypt (`services/security/passwords.py`), токен доступа —
JWT в httponly-cookie `access_token` (`services/security/tokens.py`).
Текущий пользователь и проверка роли — в `dependencies/users.py`:
`get_current_user`, `require_customer`, `require_expert`.

Нужна переменная окружения `JWT_SECRET` длиной не меньше 32 символов.

## Платежи (ЮKassa)

`services/payments/gateway.py` — единственное место с HTTP к ЮKassa,
наружу отдаёт `GatewayPayment`, а не сырой JSON. Уведомлениям ЮKassa не верим:
берём из тела только id и запрашиваем платёж через API.

Ручки: `POST /payments`, `GET /payments/{id}`, `POST /payments/{id}/refresh`,
`POST /payments/yookassa/webhook`. Переменные: `YOOKASSA_SHOP_ID`,
`YOOKASSA_SECRET_KEY`, `PAYMENT_RETURN_URL`. В кабинете ЮKassa указать адрес
уведомлений `https://nedra-npi.ru/api/v1/payments/yookassa/webhook`
и включить события `payment.succeeded` и `payment.canceled`.

## Транзакции

Сессию создаёт `get_session` (одна на запрос), а `commit` делает репозиторий
в методах `add`, `save`, `delete` — он единственный знает, где заканчивается
операция с базой. Роутер за транзакции не отвечает.

## Миграции

```bash
cd backend
alembic revision --autogenerate -m "add expertise"
alembic upgrade head
```

Автогенерация видит только те модели, что импортированы в
`models/__init__.py`. На проде миграции выполняются при старте контейнера.

## Запуск

Локально:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Тесты: `pytest tests`. Линтер: `ruff check app tests`.

Документация — `/api/docs`, живость — `/api/health`.

В составе стека — `docker compose up -d --build` из корня репозитория.
