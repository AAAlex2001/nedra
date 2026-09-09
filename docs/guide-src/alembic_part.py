"""Часть VI. Миграции Alembic и тестирование: главы 40–45."""


def mono(text):
    return f"<font name='Mono' size='9'>{text}</font>"


def build(P, B, C, note, table, Spacer, PageBreak, mm, CODE_BG, GOOD_BG):
    S = []
    A = S.append
    m = mono

    A(P("Часть VI. Миграции Alembic", "part"))
    A(P("Модель описывает, какой таблица должна быть. Но база уже существует, в ней данные, и "
        "просто пересоздать таблицу нельзя. Миграция — это скрипт, который переводит базу из "
        "одного состояния схемы в другое, не теряя данных. Alembic — инструмент, который эти "
        "скрипты хранит, упорядочивает и применяет."))

    # ---------- 40 ----------
    A(P("40. Зачем миграции и как Alembic устроен", "h1"))
    A(P("Без миграций есть два пути, и оба плохие. " + m("Base.metadata.create_all()")
        + " создаёт только отсутствующие таблицы и никогда не меняет существующие: добавили "
        "колонку в модель — в базе её не появится. Ручной " + m("ALTER TABLE") + " в psql "
        "работает, но его нужно повторить на каждом окружении, помнить порядок и уметь "
        "откатить. Миграции решают обе проблемы: изменение схемы — это файл в репозитории, "
        "который применяется автоматически и одинаково везде."))
    A(P("Как Alembic понимает, что уже применено", "h2"))
    A(P("В базе есть служебная таблица " + m("alembic_version") + " с одной строкой — "
        "идентификатором последней применённой ревизии. Каждый файл миграции знает свой "
        + m("revision") + " и " + m("down_revision") + " (предыдущую). Из них складывается "
        "цепочка. Команда " + m("alembic upgrade head") + " смотрит, где база сейчас, и "
        "применяет все ревизии от неё до конца цепочки."))
    A(C("""
0001_create_requests  →  0002_create_articles  →  0003_add_article_seo  →  0004_add_article_section
      (заявки)              (статьи, теги,           (seo_title,             (колонка section
                             просмотры, реакции)      seo_description,        + индекс)
                                                      seo_keywords)

alembic_version на проде после деплоя:  0004
""", "Цепочка миграций проекта"))
    A(P("Структура каталога", "h2"))
    A(C("""
backend/
├── alembic.ini              # где лежат миграции, формат имён файлов
├── alembic/
│   ├── env.py               # как подключиться к базе и откуда взять metadata
│   ├── script.py.mako       # шаблон нового файла миграции
│   └── versions/
│       ├── 0001_create_requests.py
│       ├── 0002_create_articles.py
│       ├── 0003_add_article_seo.py
│       └── 0004_add_article_section.py
└── app/
    └── models/              # то, с чем Alembic сравнивает базу
""", "Файлы Alembic в проекте"))

    # ---------- 41 ----------
    A(P("41. Настройка: alembic.ini и env.py", "h1"))
    A(P(m("alembic.ini") + " хранит настройки самого инструмента. Из важного: путь к каталогу "
        "миграций и шаблон имени файла. URL базы мы туда не пишем, чтобы пароль не лежал в "
        "репозитории, а берём из переменных окружения в " + m("env.py") + "."))
    A(C("""
[alembic]
script_location = alembic
file_template = %%(rev)s_%%(slug)s
prepend_sys_path = .
""", "alembic.ini"))
    A(P(m("env.py") + " — Python-файл, который Alembic выполняет при каждой команде. Его задача: "
        "создать подключение и сказать, с какими моделями сравнивать базу. У нас движок "
        "асинхронный, поэтому " + m("env.py") + " чуть сложнее стандартного."))
    A(C("""
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import get_settings
from app.models import Base

config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    \"\"\"Сгенерировать SQL в стандартный вывод, не подключаясь к базе.\"\"\"

    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    \"\"\"Выполнить миграции на уже открытом соединении.\"\"\"

    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    \"\"\"Подключиться асинхронным движком и выполнить миграции.\"\"\"

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
""", "alembic/env.py для асинхронного движка"))
    A(P("Ключевые места:"))
    A(B(m("from app.models import Base") + " — импорт пакета моделей. В его "
        + m("__init__.py") + " перечислены все модели, поэтому они регистрируются в "
        + m("Base.metadata") + ". Забыли импортировать модель — Alembic решит, что таблицу "
        "надо удалить."))
    A(B(m("target_metadata = Base.metadata") + " — эталон, с которым autogenerate сравнивает "
        "базу."))
    A(B(m("connection.run_sync(do_run_migrations)") + " — сам Alembic синхронный, поэтому его "
        "код выполняется внутри асинхронного соединения через " + m("run_sync") + ". Тот же "
        "приём, что и в тестах для " + m("create_all") + "."))
    A(B(m("NullPool") + " — без пула: миграции выполняются один раз, соединение нужно одно."))
    A(B("Два режима: online применяет миграции к базе, offline (" + m("--sql")
        + ") печатает SQL, который был бы выполнен. Второй режим удобен для ревью."))

    # ---------- 42 ----------
    A(P("42. Пишем миграцию руками", "h1"))
    A(P("Файл миграции — обычный Python с двумя функциями: " + m("upgrade") + " применяет "
        "изменение, " + m("downgrade") + " его откатывает. Внутри используется объект "
        + m("op") + " из " + m("alembic") + " — набор команд, которые превращаются в "
        + m("ALTER TABLE") + ", " + m("CREATE INDEX") + " и так далее."))
    A(C("""
\"\"\"add section to articles

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-08
\"\"\"

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "articles",
        sa.Column("section", sa.String(length=16), nullable=False, server_default="blog"),
    )
    op.create_index("ix_articles_section", "articles", ["section"])


def downgrade() -> None:
    op.drop_index("ix_articles_section", table_name="articles")
    op.drop_column("articles", "section")
""", "alembic/versions/0004_add_article_section.py"))
    A(P("Разбор", "h2"))
    A(B(m("revision") + " и " + m("down_revision") + " — место в цепочке. Мы даём короткие "
        "номера вместо случайных хэшей, чтобы порядок читался по имени файла."))
    A(B(m("sa.Column(..., nullable=False, server_default='blog')") + " — главный приём при "
        "добавлении обязательной колонки в непустую таблицу. Без " + m("server_default")
        + " PostgreSQL откажет: у существующих строк нет значения, а NULL запрещён. С ним все "
        "старые статьи получают «blog» в момент ALTER."))
    A(B(m("downgrade") + " делает ровно обратное в обратном порядке: сначала индекс, потом "
        "колонка. Индекс ссылается на колонку, поэтому первым удаляется он."))
    A(B("Строковые имена таблиц и колонок, а не классы моделей. Миграция должна работать, "
        "даже когда модель уже изменилась или удалена."))
    A(P("Команды op, которые нужны чаще всего", "h2"))
    A(table([
        ["Команда", "SQL", "Когда"],
        ["op.create_table(name, *columns)", "CREATE TABLE", "новая таблица"],
        ["op.drop_table(name)", "DROP TABLE", "откат создания"],
        ["op.add_column(table, sa.Column(...))", "ALTER TABLE ... ADD COLUMN", "новое поле"],
        ["op.drop_column(table, name)", "ALTER TABLE ... DROP COLUMN", "откат добавления"],
        ["op.alter_column(table, name, type_=..., nullable=..., new_column_name=...)", "ALTER TABLE ... ALTER COLUMN", "смена типа, обязательности, имени"],
        ["op.create_index(name, table, [cols], unique=False)", "CREATE INDEX", "индекс"],
        ["op.drop_index(name, table_name=...)", "DROP INDEX", "откат индекса"],
        ["op.create_foreign_key(name, src, ref, [cols], [ref_cols], ondelete=...)", "ADD CONSTRAINT ... FOREIGN KEY", "внешний ключ к существующей таблице"],
        ["op.create_check_constraint(name, table, condition)", "ADD CONSTRAINT ... CHECK", "проверка"],
        ["op.create_unique_constraint(name, table, [cols])", "ADD CONSTRAINT ... UNIQUE", "уникальность"],
        ["op.execute(sql)", "любой SQL", "миграция данных, всё нестандартное"],
    ], [66 * mm, 50 * mm, 49 * mm]))
    A(P("Миграция с данными", "h2"))
    A(P("Иногда мало поменять схему: надо преобразовать существующие данные. Например, вынести "
        "теги из строки через запятую в отдельную таблицу. Делается это в три шага внутри "
        "одной миграции: добавить новое, перенести данные через " + m("op.execute")
        + ", удалить старое."))
    A(C("""
def upgrade() -> None:
    op.add_column("articles", sa.Column("reading_minutes", sa.Integer(), nullable=True))

    op.execute(
        \"\"\"
        UPDATE articles
        SET reading_minutes = greatest(1, array_length(regexp_split_to_array(content, '\\s+'), 1) / 180)
        \"\"\"
    )

    op.alter_column("articles", "reading_minutes", nullable=False)


def downgrade() -> None:
    op.drop_column("articles", "reading_minutes")
""", "Пример: колонка «минут на чтение», заполненная по существующему тексту"))
    A(P("Порядок важен: сначала колонка nullable, потом заполнение, потом " + m("nullable=False")
        + ". Иначе ALTER упадёт на пустых значениях. В downgrade данные восстанавливать не "
        "нужно: они вычислимы заново."))
    A(P("Первая миграция: создание таблиц", "h2"))
    A(C("""
def upgrade() -> None:
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.UniqueConstraint("slug", name="uq_tags_slug"),
    )
    op.create_table(
        "article_tags",
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("article_id", "tag_id"),
    )
""", "Фрагмент 0002_create_articles.py"))
    A(P("Порядок создания таблиц тоже важен: " + m("article_tags") + " ссылается на "
        + m("articles") + " и " + m("tags") + ", значит, они должны быть созданы раньше. В "
        "downgrade — обратный порядок: сначала зависимые таблицы."))

    # ---------- 43 ----------
    A(P("43. Autogenerate и alembic check", "h1"))
    A(P("Alembic умеет сравнить " + m("Base.metadata") + " с реальной базой и написать "
        "миграцию сам:"))
    A(C("""
alembic revision --autogenerate -m "add reading minutes"
alembic upgrade head
""", "Сгенерировать и применить"))
    A(P("Это удобно, но черновик нужно читать перед применением. Autogenerate надёжно "
        "замечает новые и удалённые таблицы, колонки и индексы. Он <b>не</b> замечает "
        "переименования: увидит удаление старой колонки и добавление новой, и данные потеряются. "
        "Не всегда видит смену типа и изменение " + m("server_default") + ". И не пишет "
        "миграции данных. Поэтому мы пишем миграции руками, а autogenerate используем как "
        "подсказку и как проверку."))
    A(C("""
alembic check
# No new upgrade operations detected.     ← модели и миграции согласованы
# New upgrade operations detected: ...    ← в моделях есть то, чего нет в миграциях
""", "alembic check: модели против миграций"))
    A(P(m("alembic check") + " сравнивает metadata с базой и падает, если расхождения есть. "
        "Полезно как шаг CI: поменяли модель и забыли миграцию — сборка красная. Требует "
        "живую базу с применёнными миграциями."))
    A(P("Что autogenerate не видит и как с этим жить", "h2"))
    A(table([
        ["Изменение", "Что сделает autogenerate", "Что делать"],
        ["переименование колонки", "drop + add, данные потеряются", "руками op.alter_column(new_column_name=...)"],
        ["переименование таблицы", "drop + create", "руками op.rename_table"],
        ["смена server_default", "часто пропускает", "руками op.alter_column(server_default=...)"],
        ["CheckConstraint", "не всегда сравнивает", "руками op.create_check_constraint"],
        ["преобразование данных", "никогда", "руками op.execute"],
    ], [45 * mm, 60 * mm, 60 * mm]))

    # ---------- 44 ----------
    A(P("44. Эксплуатация миграций", "h1"))
    A(C("""
alembic current                     # какая ревизия применена к базе
alembic history                     # вся цепочка
alembic upgrade head                # применить всё до конца
alembic upgrade +1                  # на одну ревизию вперёд
alembic downgrade -1                # на одну назад
alembic downgrade 0003              # до конкретной ревизии
alembic upgrade 0003:0004 --sql     # показать SQL перехода, не выполняя
""", "Команды на каждый день"))
    A(P("Как миграции применяются на проде", "h2"))
    A(C("""
backend:
  command: >
    sh -c "alembic upgrade head &&
           uvicorn app.main:app --host 0.0.0.0 --port 8000"
""", "docker-compose.yml: миграции перед стартом сервера"))
    A(P("Контейнер бэкенда при каждом запуске сначала выполняет " + m("alembic upgrade head")
        + " и только потом поднимает uvicorn. Если миграция упала, сервер не стартует, "
        "health check в деплое не пройдёт, и вы увидите ошибку в логах вместо тихо сломанного "
        "сайта. Схема базы всегда соответствует коду, который её использует."))
    A(P("Проверка перед пушем", "h2"))
    A(P("Мы проверяли каждую миграцию офлайн, без базы: " + m("alembic upgrade 0003:0004 --sql")
        + " печатает точный SQL. Так была найдена и подтверждена команда с "
        + m("DEFAULT 'blog' NOT NULL") + ". Плюс e2e-тест на SQLite создаёт таблицы через "
        + m("create_all") + " по моделям — если модель и миграция разойдутся, "
        + m("alembic check") + " на проде это покажет."))
    A(P("Типичные ошибки", "h2"))
    A(table([
        ["Симптом", "Причина", "Лечение"],
        ["column contains null values при add_column NOT NULL", "в таблице уже есть строки", "server_default или сначала nullable, заполнить, потом NOT NULL"],
        ["Multiple head revisions", "две ветки миграций с одним down_revision (слияние веток git)", "alembic merge heads, затем upgrade"],
        ["Can't locate revision", "файл миграции удалён, а в alembic_version его номер", "вернуть файл или поправить alembic_version руками"],
        ["Target database is not up to date при autogenerate", "в базе не все миграции", "alembic upgrade head, потом revision"],
        ["autogenerate предлагает удалить таблицу", "модель не импортирована в models/__init__.py", "добавить импорт"],
        ["MissingGreenlet в env.py", "синхронный код на асинхронном движке", "run_sync, как в примере выше"],
    ], [52 * mm, 55 * mm, 58 * mm]))
    A(note("Правило безопасности: перед миграцией, которая удаляет или меняет тип колонки, "
           "снимите дамп (глава 12). Добавление колонок и индексов безопасно, удаление — нет."))

    # ---------- 45 ----------
    A(P("45. Тестирование: SQLite, TestClient и подмена сессии", "h1"))
    A(P("Прод работает на PostgreSQL, а тесты удобно гонять без сервера. Наш e2e-скрипт "
        "поднимает приложение на SQLite в файле и прогоняет через него сорок с лишним "
        "проверок: создание статей, публикацию, теги, просмотры, реакции, загрузку файлов. "
        "Вот скелет."))
    A(C("""
import asyncio
import os
import pathlib

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_session
from app.main import app
from app.models import Base

db_file = pathlib.Path(os.environ["CHECK_DB"])
if db_file.exists():
    db_file.unlink()

engine = create_async_engine(f"sqlite+aiosqlite:///{db_file.as_posix()}")
Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(init())


async def override_session():
    async with Session() as session:
        yield session


app.dependency_overrides[get_session] = override_session
client = TestClient(app)
ADMIN = {"X-Admin-Token": os.environ["ADMIN_API_TOKEN"]}

r = client.post("/api/v1/admin/tags", json={"title": "Экология"}, headers=ADMIN)
assert r.status_code == 201
""", "Скелет e2e-теста"))
    A(P("Три приёма", "h2"))
    A(B(m("Base.metadata.create_all") + " вместо миграций: создаёт таблицы по моделям одним "
        "вызовом. Быстро и не требует Alembic. Через " + m("run_sync") + ", потому что "
        + m("create_all") + " синхронный."))
    A(B(m("app.dependency_overrides[get_session] = override_session") + " — подмена "
        "зависимости FastAPI. Роутеры не меняются, они по-прежнему просят " + m("get_session")
        + ", но получают тестовую сессию на SQLite."))
    A(B(m("TestClient") + " — HTTP-клиент, который вызывает приложение напрямую, без сети. "
        "Запоминает cookie между запросами, поэтому проверка «второй просмотр того же "
        "посетителя не считается» работает."))
    A(P("Где SQLite и PostgreSQL расходятся", "h2"))
    A(table([
        ["Тема", "PostgreSQL", "SQLite", "Как обошли"],
        ["JSONB", "есть", "нет", "JSON().with_variant(JSONB, 'postgresql')"],
        ["timestamptz", "момент времени", "строка", "published_at = func.now(): время ставит база"],
        ["сравнение дат", "по значению", "по строке", "даты со смещением в одном формате"],
        ["now()", "функция", "функция", "везде func.now(), а не datetime.now()"],
        ["UUID", "тип uuid", "нет", "String(36)"],
        ["ON CONFLICT", "есть", "есть (с 3.24)", "не используем, ловим IntegrityError"],
        ["secure cookie по http", "не про базу", "—", "COOKIE_SECURE=false в тестовом окружении"],
    ], [30 * mm, 35 * mm, 30 * mm, 70 * mm]))
    A(P("Вывод: тесты на SQLite ловят логические ошибки, ошибки типов и потоки данных, но не "
        "гарантируют, что SQL поедет на PostgreSQL. Поэтому перед пушем мы дополнительно "
        "смотрели SQL миграций офлайн, а деплой падает, если " + m("alembic upgrade head")
        + " не прошёл. Для серьёзного проекта следующий шаг — тесты на настоящем PostgreSQL в "
        "Docker, например через библиотеку testcontainers."))

    A(PageBreak())
    return S
