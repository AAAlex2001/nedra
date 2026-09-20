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

Аккаунт один на email. `users.role` — активная роль, она переключается
через `POST /auth/role`. Роль эксперта доступна, только если у аккаунта есть
`ExpertProfile`; фронт узнаёт об этом из поля `is_expert`.

## Эксперты

Эксперт не регистрируется сам. Он подаёт заявку (`POST /experts/applications`,
multipart: поле `payload` с JSON и файлы `scans`), админ проверяет её и одобряет
(`POST /admin/experts/applications/{id}/approve`) — только тогда создаётся
пользователь с ролью `expert`, профиль и удостоверения. Хеш пароля хранится
в заявке и переносится в пользователя.

- `services/experts/catalog.py` — справочник Ростехнадзора: направления,
  области аттестации Э1…Э15, объекты экспертизы и какие объекты по какой
  области выдаются. Фронт получает его через `GET /experts/catalog`.
- `services/experts/validators.py` — проверка удостоверения по справочнику.
- `services/files/storage.py` — закрытое хранилище (`PRIVATE_DIR`): сканы
  лежат вне `media` и отдаются только через админскую ручку.

Эксперт с нерассмотренной заявкой при попытке входа получает 403 с понятным
текстом, а не «неверный пароль».

## Экспертиза: путь от заявки до приёмки

Статусы в `models/expertise.py`, по сценарию на каждый шаг в
`services/expertise/usecases/`:

| Статус | Кто действует | Ручка | Что происходит |
|---|---|---|---|
| `new` | заказчик | `POST /expertise` | документация загружена, цена зафиксирована из тарифа, эксперты по аттестации уведомлены |
| `expert_ready` | эксперт | `POST /expertise/{id}/accept` | первый готовый эксперт закрепляется за заявкой, заказчику уведомление и письмо |
| `contract` | заказчик | `POST /expertise/{id}/confirm` | вторая галочка — договор заключён |
| `in_progress` | заказчик | `POST /expertise/{id}/payment` | аванс 50 % через ЮKassa; статус двигает вебхук или `POST /expertise/{id}/payment/refresh` |
| `remarks` | эксперт | `POST /expertise/{id}/remarks` | multipart: `text`, `files` или и то и другое — рекомендации по приведению объекта в соответствие |
| `in_progress` | заказчик | `POST /expertise/{id}/revision` | исправленная документация, экспертиза возвращается в работу |
| `conclusion_ready` | эксперт | `POST /expertise/{id}/conclusion-ready` | заключение готово, заказчику письмо про полную оплату |
| `paid` | заказчик | `POST /expertise/{id}/payment` | остаток 50 % |
| `sent` | эксперт | `POST /expertise/{id}/conclusion` | multipart: `result` (positive/negative/remarks) и файлы заключения, подписанные ЭЦП |
| `accepted` | заказчик | `POST /expertise/{id}/accept-work` | работа принята |

Цикл замечаний повторяется сколько нужно: каждый раунд это строка в
`expertise_remarks` с текстом и файлами (`expertise_documents.remark_id`),
повторная подача закрывает его датой и возвращает статус `in_progress`.

Сумму этапов считает `services/expertise/money.py`: 50/50, копейка при
нечётной сумме уходит в остаток. `ApplyExpertisePaymentUseCase` идемпотентен:
повторное уведомление ЮKassa ничего не ломает. `PAYMENT_RETURN_URL` должен
вести в кабинет (`/kabinet`): фронт при загрузке сам проверяет
незавершённые платежи.

## Тарифы

Стоимость экспертизы задаёт админ по парам «область аттестации × объект
экспертизы» (`PUT /admin/tariffs`, пакет ячеек; `price: null` удаляет тариф).
Публичный список — `GET /tariffs`. Пары проверяются по справочнику экспертов.
Модуль экспертизы будет брать цену отсюда, эксперт свою цену не назначает.

## Платежи (ЮKassa)

`services/payments/gateway.py` — единственное место с HTTP к ЮKassa,
наружу отдаёт `GatewayPayment`, а не сырой JSON. Уведомлениям ЮKassa не верим:
берём из тела только id и запрашиваем платёж через API.

К каждому платежу прикладывается чек по 54-ФЗ: одна позиция «услуга»
на всю сумму, email плательщика из аккаунта. Ставка НДС в чеке —
`YOOKASSA_VAT_CODE` (по умолчанию 1, «без НДС»; 2 — 0 %, 3 — 10 %, 4 — 20 %).

Ручки: `POST /payments`, `GET /payments/{id}`, `POST /payments/{id}/refresh`,
`POST /payments/yookassa/webhook`. Переменные: `YOOKASSA_SHOP_ID`,
`YOOKASSA_SECRET_KEY`, `PAYMENT_RETURN_URL`, `YOOKASSA_VAT_CODE`. В кабинете ЮKassa указать адрес
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
