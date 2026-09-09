"""Часть V. Движок, сессии, async и FastAPI: главы 37–39."""


def mono(text):
    return f"<font name='Mono' size='9'>{text}</font>"


def build(P, B, C, note, table, Spacer, PageBreak, mm, CODE_BG, GOOD_BG):
    S = []
    A = S.append
    m = mono

    A(P("Часть V. Движок, сессии и FastAPI", "part"))
    A(P("Модели описывают таблицы, запросы описывают, что достать. Осталось понять, как всё "
        "это физически доезжает до PostgreSQL и обратно: кто открывает соединение, кто держит "
        "транзакцию, почему у нас всё асинхронное и где именно SQLAlchemy встречается с "
        "FastAPI."))

    # ---------- 37 ----------
    A(P("37. Engine: соединения, пул и async", "h1"))
    A(P("Engine — точка входа SQLAlchemy в базу. Он хранит URL, знает диалект и драйвер и "
        "управляет пулом соединений. Создаётся один раз на всё приложение."))
    A(C("""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=settings.debug)

SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session():
    \"\"\"Сессия на один HTTP-запрос: открыть, отдать роутеру, закрыть.\"\"\"

    async with SessionLocal() as session:
        yield session
""", "backend/app/database.py"))
    A(P("Что откуда импортируем", "h2"))
    A(table([
        ["Имя", "Модуль", "Зачем"],
        ["create_async_engine", "sqlalchemy.ext.asyncio", "создать движок под асинхронный драйвер asyncpg"],
        ["AsyncSession", "sqlalchemy.ext.asyncio", "класс сессии с await у execute, commit, refresh"],
        ["async_sessionmaker", "sqlalchemy.ext.asyncio", "фабрика сессий с общими настройками"],
        ["create_engine, Session, sessionmaker", "sqlalchemy, sqlalchemy.orm", "то же для синхронного кода; в проекте не используются"],
    ], [42 * mm, 40 * mm, 83 * mm]))
    A(P("Пул соединений", "h2"))
    A(P("Открыть TCP-соединение с PostgreSQL и пройти аутентификацию — дорого, десятки "
        "миллисекунд. Поэтому движок держит пул: несколько открытых соединений, которые "
        "сессии берут на время запроса и возвращают. По умолчанию пять постоянных плюс до "
        "десяти временных. Для сайта с десятками запросов в секунду этого хватает; если "
        "увидите ошибку " + m("QueuePool limit ... reached") + ", значит, соединения не "
        "возвращаются: где-то сессия не закрывается или транзакция висит."))
    A(C("""
engine = create_async_engine(
    settings.database_url,
    pool_size=5,          # постоянных соединений
    max_overflow=10,      # временных сверх pool_size под пиковую нагрузку
    pool_pre_ping=True,   # перед выдачей проверить, живо ли соединение
    pool_recycle=1800,    # пересоздавать соединения старше 30 минут
    echo=False,           # печатать весь SQL в лог: включать только при отладке
)
""", "Настройки пула, которые имеет смысл знать"))
    A(P(m("pool_pre_ping") + " спасает от ситуации «база перезапустилась, а в пуле лежат "
        "мёртвые соединения»: перед выдачей движок отправляет " + m("SELECT 1") + " и при "
        "ошибке открывает новое. После " + m("docker compose restart db") + " без этого флага "
        "первые запросы бэкенда упадут."))
    A(P("Синхронно или асинхронно", "h2"))
    A(P("FastAPI построен на asyncio: один процесс обслуживает много запросов, переключаясь "
        "между ними в точках " + m("await") + ". Если внутри такого процесса вызвать "
        "блокирующий драйвер psycopg2, весь процесс встанет и будет ждать ответа базы, другие "
        "запросы замрут. Асинхронный драйвер asyncpg отдаёт управление на время ожидания. "
        "Поэтому в проекте всё асинхронное: " + m("create_async_engine") + ", "
        + m("AsyncSession") + ", " + m("await db.execute(...)") + ", и роутеры объявлены как "
        + m("async def") + "."))
    A(P("Цена асинхронности — одна: ленивая подгрузка не работает. Когда вы обращаетесь к "
        + m("article.tags") + ", а теги ещё не загружены, синхронный SQLAlchemy тихо сделает "
        "запрос. Асинхронный не может: обращение к атрибуту — не " + m("await") + ", и "
        "выполнить запрос негде. Отсюда ошибка " + m("MissingGreenlet") + " и наши правила: "
        + m("lazy='selectin'") + " у связей, которые нужны всегда, и явная перечитка объекта "
        "после commit. Подробно — в главе 27, здесь важно понять причину."))
    A(P("echo и логи SQL", "h2"))
    A(P(m("echo=True") + " печатает каждый SQL-запрос с параметрами. Это лучший способ "
        "увидеть, что на самом деле генерирует ORM, поймать N+1 и лишние запросы. Включайте "
        "локально через " + m("DEBUG=true") + ", на проде держите выключенным: лог раздувается "
        "мгновенно."))

    # ---------- 38 ----------
    A(P("38. Сессия: жизненный цикл, identity map, expire_on_commit", "h1"))
    A(P("Сессия — рабочее пространство одной единицы работы. Она берёт соединение из пула, "
        "открывает транзакцию, следит за объектами, которые вы через неё загрузили или "
        "добавили, и в нужный момент отправляет изменения в базу."))
    A(P("Жизненный цикл в одном запросе", "h2"))
    A(C("""
async with SessionLocal() as db:          # 1. сессия создана, соединения пока нет
    article = await db.get(Article, 42)   # 2. первый запрос: взяли соединение, BEGIN
    article.title = "Новый заголовок"     # 3. объект «грязный», в базу ещё ничего не ушло
    tag = Tag(slug="eko", title="Эко")
    db.add(tag)                           # 4. объект «ожидающий», INSERT ещё не отправлен
    await db.flush()                      # 5. UPDATE и INSERT ушли в базу, транзакция открыта
    print(tag.id)                         # 6. id уже есть благодаря RETURNING
    await db.commit()                     # 7. COMMIT: изменения видны всем
                                          # 8. выход из with: соединение вернулось в пул
""", "Что происходит на каждом шаге"))
    A(P("Unit of Work: сессия копит изменения", "h2"))
    A(P("Вы меняете атрибуты объектов как обычные поля Python, а сессия запоминает, что "
        "изменилось. При flush она сама сортирует операции в правильном порядке: сначала "
        "вставить родителя, потом детей с внешним ключом на него, обновления сгруппировать. "
        "Это паттерн Unit of Work. Поэтому в сервисе статей нет ни одного явного UPDATE для "
        "полей: " + m("article.title = changes['title']") + " и потом один " + m("commit") + "."))
    A(P("flush против commit", "h2"))
    A(B(m("flush") + " отправляет накопленные INSERT/UPDATE/DELETE в базу, но транзакцию не "
        "закрывает. Нужен, когда хотите получить " + m("id") + " до commit или поймать "
        + m("IntegrityError") + " в конкретном месте, как мы делаем при регистрации просмотра."))
    A(B(m("commit") + " делает flush и затем COMMIT. После него транзакция закрыта, следующая "
        "операция откроет новую."))
    A(B(m("rollback") + " откатывает транзакцию и сбрасывает состояние объектов к тому, что "
        "было. После IntegrityError сессия непригодна, пока не сделать rollback."))
    A(P("Identity map: один объект на одну строку", "h2"))
    A(P("Сессия хранит словарь «первичный ключ → объект». Если вы дважды запросите статью с "
        "id 42 в одной сессии, получите один и тот же объект Python, а не две копии. Это "
        "удобно: изменения не расходятся. Но это же — причина ловушки, которую мы поймали."))
    A(C("""
article = await db.get(Article, article_id)
article.title = "..."
await db.commit()
again = await db.get(Article, article_id)   # тот же объект из identity map, запроса в базу нет
print(again.updated_at)                      # MissingGreenlet: атрибут протух после commit
""", "Почему db.get после commit не помог"))
    A(P("После commit SQLAlchemy помечает колонки с " + m("onupdate") + " и "
        + m("server_default") + " как устаревшие: их значения вычислила база, Python их не "
        "знает. Обращение к такому атрибуту требует запроса, а в async это невозможно. "
        + m("db.get") + " вернул тот же объект из identity map, не ходя в базу. Решение — "
        "заставить сессию перечитать строку и перезаписать объект:"))
    A(C("""
async def reload(self, article_id: int) -> Article:
    \"\"\"Перечитать статью из базы после записи.\"\"\"

    stmt = (
        select(Article)
        .where(Article.id == article_id)
        .execution_options(populate_existing=True)
    )

    result = await self.db.execute(stmt)

    return result.scalar_one()
""", "populate_existing: обновить объект в identity map данными из базы"))
    A(P("Альтернатива — " + m("await db.refresh(article)") + ": перечитывает один объект. Мы "
        "выбрали " + m("populate_existing") + ", потому что он заодно подгружает теги через "
        "selectin, а " + m("refresh") + " связи по умолчанию не трогает."))
    A(P("expire_on_commit", "h2"))
    A(P("По умолчанию после commit сессия помечает <b>все</b> атрибуты всех объектов "
        "устаревшими, и любое обращение к ним требует запроса. В синхронном коде это просто "
        "лишние запросы, в async — ошибка. Поэтому у нас " + m("expire_on_commit=False")
        + ": объекты после commit остаются читаемыми. Обратная сторона — колонки, вычисленные "
        "базой, надо перечитывать явно, что мы и делаем в " + m("reload") + "."))
    A(P("Сессия на запрос: зависимость FastAPI", "h2"))
    A(C("""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.services.articles import ArticleService


def get_article_service(
    session: AsyncSession = Depends(get_session),
) -> ArticleService:
    \"\"\"Сервис статей с сессией текущего запроса.\"\"\"

    return ArticleService(session)


@router.get("/articles/{slug}")
async def get_article(
    slug: str,
    service: ArticleService = Depends(get_article_service),
) -> ArticleSchema:
    article = await service.get_published(slug)

    return ArticleSchema.model_validate(article)
""", "Цепочка зависимостей: get_session → сервис → роутер"))
    A(P("FastAPI вызывает " + m("get_session") + " в начале запроса, доходит до " + m("yield")
        + " и отдаёт сессию дальше по цепочке. Когда ответ отправлен, выполнение продолжается "
        "после " + m("yield") + ": блок " + m("async with") + " закрывается, соединение "
        "возвращается в пул. Если внутри было исключение, сессия откатится. Так каждая заявка "
        "получает свою транзакцию, а роутер не знает ничего о движке."))
    A(P("Почему сервис, а не запросы в роутере", "h2"))
    A(P("Роутер отвечает за HTTP: разобрать параметры, вернуть код ответа, превратить "
        "доменную ошибку в 404 или 422. Сервис отвечает за данные: запросы, транзакции, "
        "правила («черновик считается ненайденным»). Разделение даёт две вещи: сервис можно "
        "вызвать из скрипта или теста без HTTP, а роутер читается как описание API. Сервис "
        "получает сессию снаружи и коммитит сам — так одна сессия проходит через все его "
        "методы в рамках запроса."))

    # ---------- 39 ----------
    A(P("39. Карта импортов: что откуда и почему", "h1"))
    A(P("SQLAlchemy разложен на подпакеты по смыслу. Когда понимаешь логику, перестаёшь "
        "гуглить каждый импорт."))
    A(table([
        ["Откуда", "Что", "Смысл"],
        ["sqlalchemy", "select, insert, update, delete, func, and_, or_, not_, exists, case, cast, text", "конструкторы SQL-выражений, ядро (Core)"],
        ["sqlalchemy", "Integer, String, Text, Boolean, DateTime, Date, Numeric, JSON, Enum, SmallInteger", "типы колонок, общие для всех баз"],
        ["sqlalchemy", "Table, Column, ForeignKey, MetaData, CheckConstraint, UniqueConstraint, Index", "описание схемы на уровне таблиц"],
        ["sqlalchemy.orm", "DeclarativeBase, Mapped, mapped_column, relationship, selectinload, joinedload", "ORM: классы-модели и связи"],
        ["sqlalchemy.ext.asyncio", "create_async_engine, AsyncSession, async_sessionmaker", "асинхронный движок и сессии"],
        ["sqlalchemy.exc", "IntegrityError, NoResultFound, MultipleResultsFound, SQLAlchemyError", "исключения"],
        ["sqlalchemy.dialects.postgresql", "JSONB, UUID, ARRAY, insert (с on_conflict)", "то, что есть только в PostgreSQL"],
        ["alembic", "op, context", "команды миграций и доступ к конфигу"],
    ], [42 * mm, 70 * mm, 53 * mm]))
    A(P("Разбор импортов нашей модели", "h2"))
    A(C("""
from datetime import datetime                      # аннотации Mapped[datetime]

from sqlalchemy import (
    JSON,              # тип JSON, общий для всех баз (для SQLite в тестах)
    CheckConstraint,   # CHECK (value IN (-1, 1))
    Column,            # колонка в Table без класса-модели: article_tags
    DateTime,          # timestamp; с timezone=True — timestamptz
    ForeignKey,        # внешний ключ
    Integer,           # int4
    SmallInteger,      # int2 — для value реакции хватит
    String,            # varchar(n)
    Table,             # таблица без модели — промежуточная для M:N
    Text,              # text без ограничения длины
    func,              # генератор SQL-функций: func.now(), func.count()
)
from sqlalchemy.dialects.postgresql import JSONB   # настоящий JSONB для прода
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base                   # общий DeclarativeBase проекта
""", "backend/app/models/articles.py, шапка"))
    A(B(m("JSON().with_variant(JSONB, 'postgresql')") + " — «по умолчанию JSON, а на PostgreSQL "
        "JSONB». Так одна модель работает и в тестах на SQLite, и на проде."))
    A(B(m("func") + " — не функция, а объект-генератор: любой атрибут превращается в вызов "
        "SQL-функции с тем же именем. " + m("func.now()") + " даст " + m("now()") + ", "
        + m("func.random()") + " — " + m("random()") + ", " + m("func.count()") + " — "
        + m("count(*)") + ". Он ничего не проверяет: опечатка уедет в базу и упадёт там."))
    A(B(m("Base") + " импортируется из одного места. У всех моделей общий "
        + m("Base.metadata") + ", иначе Alembic увидит только часть таблиц."))
    A(P("Разбор импортов сервиса", "h2"))
    A(C("""
from dataclasses import dataclass                        # ArticleStats — простой контейнер

from sqlalchemy import and_, func, select, update        # выражения и команды
from sqlalchemy.exc import IntegrityError                # ловим гонку на уникальном ключе
from sqlalchemy.ext.asyncio import AsyncSession          # тип для аннотации self.db

from app.models.articles import Article, ArticleReaction, ArticleView, Tag, article_tags
from app.schemas.articles import ArticleCreateSchema, ArticleUpdateSchema
from app.services.content import make_slug, prepare_content
from app.services.exceptions import ArticleNotFoundError, TagNotFoundError
""", "backend/app/services/articles.py, шапка"))
    A(P("Заметьте, что сервис не импортирует ничего из FastAPI. Он не знает про HTTP, "
        "Depends и статусы ответов. Доменные ошибки — свои классы в "
        + m("services/exceptions.py") + ", и уже роутер переводит " + m("ArticleNotFoundError")
        + " в 404. Так сервис можно вызвать из скрипта загрузки статей или из теста."))
    A(P("Разбор импортов роутера", "h2"))
    A(C("""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_article_service, get_visitor_id
from app.schemas.articles import ArticleCardSchema, ArticleListSchema, ArticleSchema, Section
from app.services.articles import ArticleService
from app.services.exceptions import ArticleNotFoundError
""", "backend/app/routers/articles.py, шапка"))
    A(P("Роутер, наоборот, не импортирует ни моделей, ни select. Он работает со схемами "
        "Pydantic на входе и выходе и с сервисом посередине. Направление зависимостей всегда "
        "одно: роутеры → сервисы → модели. Модели не знают о сервисах, сервисы не знают о "
        "роутерах."))

    A(PageBreak())
    return S
