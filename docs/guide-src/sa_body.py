"""Главы 13–36 и 46–48: ядро SQLAlchemy из прежней методички, перенумерованное."""


def build(P, B, C, note, table, Spacer, PageBreak, mm, CODE_BG, GOOD_BG):
    S = []
    A = S.append

    # ================= ЧАСТЬ I =================
    A(P("Часть II. Основы SQLAlchemy", "part"))

    # --- 1 ---
    A(P("13. Что такое ORM и зачем он нужен", "h1"))
    A(P("База хранит строки в таблицах. Python работает с объектами. ORM — прослойка, "
        "которая переводит одно в другое: класс становится таблицей, экземпляр — строкой, "
        "атрибут — колонкой."))
    A(C("""
# Без ORM
cursor.execute("SELECT id, name, email FROM requests WHERE id = %s", (5,))
row = cursor.fetchone()
name = row[1]        # надо помнить порядок колонок

# С ORM
request = await session.get(Request, 5)
name = request.name  # понятно без комментариев
"""))
    A(B("<b>Типизация.</b> IDE знает тип поля и подскажет опечатку до запуска."))
    A(B("<b>Безопасность.</b> Параметры экранируются — SQL-инъекция через ORM практически "
        "невозможна."))
    A(B("<b>Переносимость.</b> Один код работает на Postgres, MySQL, SQLite."))
    A(B("<b>Связи.</b> <font name='Mono' size='9'>article.tags</font> вместо ручного JOIN "
        "в каждом запросе."))
    A(Spacer(1, 4))
    A(note("<b>Цена абстракции.</b> ORM скрывает SQL, и легко написать код, который "
           "выглядит невинно, а порождает сотню запросов. Правило: работая с ORM, всегда "
           "представляй, какой SQL получится."))

    # --- 2 ---
    A(P("14. Три кирпича: Base, Mapped, mapped_column", "h1"))
    A(C("""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
""", "app/models/base.py"))
    A(P("От <font name='Mono' size='9'>Base</font> наследуются все модели. Наследование — "
        "это и есть регистрация в реестре схемы."))

    A(P("Mapped и mapped_column — два ответа на два вопроса", "h2"))
    A(C("""
title: Mapped[str] = mapped_column(String(255))
#      ^^^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^^^^^^^
#      чем будет     чем будет
#      в Python      в базе данных
"""))
    A(P("Аннотация не декоративная — SQLAlchemy её читает и выводит из неё "
        "<font name='Mono' size='9'>nullable</font>:"))
    A(C("""
title: Mapped[str]                # NOT NULL
cover_image: Mapped[str | None]   # NULL разрешён
"""))
    A(P("Поэтому <font name='Mono' size='9'>nullable=True</font> руками писать не нужно. "
        "Один источник правды вместо двух, которые могут разойтись."))
    A(note("<b>Самая частая ошибка.</b> Написать "
           "<font name='Mono' size='9'>content = Mapped[Text]</font> вместо "
           "<font name='Mono' size='9'>content: Mapped[str] = mapped_column(Text)</font>. "
           "Две беды сразу: знак равенства вместо двоеточия (присваивание, а не "
           "аннотация) и тип колонки внутри <font name='Mono' size='9'>Mapped[]</font>, "
           "где должен стоять питоновский тип. Колонки не будет, ошибки тоже."))
    A(P("<b>Правило: каждая колонка — это имя : Mapped[тип] = mapped_column(...).</b> "
        "Три части, все обязательны."))

    A(PageBreak())

    # --- 3 ---
    A(P("15. metadata — реестр схемы", "h1"))
    A(P("<font name='Mono' size='9'>Base.metadata</font> — каталог всего, что SQLAlchemy "
        "знает о базе: таблицы, колонки, индексы, внешние ключи. Объявлять не надо, его "
        "создаёт <font name='Mono' size='9'>DeclarativeBase</font>."))
    A(C("""
from app.models import Base

print(Base.metadata.tables.keys())
# dict_keys(['requests', 'articles', 'tags', 'article_tags'])
"""))
    A(P("Реестр читает Alembic:"))
    A(C("""
target_metadata = Base.metadata
""", "alembic/env.py"))
    A(P("Он сравнивает <b>реестр</b> с реальной схемой и генерирует разницу."))
    A(note("<b>Следствие.</b> Таблица попадает в реестр только когда Python выполнил файл "
           "с классом. Модель не импортирована в "
           "<font name='Mono' size='9'>models/__init__.py</font> — её нет в "
           "<font name='Mono' size='9'>metadata</font>, Alembic не видит разницы и создаёт "
           "<b>пустую миграцию</b>. Без ошибки и предупреждения."))
    A(C("""
from app.models.base import Base
from app.models.request import Request      # noqa: F401
from app.models.article import Article, Tag # noqa: F401

__all__ = ["Base", "Request", "Article", "Tag"]
""", "app/models/__init__.py"))

    # --- 4 ---
    A(P("16. Типы колонок", "h1"))
    A(table([
        ["Тип", "Python", "Когда применять"],
        ["Integer", "int", "числа, счётчики, внешние ключи"],
        ["BigInteger", "int", "когда int мало: суммы в копейках, telegram_id"],
        ["SmallInteger", "int", "мелкие значения: рейтинг 1-5, номер месяца"],
        ["String(n)", "str", "текст с известным пределом"],
        ["Text", "str", "длинный текст: статья, комментарий"],
        ["Boolean", "bool", "флаги"],
        ["DateTime(timezone=True)", "datetime", "метки времени, timezone обязателен"],
        ["Date", "date", "дата без времени: дедлайн"],
        ["Time", "time", "время без даты: часы работы"],
        ["Interval", "timedelta", "длительность"],
        ["Numeric(10, 2)", "Decimal", "деньги — не Float"],
        ["Float", "float", "измерения, где точность не критична"],
        ["Enum(PyEnum)", "Enum", "фиксированный набор: статус, роль"],
        ["JSON / JSONB", "dict, list", "неструктурированные данные"],
        ["ARRAY(Integer)", "list[int]", "массив, только Postgres"],
        ["UUID", "UUID", "идентификатор, только Postgres"],
        ["LargeBinary", "bytes", "бинарные данные (лучше хранить файлы вне БД)"],
    ], [40 * mm, 26 * mm, 99 * mm]))

    A(Spacer(1, 8))
    A(P("Живой пример", "h2"))
    A(C("""
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    comment: Mapped[str] = mapped_column(Text, default="")
    sum_amount: Mapped[int] = mapped_column(BigInteger)
    deadline: Mapped[date] = mapped_column(Date)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), index=True)
""", "agregator/models/order.py"))
    A(P("Выбор осмысленный: <font name='Mono' size='9'>title</font> ограничен, "
        "<font name='Mono' size='9'>comment</font> нет; сумма в "
        "<font name='Mono' size='9'>BigInteger</font>, потому что копейки крупного заказа "
        "переполнят <font name='Mono' size='9'>INTEGER</font>; дедлайн — "
        "<font name='Mono' size='9'>Date</font>, время суток бессмысленно."))

    A(P("Деньги: Numeric, а не Float", "h2"))
    A(C("""
>>> 0.1 + 0.2
0.30000000000000004        # Float — двоичная дробь, копейки теряются

price: Mapped[Decimal] = mapped_column(Numeric(10, 2))   # правильно
price: Mapped[int] = mapped_column(BigInteger)           # тоже: хранить в копейках
"""))

    A(P("Идентификаторы — всегда строка", "h2"))
    A(C("""
inn: Mapped[str | None] = mapped_column(String(12))   # правильно
inn: Mapped[int | None] = mapped_column(Integer)      # ошибка
"""))
    A(P("ИНН <font name='Mono' size='9'>0123456789</font> в числовой колонке станет "
        "<font name='Mono' size='9'>123456789</font>. Правило: если «число» нельзя "
        "складывать — это идентификатор, и хранить его надо текстом. Телефоны, ИНН, "
        "артикулы, номера договоров."))

    A(PageBreak())

    # --- 5 ---
    A(P("17. Параметры колонок", "h1"))
    A(table([
        ["Параметр", "Что делает"],
        ["primary_key=True", "первичный ключ; индекс создаётся автоматически"],
        ["unique=True", "запрет дублей на уровне БД"],
        ["index=True", "индекс для ускорения поиска"],
        ["nullable=False", "выводится из аннотации, писать не нужно"],
        ["default=...", "значение подставляет Python перед вставкой"],
        ["server_default=...", "значение подставляет база"],
        ["onupdate=...", "пересчитывается при UPDATE через ORM"],
        ["server_onupdate=...", "то же, но на стороне базы"],
        ["ForeignKey(...)", "ссылка на колонку другой таблицы"],
        ["comment='...'", "комментарий к колонке в схеме БД"],
        ["autoincrement=False", "отключить автоинкремент у целочисленного PK"],
    ], [46 * mm, 119 * mm]))

    A(Spacer(1, 8))
    A(note("<b>index=True на primary_key не нужен.</b> Первичный ключ индексируется "
           "автоматически. Добавив <font name='Mono' size='9'>index=True</font>, вы "
           "создадите второй, дублирующий индекс: лишнее место и лишняя работа при "
           "каждой вставке."))

    A(P("default против server_default", "h2"))
    A(C("""
# Python ставит значение перед вставкой
created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

# База ставит значение сама
created_at: Mapped[datetime] = mapped_column(server_default=func.now())
"""))
    A(table([
        ["", "default", "server_default"],
        ["Кто вычисляет", "Python", "база данных"],
        ["Работает при вставке мимо ORM", "нет", "да"],
        ["Видно в схеме таблицы", "нет", "да"],
        ["Что передавать", "значение или функцию", "SQL-выражение или строку"],
    ], [46 * mm, 60 * mm, 59 * mm]))

    A(Spacer(1, 8))
    A(P("Для времени создания надёжнее база: процессов приложения может быть несколько, и "
        "часы у них разъезжаются, а база одна. Кроме того, "
        "<font name='Mono' size='9'>server_default</font> обязателен, когда добавляешь "
        "<font name='Mono' size='9'>NOT NULL</font>-колонку в таблицу с существующими "
        "строками — иначе миграция не пройдёт."))
    A(C("""
# server_default принимает SQL, а не Python-значение
is_active: Mapped[bool] = mapped_column(server_default="true")
count: Mapped[int] = mapped_column(server_default=text("0"))
created: Mapped[datetime] = mapped_column(server_default=func.now())
"""))

    A(note("<b>Ловушка изменяемых значений по умолчанию.</b> Пишите "
           "<font name='Mono' size='9'>default=list</font>, а не "
           "<font name='Mono' size='9'>default=[]</font>. Список, записанный литералом, "
           "создаётся один раз при импорте модуля и станет общим для всех строк. "
           "Передавать надо функцию."))

    A(P("onupdate", "h2"))
    A(C("""
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),      # пересчитается при каждом UPDATE
)
"""))
    A(P("Работает при обновлении через ORM. Если данные меняют напрямую в SQL, нужен "
        "триггер в базе или <font name='Mono' size='9'>server_onupdate</font>."))

    A(PageBreak())

    # --- 6 ---
    A(P("18. Ограничения и индексы: __table_args__", "h1"))
    A(P("Ограничения на уровне колонки задаются в "
        "<font name='Mono' size='9'>mapped_column</font>. Всё, что затрагивает "
        "<b>несколько колонок сразу</b>, — в "
        "<font name='Mono' size='9'>__table_args__</font>."))

    A(C("""
from sqlalchemy import CheckConstraint, Index, UniqueConstraint


class Account(Base):
    __tablename__ = "accounts"

    email: Mapped[str | None] = mapped_column(String(320))
    phone: Mapped[str | None] = mapped_column(String(20))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))

    __table_args__ = (
        CheckConstraint(
            "(email IS NOT NULL OR phone IS NOT NULL)",
            name="account_email_or_phone_required",
        ),
        UniqueConstraint("email", "role", name="uq_accounts_email_role"),
        UniqueConstraint("phone", "role", name="uq_accounts_phone_role"),
    )
""", "agregator: аккаунт"))

    A(P("Что здесь описано", "h2"))
    A(B("<b>CheckConstraint</b> — правило, которое база проверяет при каждой записи. Тут: "
        "должен быть указан хотя бы email или телефон. Логику «или» нельзя выразить через "
        "<font name='Mono' size='9'>nullable</font>, поэтому она уходит в ограничение."))
    A(B("<b>UniqueConstraint по двум колонкам</b> — уникальна не почта сама по себе, а "
        "пара «почта + роль». Один человек может быть и заказчиком, и экспертом с одной "
        "почтой, но не может завести два аккаунта заказчика."))
    A(Spacer(1, 4))
    A(note("<b>Всегда давайте ограничениям имя.</b> Без "
           "<font name='Mono' size='9'>name=</font> база придумает своё, и в разных "
           "окружениях оно может отличаться — Alembic начнёт генерировать миграции "
           "«на пустом месте», пытаясь переименовать ограничение туда-сюда.", CODE_BG))

    A(P("Составные и частичные индексы", "h2"))
    A(C("""
    __table_args__ = (
        # составной: ускоряет WHERE status=... AND created_at > ...
        Index("ix_orders_status_created", "status", "created_at"),

        # частичный: индексируем только активные — он меньше и быстрее
        Index(
            "ix_orders_active",
            "created_at",
            postgresql_where=text("status = 'ACTIVE'"),
        ),

        # уникальный составной
        Index("uq_view_once", "article_id", "visitor_id", unique=True),
    )
"""))
    A(P("Порядок колонок в составном индексе важен: он работает для условий по первой "
        "колонке или по первой+второй, но не по одной только второй. Правило — сначала "
        "то, по чему фильтруют точным сравнением, потом диапазоны."))

    A(P("Когда индекс нужен", "h2"))
    A(B("Внешние ключи — Postgres <b>не создаёт</b> индекс на FK автоматически, а join и "
        "фильтр по нему идут постоянно."))
    A(B("Колонки в <font name='Mono' size='9'>WHERE</font> и "
        "<font name='Mono' size='9'>ORDER BY</font> частых запросов."))
    A(B("<font name='Mono' size='9'>slug</font>, по которому ищется каждая статья."))
    A(Spacer(1, 4))
    A(P("Индекс ускоряет чтение и замедляет запись — на каждую вставку его надо "
        "обновлять. Поэтому индексируют не всё подряд, а то, по чему реально ищут."))

    A(PageBreak())

    # --- 7 ---
    A(P("19. Enum в моделях", "h1"))
    A(P("Когда у поля фиксированный набор значений — статус, роль, тип работ — его "
        "описывают перечислением. Так набор задан в одном месте, а не размазан по "
        "строковым литералам."))

    A(C("""
from enum import Enum as PyEnum
from sqlalchemy import Enum


class OrderStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class Order(Base):
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        index=True,
        default=OrderStatus.ACTIVE,
        server_default=OrderStatus.ACTIVE.value,
    )
""", "agregator: статус заказа"))

    A(P("Зачем наследоваться от str", "h2"))
    A(P("<font name='Mono' size='9'>class OrderStatus(str, PyEnum)</font> — значение "
        "остаётся строкой, и его можно сравнивать, сериализовать в JSON и передавать в "
        "Pydantic без преобразований."))
    A(C("""
OrderStatus.ACTIVE == "ACTIVE"     # True — благодаря наследованию от str
"""))

    A(note("<b>Изменение Enum — это миграция.</b> В Postgres перечисление становится "
           "отдельным типом в базе. Добавить значение можно "
           "(<font name='Mono' size='9'>ALTER TYPE ... ADD VALUE</font>), удалить или "
           "переименовать — гораздо сложнее. Поэтому набор значений продумывают заранее, "
           "а <font name='Mono' size='9'>autogenerate</font> изменения Enum <b>не "
           "отслеживает</b> — миграцию придётся писать руками."))

    A(P("Альтернатива: строка с CheckConstraint", "h2"))
    A(C("""
status: Mapped[str] = mapped_column(String(20))

__table_args__ = (
    CheckConstraint("status IN ('ACTIVE', 'ARCHIVED')", name="ck_order_status"),
)
"""))
    A(P("Менять набор проще (обычная миграция ограничения), но теряется типизация в "
        "Python. Выбор зависит от того, насколько часто ожидаются изменения."))

    # --- 8 ---
    A(P("20. Миксины: переиспользование колонок", "h1"))
    A(P("<font name='Mono' size='9'>created_at</font> и "
        "<font name='Mono' size='9'>updated_at</font> нужны почти в каждой таблице. "
        "Копировать их в двадцать моделей — значит однажды где-то ошибиться."))

    A(C("""
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Article(TimestampMixin, Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    # created_at и updated_at пришли из миксина
""", "миксин с метками времени"))

    A(P("Порядок наследования важен: миксин идёт <b>первым</b>, "
        "<font name='Mono' size='9'>Base</font> — последним."))

    A(P("Миксин с внешним ключом", "h2"))
    A(P("Если в миксине нужен <font name='Mono' size='9'>ForeignKey</font> или "
        "<font name='Mono' size='9'>relationship</font>, объявлять их надо через "
        "<font name='Mono' size='9'>declared_attr</font> — иначе один и тот же объект "
        "колонки попытается принадлежать нескольким таблицам сразу."))
    A(C("""
from sqlalchemy.orm import declared_attr


class AuthorMixin:
    @declared_attr
    def author_id(cls) -> Mapped[int]:
        return mapped_column(ForeignKey("accounts.id", ondelete="SET NULL"))

    @declared_attr
    def author(cls) -> Mapped["Account"]:
        return relationship("Account")
"""))

    A(PageBreak())

    # ================= ЧАСТЬ II =================
    A(P("Часть III. Связи", "part"))

    # --- 9 ---
    A(P("21. Как понять, какая связь нужна", "h1"))
    A(P("Связей три вида, и выбрать помогает один вопрос, заданный <b>с обеих сторон</b>."))
    A(C("""
Сколько Б может быть у одного А?   и   Сколько А может быть у одного Б?

один  — один   ->  1:1
один  — много  ->  1:N
много — много  ->  M:N
"""))
    A(table([
        ["Пример", "Туда", "Обратно", "Связь"],
        ["Аккаунт — профиль эксперта", "один", "один", "1:1"],
        ["Аккаунт — заказы", "много", "один", "1:N"],
        ["Заказ — бейджи", "много", "один", "1:N"],
        ["Статья — теги", "много", "много", "M:N"],
    ], [58 * mm, 30 * mm, 33 * mm, 27 * mm]))

    A(Spacer(1, 8))
    A(P("Где физически лежит связь", "h2"))
    A(P("Это главное. Связь — это <b>колонка с внешним ключом</b>, и вопрос лишь в том, в "
        "какой таблице она помещается."))
    A(table([
        ["Связь", "Где хранится", "Что писать"],
        ["1:1", "FK в одной из таблиц + unique", "relationship(uselist=False)"],
        ["1:N", "FK в таблице «многих»", "relationship(...)"],
        ["M:N", "отдельная таблица", "Table + relationship(secondary=...)"],
    ], [22 * mm, 63 * mm, 80 * mm]))

    A(Spacer(1, 8))
    A(note("<b>Почему M:N требует третью таблицу.</b> Куда положить колонку? В "
           "<font name='Mono' size='9'>articles</font> — у статьи станет один тег. В "
           "<font name='Mono' size='9'>tags</font> — тег будет принадлежать одной статье. "
           "Обе стороны «многие», колонке негде поместиться."))

    # --- 10 ---
    A(P("22. Один ко многим (1:N)", "h1"))
    A(C("""
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), index=True
    )

    customer: Mapped["Account"] = relationship(back_populates="orders")


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)

    orders: Mapped[list["Order"]] = relationship(back_populates="customer")
""", "agregator: аккаунт и его заказы"))

    A(C("""
orders
+----+-------------+---------------------+
| id | customer_id | title               |
+----+-------------+---------------------+
|  1 |          42 | Экспертиза ПБ       |
|  2 |          42 | Проект котельной    |
|  3 |          77 | Изыскания           |
+----+-------------+---------------------+

У аккаунта 42 два заказа. Одной колонки хватает.
"""))

    A(P("Две стороны одной связи", "h2"))
    A(P("<font name='Mono' size='9'>Order.customer</font> — один объект, "
        "<font name='Mono' size='9'>Account.orders</font> — список. Это одна связь с "
        "разных сторон, и связывает их "
        "<font name='Mono' size='9'>back_populates</font>: имя атрибута напротив."))
    A(C("""
account.orders.append(new_order)
new_order.customer      # Account(id=42) — проставилось само
"""))

    A(P("Индекс на внешнем ключе", "h2"))
    A(P("Postgres <b>не создаёт</b> индекс на FK автоматически (в отличие от первичного "
        "ключа). А запрос «все заказы аккаунта» идёт именно по этой колонке. Без индекса "
        "база читает таблицу целиком: на десяти строках незаметно, на миллионе фатально."))

    A(PageBreak())

    # --- 11 ---
    A(P("23. Один к одному (1:1)", "h1"))
    A(C("""
class Account(Base):
    expert_profile: Mapped["Expert | None"] = relationship(
        back_populates="account",
        uselist=False,           # не список, а один объект или None
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Expert(Base):
    __tablename__ = "experts"

    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), unique=True
    )
    account: Mapped["Account"] = relationship(back_populates="expert_profile")
""", "agregator: аккаунт и профиль эксперта"))

    A(note("<b>unique=True на внешнем ключе — это и есть «один к одному».</b> Без него "
           "база позволит создать два профиля для одного аккаунта, а "
           "<font name='Mono' size='9'>uselist=False</font> вернёт случайный. Ограничение "
           "должно стоять в схеме, а не только в коде."))

    A(P("Когда разделять на две таблицы", "h2"))
    A(B("<b>Разные наборы полей.</b> У заказа в agregator есть "
        "<font name='Mono' size='9'>cadastral_details</font>, "
        "<font name='Mono' size='9'>forensic_details</font>, "
        "<font name='Mono' size='9'>laboratory_details</font> — для каждого типа работ "
        "свой набор. Слить их в одну таблицу значит получить сотню колонок, из которых "
        "заполнены пять."))
    A(B("<b>Необязательность.</b> Профиль эксперта есть не у каждого аккаунта."))
    A(B("<b>Объём.</b> Редко читаемое тяжёлое поле выносят, чтобы не тащить его в каждом "
        "запросе."))

    # --- 12 ---
    A(P("24. Многие ко многим (M:N)", "h1"))
    A(C("""
article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", ForeignKey("articles.id", ondelete="CASCADE"),
           primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"),
           primary_key=True),
)


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))

    tags: Mapped[list["Tag"]] = relationship(
        secondary=article_tags,
        back_populates="articles",
        lazy="selectin",
    )


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))

    articles: Mapped[list["Article"]] = relationship(
        secondary=article_tags,
        back_populates="tags",
    )
""", "nedra: статьи блога и теги"))

    A(C("""
articles              tags                  article_tags
+----+----------+     +----+------------+   +------------+--------+
| id | title    |     | id | title      |   | article_id | tag_id |
+----+----------+     +----+------------+   +------------+--------+
|  1 | Мини-НПЗ |     |  1 | Бизнес     |   |          1 |      1 |
|  2 | Небо ТЭК |     |  2 | Безопасн.  |   |          1 |      2 |
+----+----------+     +----+------------+   |          2 |      2 |
                                            +------------+--------+
"""))

    A(P("Зачем Base.metadata в Table", "h2"))
    A(P("Класс попадает в реестр через наследование от "
        "<font name='Mono' size='9'>Base</font>. "
        "<font name='Mono' size='9'>Table</font> ни от чего не наследуется, поэтому "
        "реестр передают вторым аргументом. Без этого Alembic таблицу не увидит."))

    A(P("Почему Column, а не mapped_column", "h2"))
    A(P("<font name='Mono' size='9'>mapped_column</font> связывает колонку с атрибутом "
        "класса и даёт типизацию. У <font name='Mono' size='9'>Table</font> класса нет — "
        "значит нет и атрибутов, нечего типизировать. Здесь голый "
        "<font name='Mono' size='9'>Column</font>."))

    A(P("Составной первичный ключ", "h2"))
    A(P("<font name='Mono' size='9'>primary_key=True</font> на обеих колонках даёт ключ из "
        "пары. База сама запретит вставить <font name='Mono' size='9'>(1, 1)</font> "
        "дважды. Отдельный <font name='Mono' size='9'>id</font> здесь не нужен и вреден: "
        "с ним дубли снова станут возможны."))
    A(C("""
article.tags.append(tag)   # SQLAlchemy сама вставит строку в article_tags
article.tags               # [Tag(...), Tag(...)] — сама сделает JOIN
"""))

    A(PageBreak())

    # --- 13 ---
    A(P("25. Промежуточная таблица: Table или модель", "h1"))
    A(P("Развилка, которая встречается в каждом проекте. Ответ зависит от одного: "
        "<b>есть ли у самой связи собственные данные</b>."))

    A(P("Вариант A: Table — связь это просто факт", "h2"))
    A(P("«У статьи есть тег». Больше сказать нечего — значит "
        "<font name='Mono' size='9'>Table</font>."))

    A(P("Вариант B: модель — у связи есть свойства", "h2"))
    A(P("«Эксперт аттестован по специализации <b>с такого-то года</b>, документ "
        "<b>такой-то</b>». Эти поля не про эксперта и не про специализацию, а именно про "
        "их связь. Такую модель называют association object."))
    A(C("""
class ExpertSpecialization(Base):
    __tablename__ = "expert_specializations"

    expert_id: Mapped[int] = mapped_column(
        ForeignKey("experts.id", ondelete="CASCADE"), primary_key=True
    )
    specialization_id: Mapped[int] = mapped_column(
        ForeignKey("specializations.id", ondelete="CASCADE"), primary_key=True
    )

    # ради этого и понадобился класс
    certified_since: Mapped[date] = mapped_column(Date)
    certificate_number: Mapped[str] = mapped_column(String(100))

    expert: Mapped["Expert"] = relationship(back_populates="specializations")
    specialization: Mapped["Specialization"] = relationship(
        back_populates="experts"
    )
"""))

    A(note("<b>Разница в использовании.</b> С <font name='Mono' size='9'>Table</font> "
           "работаешь со списком целевых объектов: "
           "<font name='Mono' size='9'>article.tags</font> — список "
           "<font name='Mono' size='9'>Tag</font>. С association object — список "
           "<b>связей</b>, и до специализации надо идти через "
           "<font name='Mono' size='9'>.specialization</font>. Менее удобно, поэтому не "
           "превращайте связь в модель без нужды."))

    A(table([
        ["Вопрос", "Table", "Модель"],
        ["У связи есть свои поля?", "нет", "да"],
        ["Нужна дата создания связи?", "нет", "да"],
        ["Связь надо менять, а не только добавлять и удалять?", "нет", "да"],
        ["Пример", "статья — тег", "эксперт — специализация"],
    ], [70 * mm, 30 * mm, 65 * mm]))

    A(Spacer(1, 6))
    A(note("<b>Формулировка для собеседования.</b> «Промежуточная таблица без своих полей "
           "описывается через <font name='Mono' size='9'>Table</font> и подключается "
           "параметром <font name='Mono' size='9'>secondary</font>. Если у связи "
           "появляются собственные атрибуты, она становится association object — обычной "
           "моделью с двумя внешними ключами в составном первичном ключе».", GOOD_BG))

    # --- 14 ---
    A(P("26. Параметры relationship", "h1"))
    A(table([
        ["Параметр", "Зачем"],
        ["back_populates", "имя атрибута на другой стороне; держит стороны в согласии"],
        ["secondary", "промежуточная таблица для M:N"],
        ["uselist=False", "связь 1:1 — один объект вместо списка"],
        ["cascade", "что делать со связанными объектами при операциях с родителем"],
        ["passive_deletes=True", "доверить каскадное удаление базе"],
        ["lazy", "стратегия загрузки"],
        ["foreign_keys", "какой FK использовать, если их несколько"],
        ["order_by", "порядок элементов в списке"],
        ["primaryjoin", "своё условие соединения, когда FK недостаточно"],
        ["viewonly=True", "связь только для чтения, изменения не пишутся"],
        ["single_parent=True", "объект может принадлежать только одному родителю"],
    ], [46 * mm, 119 * mm]))

    A(Spacer(1, 8))
    A(P("foreign_keys — когда связей несколько", "h2"))
    A(C("""
class Order(Base):
    customer_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    assigned_expert_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts.id")
    )

    customer: Mapped["Account"] = relationship(
        foreign_keys=[customer_id], back_populates="orders"
    )
    assigned_expert: Mapped["Account | None"] = relationship(
        foreign_keys=[assigned_expert_id], back_populates="assigned_orders"
    )
""", "две связи к одной таблице"))
    A(P("Без <font name='Mono' size='9'>foreign_keys</font> приложение не запустится: "
        "SQLAlchemy не сможет определить условие соединения."))

    A(P("order_by и viewonly", "h2"))
    A(C("""
comments: Mapped[list["Comment"]] = relationship(
    order_by="Comment.created_at.desc()",   # свежие первыми
)

last_message: Mapped["Message | None"] = relationship(
    primaryjoin="and_(Chat.id == Message.chat_id, Message.is_last == True)",
    viewonly=True,       # вычисляемая связь, писать в неё нельзя
)
"""))

    A(PageBreak())

    # --- 15 ---
    A(P("27. Загрузка данных: lazy, N+1 и async", "h1"))
    A(P("Самая важная глава. Здесь живут и главная ошибка производительности, и главная "
        "ошибка async."))

    A(P("Проблема N+1", "h2"))
    A(C("""
articles = (await session.execute(select(Article).limit(12))).scalars().all()

for article in articles:
    print(article.tags)     # каждое обращение — отдельный запрос
"""))
    A(C("""
SELECT * FROM articles LIMIT 12;                              -- 1 запрос
SELECT * FROM tags JOIN article_tags ... WHERE article_id=1;  -- +1
SELECT * FROM tags JOIN article_tags ... WHERE article_id=2;  -- +1
...                                                           -- ещё 10
                                                    итого 13 запросов
"""))
    A(P("Один запрос за списком плюс по одному на каждый элемент. На списке из 1000 "
        "записей — 1001 запрос."))

    A(P("Стратегии загрузки", "h2"))
    A(P("Задаются параметром <font name='Mono' size='9'>lazy=</font> в "
        "<font name='Mono' size='9'>relationship</font>."))
    A(table([
        ["Значение lazy", "Как работает", "Когда"],
        ["lazy=\"select\" (по умолчанию)", "отдельный запрос в момент обращения", "почти никогда в async"],
        ["lazy=\"selectin\"", "доп. запрос WHERE id IN (...)", "списки — лучший выбор"],
        ["lazy=\"joined\"", "JOIN в основном запросе", "1:1 и «многие к одному»"],
        ["lazy=\"subquery\"", "подзапрос", "устарел, вместо него selectin"],
        ["lazy=\"raise\"", "исключение при ленивой загрузке", "чтобы ловить N+1 на тестах"],
        ["lazy=\"noload\"", "всегда пустой список", "когда связь точно не нужна"],
    ], [42 * mm, 58 * mm, 65 * mm]))

    A(Spacer(1, 6))
    A(note("<b>Не путайте с функцией <font name='Mono' size='9'>select()</font>.</b> Это "
           "разные вещи с одинаковым именем. "
           "<font name='Mono' size='9'>select(Article)</font> — функция построения "
           "запроса, вы пишете её сами и выполняете через "
           "<font name='Mono' size='9'>await session.execute(...)</font>; она нужна всегда "
           "и в async работает прекрасно. "
           "<font name='Mono' size='9'>lazy=\"select\"</font> — стратегия, при которой "
           "SQLAlchemy пытается сходить в базу <b>сама</b>, в момент чтения "
           "<font name='Mono' size='9'>article.tags</font>, без "
           "<font name='Mono' size='9'>await</font>. Вот это в async и невозможно. Правило "
           "простое: явный запрос с <font name='Mono' size='9'>await</font> работает, "
           "неявный без него — падает."))

    A(Spacer(1, 8))
    A(P("Два способа задать стратегию", "h2"))
    A(C("""
# 1. В модели — всегда так грузить
tags: Mapped[list["Tag"]] = relationship(secondary=article_tags,
                                         lazy="selectin")

# 2. В конкретном запросе — только здесь
from sqlalchemy.orm import selectinload, joinedload

stmt = select(Article).options(selectinload(Article.tags)).limit(12)

# вложенные связи
stmt = select(Order).options(
    selectinload(Order.responses).selectinload(OrderResponse.expert)
)
"""))
    A(P("Первый способ удобнее, когда связь нужна почти всегда (теги статьи, бейджи "
        "заказа). Второй — когда она нужна редко."))

    A(note("<b>В async ленивая загрузка не работает вообще.</b> Обращение к незагруженной "
           "связи выбросит <font name='Mono' size='9'>MissingGreenlet</font>. Ленивая "
           "подгрузка делает синхронный запрос в момент чтения атрибута, а в асинхронном "
           "коде синхронных запросов быть не может. Поэтому стратегию нужно задавать "
           "<b>всегда</b> — в модели или в запросе. Это не оптимизация, а обязательное "
           "условие."))

    A(P("Почему selectin, а не joined", "h2"))
    A(P("<font name='Mono' size='9'>joined</font> делает один запрос с JOIN — идеально для "
        "«многие к одному». Но для списка «один ко многим» JOIN размножает строки: 12 "
        "статей по 3 тега дадут 36 строк, где данные статей продублированы трижды. "
        "<font name='Mono' size='9'>selectin</font> делает второй запрос с "
        "<font name='Mono' size='9'>WHERE id IN (...)</font> — данных по сети меньше."))

    A(P("Как увидеть свои запросы", "h2"))
    A(C("""
engine = create_async_engine(url, echo=True)   # печатает весь SQL в консоль
"""))

    A(PageBreak())

    # --- 16 ---
    A(P("28. Удаление: cascade и ondelete", "h1"))
    A(P("Похожие вещи настраиваются в двух разных местах и работают на разных уровнях."))
    A(table([
        ["", "cascade", "ondelete"],
        ["Где пишется", "в relationship", "в ForeignKey"],
        ["Кто исполняет", "SQLAlchemy (Python)", "база данных"],
        ["Как работает", "выгружает детей, удаляет по одному", "удаляет одним запросом"],
        ["Работает мимо ORM?", "нет", "да"],
    ], [38 * mm, 64 * mm, 63 * mm]))

    A(Spacer(1, 8))
    A(C("""
class Order(Base):
    badges: Mapped[list["OrderBadge"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",   # уровень ORM
        passive_deletes=True,           # доверить работу базе
    )


class OrderBadge(Base):
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE")   # уровень БД
    )
""", "agregator: правильная связка"))

    A(B("<b>cascade=\"all, delete-orphan\"</b> — удаляя заказ через ORM, удалить и бейджи. "
        "<font name='Mono' size='9'>delete-orphan</font> добавляет: бейдж, выброшенный из "
        "списка, тоже удаляется — он потерял родителя."))
    A(B("<b>ondelete=\"CASCADE\"</b> — то же правило в самой базе. Сработает даже при "
        "удалении напрямую через SQL."))
    A(B("<b>passive_deletes=True</b> — не выгружать детей в память ради удаления. Без него "
        "SQLAlchemy сначала прочитает все бейджи, потом удалит по одному."))

    A(P("Значения cascade", "h2"))
    A(table([
        ["Значение", "Что делает"],
        ["save-update", "сохранять связанные объекты вместе с родителем (по умолчанию)"],
        ["merge", "объединять связанные при merge()"],
        ["delete", "удалять детей при удалении родителя"],
        ["delete-orphan", "удалять ребёнка, отвязанного от родителя"],
        ["all", "сокращение для save-update, merge, refresh-expire, expunge, delete"],
    ], [36 * mm, 129 * mm]))

    A(Spacer(1, 8))
    A(P("ondelete: варианты", "h2"))
    A(table([
        ["Значение", "Что происходит при удалении родителя"],
        ["CASCADE", "дети удаляются: бейджи заказа, связи с тегами"],
        ["SET NULL", "ссылка обнуляется: у заказа снимается назначенный эксперт"],
        ["RESTRICT", "удаление запрещено, пока есть дети"],
        ["NO ACTION", "по умолчанию: ошибка внешнего ключа"],
    ], [32 * mm, 133 * mm]))

    A(Spacer(1, 8))
    A(P("В agregator выбор осмысленный: у заказа "
        "<font name='Mono' size='9'>customer_id</font> — "
        "<font name='Mono' size='9'>CASCADE</font> (нет заказчика — нет заказа), а "
        "<font name='Mono' size='9'>assigned_expert_id</font> — "
        "<font name='Mono' size='9'>SET NULL</font> (эксперт ушёл, заказ остался и его "
        "можно переназначить)."))

    A(PageBreak())

    # ================= ЧАСТЬ III =================
    A(P("Часть IV. Запросы", "part"))

    # --- 17 ---
    A(P("29. select: основы", "h1"))
    A(C("""
from sqlalchemy import select

# по первичному ключу — самый короткий путь
article = await session.get(Article, 5)

# по условию
stmt = select(Article).where(Article.slug == "mini-npz")
article = (await session.execute(stmt)).scalar_one_or_none()

# список с фильтром, сортировкой и пагинацией
stmt = (
    select(Article)
    .where(Article.published_at.is_not(None))
    .order_by(Article.published_at.desc())
    .limit(12)
    .offset(0)
)
articles = list((await session.execute(stmt)).scalars().all())
"""))

    A(P("Методы результата", "h2"))
    A(table([
        ["Метод", "Возвращает"],
        ["scalar_one_or_none()", "объект или None; ошибка, если найдено больше одного"],
        ["scalar_one()", "ровно один; ошибка и когда ничего не найдено"],
        ["scalars().all()", "список объектов"],
        ["scalars().first()", "первый или None"],
        ["session.scalar(stmt)", "сразу одно значение — удобно для COUNT"],
        ["all()", "список кортежей (когда выбираешь несколько колонок)"],
    ], [46 * mm, 119 * mm]))

    A(Spacer(1, 8))
    A(P("Запрос строится по частям", "h2"))
    A(C("""
stmt = select(Article)

if tag_slug:
    stmt = stmt.join(Article.tags).where(Tag.slug == tag_slug)

if only_published:
    stmt = stmt.where(Article.published_at.is_not(None))

stmt = stmt.order_by(Article.published_at.desc()).limit(limit)
"""))
    A(P("Каждый вызов возвращает <b>новый</b> объект запроса, а не меняет старый. Поэтому "
        "результат обязательно присваивать обратно — "
        "<font name='Mono' size='9'>stmt.where(...)</font> без "
        "<font name='Mono' size='9'>stmt =</font> не сделает ничего."))

    A(P("Выбор отдельных колонок", "h2"))
    A(C("""
# только нужные поля — меньше данных по сети
stmt = select(Article.id, Article.title, Article.views_count)
rows = (await session.execute(stmt)).all()

for row in rows:
    print(row.title, row.views_count)   # доступ по имени
"""))

    # --- 18 ---
    A(P("30. Операторы и условия", "h1"))
    A(table([
        ["Python", "SQL", "Пример"],
        ["==", "=", "Article.slug == 'npz'"],
        ["!=", "<>", "Order.status != 'ARCHIVED'"],
        [">  >=  <  <=", "> >= < <=", "Article.views_count >= 100"],
        [".in_([...])", "IN", "Article.id.in_([1, 2, 3])"],
        [".not_in([...])", "NOT IN", "Tag.slug.not_in(['spam'])"],
        [".is_(None)", "IS NULL", "Article.published_at.is_(None)"],
        [".is_not(None)", "IS NOT NULL", "Article.cover_image.is_not(None)"],
        [".like('%x%')", "LIKE", "Article.title.like('%НПЗ%')"],
        [".ilike('%x%')", "ILIKE", "Article.title.ilike('%нпз%')"],
        [".between(a, b)", "BETWEEN", "Order.deadline.between(d1, d2)"],
        [".startswith('x')", "LIKE 'x%'", "Tag.slug.startswith('prom')"],
        [".contains(x)", "для связей", "Article.tags.contains(tag)"],
        [".any()", "EXISTS", "Article.tags.any(Tag.slug == 'npz')"],
    ], [36 * mm, 30 * mm, 99 * mm]))

    A(Spacer(1, 8))
    A(P("Логические операторы", "h2"))
    A(C("""
from sqlalchemy import and_, or_, not_

# И — просто перечисление через запятую
select(Article).where(
    Article.published_at.is_not(None),
    Article.views_count > 100,
)

# то же явно
select(Article).where(and_(...))

# ИЛИ
select(Tag).where(or_(Tag.slug == "npz", Tag.slug == "bpla"))

# отрицание
select(Article).where(not_(Article.slug.startswith("draft")))
"""))
    A(note("<b>Не используйте Python-операторы and / or / not.</b> Они работают с "
           "истинностью объекта, а не строят SQL. Нужны именно "
           "<font name='Mono' size='9'>and_</font>, "
           "<font name='Mono' size='9'>or_</font>, "
           "<font name='Mono' size='9'>not_</font> — либо перечисление через запятую для "
           "«И»."))

    A(P("Фильтр по связи", "h2"))
    A(C("""
# статьи, у которых есть тег с таким slug — без JOIN, через EXISTS
stmt = select(Article).where(Article.tags.any(Tag.slug == "promyshlennost"))

# у заказа есть хотя бы один отклик
stmt = select(Order).where(Order.responses.any())

# все отклики удовлетворяют условию
stmt = select(Order).where(~Order.responses.any(OrderResponse.price > 100000))
"""))
    A(P("<font name='Mono' size='9'>.any()</font> разворачивается в "
        "<font name='Mono' size='9'>EXISTS</font> и <b>не даёт дублей</b>, в отличие от "
        "JOIN — об этом в разделе про соединения."))

    A(PageBreak())

    # --- 19 ---
    A(P("31. Функции SQL: func", "h1"))
    A(P("<font name='Mono' size='9'>func</font> — это мост к любым функциям базы. "
        "SQLAlchemy не держит их список: <font name='Mono' size='9'>func.что_угодно()</font> "
        "превращается в вызов <font name='Mono' size='9'>что_угодно()</font> в SQL. "
        "Поэтому доступны и стандартные функции, и специфичные для Postgres."))

    A(C("""
from sqlalchemy import func

func.count()          ->  count()
func.now()            ->  now()
func.coalesce(a, b)   ->  coalesce(a, b)
func.jsonb_agg(x)     ->  jsonb_agg(x)     — специфично для Postgres
"""))

    A(P("Агрегатные функции", "h2"))
    A(table([
        ["Функция", "Что делает", "Пример"],
        ["func.count()", "количество строк", "select(func.count()).select_from(Article)"],
        ["func.count(col)", "количество не-NULL значений", "func.count(Article.cover_image)"],
        ["func.count(distinct(col))", "количество уникальных", "func.count(distinct(Order.customer_id))"],
        ["func.sum(col)", "сумма", "func.sum(Order.sum_amount)"],
        ["func.avg(col)", "среднее", "func.avg(Article.views_count)"],
        ["func.min / func.max", "минимум и максимум", "func.max(Article.published_at)"],
    ], [46 * mm, 47 * mm, 72 * mm]))

    A(Spacer(1, 8))
    A(P("Работа с датой и временем", "h2"))
    A(table([
        ["Функция", "Что делает"],
        ["func.now()", "текущее время базы; для server_default"],
        ["func.current_date()", "сегодняшняя дата"],
        ["func.date_trunc('month', col)", "округление вниз: начало месяца, дня, часа"],
        ["func.extract('year', col)", "вытащить часть даты"],
        ["func.age(col)", "разница со текущим моментом (Postgres)"],
        ["func.to_char(col, 'DD.MM.YYYY')", "форматирование в строку (Postgres)"],
    ], [56 * mm, 109 * mm]))

    A(Spacer(1, 8))
    A(C("""
# статистика заявок по месяцам
stmt = (
    select(
        func.date_trunc("month", Request.created_at).label("month"),
        func.count().label("total"),
    )
    .group_by("month")
    .order_by("month")
)
""", "nedra: сколько заявок приходит каждый месяц"))

    A(P("Работа со строками", "h2"))
    A(table([
        ["Функция", "Что делает"],
        ["func.lower / func.upper", "регистр"],
        ["func.length(col)", "длина строки"],
        ["func.trim(col)", "убрать пробелы по краям"],
        ["func.concat(a, b)", "склеить (или оператор +)"],
        ["func.replace(col, a, b)", "заменить подстроку"],
        ["func.substr(col, 1, 100)", "часть строки"],
    ], [56 * mm, 109 * mm]))

    A(Spacer(1, 8))
    A(P("coalesce — подстановка значения вместо NULL", "h2"))
    A(C("""
# если описания нет, показать первые 200 символов текста
stmt = select(
    Article.title,
    func.coalesce(Article.description, func.substr(Article.content, 1, 200)),
)

# сумма по пустой выборке даёт NULL — превращаем в 0
total = await session.scalar(
    select(func.coalesce(func.sum(Order.sum_amount), 0))
)
"""))
    A(note("<b>Про <font name='Mono' size='9'>sum</font> и пустую выборку.</b> "
           "<font name='Mono' size='9'>COUNT</font> по нулю строк вернёт "
           "<font name='Mono' size='9'>0</font>, а <font name='Mono' size='9'>SUM</font> — "
           "<font name='Mono' size='9'>NULL</font>. В Python это станет "
           "<font name='Mono' size='9'>None</font>, и арифметика с ним упадёт. Оборачивайте "
           "суммы в <font name='Mono' size='9'>coalesce</font>."))

    A(P("Функции в выражениях колонок", "h2"))
    A(C("""
# инкремент средствами базы — атомарно
update(Article).values(views_count=Article.views_count + 1)

# нормализация при поиске
select(Account).where(func.lower(Account.email) == email.lower())
"""))
    A(P("Обратите внимание: <font name='Mono' size='9'>Article.views_count + 1</font> — "
        "это <b>SQL-выражение</b>, а не вычисление в Python. Значение читает и "
        "увеличивает сама база."))

    A(P("label — имя для вычисляемой колонки", "h2"))
    A(C("""
stmt = select(
    Tag.title,
    func.count(Article.id).label("articles_count"),
).join(Tag.articles).group_by(Tag.id)

for row in (await session.execute(stmt)).all():
    print(row.title, row.articles_count)   # обращение по метке
"""))

    A(PageBreak())

    # --- 20 ---
    A(P("32. Агрегация и группировка", "h1"))
    A(P("<font name='Mono' size='9'>GROUP BY</font> схлопывает строки в группы, а "
        "агрегатные функции считают по каждой группе."))

    A(C("""
# сколько заявок по каждому направлению
stmt = (
    select(
        Request.direction,
        func.count().label("total"),
    )
    .group_by(Request.direction)
    .order_by(func.count().desc())
)

rows = (await session.execute(stmt)).all()
# [(2, 47), (0, 31), (5, 12), ...]
""", "nedra: популярность направлений"))

    A(P("HAVING — фильтр по результату агрегации", "h2"))
    A(C("""
# теги, у которых больше 5 статей
stmt = (
    select(Tag.title, func.count(Article.id).label("cnt"))
    .join(Tag.articles)
    .group_by(Tag.id)
    .having(func.count(Article.id) > 5)
)
"""))
    A(note("<b>WHERE или HAVING.</b> <font name='Mono' size='9'>WHERE</font> отсеивает "
           "строки <b>до</b> группировки, <font name='Mono' size='9'>HAVING</font> — "
           "группы <b>после</b>. Условие по обычной колонке — в "
           "<font name='Mono' size='9'>WHERE</font> (так быстрее, строк меньше), условие "
           "по агрегату — только в <font name='Mono' size='9'>HAVING</font>."))

    A(C("""
stmt = (
    select(Tag.title, func.count(Article.id))
    .join(Tag.articles)
    .where(Article.published_at.is_not(None))   # до группировки
    .group_by(Tag.id)
    .having(func.count(Article.id) > 5)         # после
)
"""))

    A(P("Несколько агрегатов сразу", "h2"))
    A(C("""
stmt = select(
    func.count().label("total"),
    func.sum(Article.views_count).label("views"),
    func.avg(Article.likes_count).label("avg_likes"),
    func.max(Article.published_at).label("last_published"),
)

stats = (await session.execute(stmt)).one()
print(stats.total, stats.views, stats.avg_likes)
"""))

    A(P("Оконные функции", "h2"))
    A(P("Считают по группе, но <b>не схлопывают</b> строки — каждая строка остаётся и "
        "получает своё значение."))
    A(C("""
# место статьи по просмотрам внутри своего тега
stmt = select(
    Article.title,
    func.row_number().over(
        partition_by=Tag.id,
        order_by=Article.views_count.desc(),
    ).label("rank"),
).join(Article.tags)
"""))
    A(P("Полезные оконные функции: "
        "<font name='Mono' size='9'>row_number()</font> — порядковый номер, "
        "<font name='Mono' size='9'>rank()</font> — место с пропусками при равенстве, "
        "<font name='Mono' size='9'>lag() / lead()</font> — значение из соседней строки, "
        "<font name='Mono' size='9'>sum().over()</font> — нарастающий итог."))

    A(PageBreak())

    # --- 21 ---
    A(P("33. JOIN: соединение таблиц", "h1"))
    A(C("""
# по связи — SQLAlchemy сама знает условие
stmt = select(Article).join(Article.tags).where(Tag.slug == "npz")

# явно по таблице и условию
stmt = select(Order).join(Account, Order.customer_id == Account.id)

# LEFT JOIN — строки левой таблицы остаются, даже если справа ничего нет
stmt = select(Article).outerjoin(Article.tags)
"""))

    A(note("<b>Главная ловушка JOIN — дубли.</b> Если у статьи три тега, JOIN вернёт её "
           "трижды. Для фильтра «есть такой тег» это лишнее. Решения: "
           "<font name='Mono' size='9'>.distinct()</font>, либо — лучше — "
           "<font name='Mono' size='9'>.where(Article.tags.any(...))</font>, которое "
           "разворачивается в <font name='Mono' size='9'>EXISTS</font> и дублей не даёт."))

    A(C("""
# даёт дубли, если тегов несколько
select(Article).join(Article.tags).where(Tag.slug.in_(["a", "b"]))

# дублей нет
select(Article).where(Article.tags.any(Tag.slug.in_(["a", "b"])))
"""))

    A(P("JOIN не загружает связь", "h2"))
    A(C("""
stmt = (
    select(Article)
    .join(Article.tags)                       # для фильтрации
    .where(Tag.slug == "promyshlennost")
    .options(selectinload(Article.tags))      # для загрузки
)
"""))
    A(P("Это разные задачи. <font name='Mono' size='9'>join</font> позволяет написать "
        "условие по связанной таблице, но <b>не кладёт</b> теги в объекты. Без "
        "<font name='Mono' size='9'>options</font> обращение к "
        "<font name='Mono' size='9'>article.tags</font> вызовет ленивую загрузку — и "
        "падение в async."))

    # --- 22 ---
    A(P("34. Подзапросы, CTE и exists", "h1"))

    A(P("exists — есть ли хоть одна строка", "h2"))
    A(C("""
from sqlalchemy import exists

# аккаунты, у которых есть хотя бы один заказ
stmt = select(Account).where(
    exists().where(Order.customer_id == Account.id)
)

# проверка одной записи — дешевле, чем считать все
has_view = await session.scalar(
    select(exists().where(
        ArticleView.article_id == article_id,
        ArticleView.visitor_id == visitor_id,
    ))
)
"""))
    A(P("<font name='Mono' size='9'>EXISTS</font> останавливается на первой найденной "
        "строке, поэтому он всегда быстрее, чем "
        "<font name='Mono' size='9'>COUNT(*) > 0</font>."))

    A(P("Подзапрос", "h2"))
    A(C("""
# средние просмотры
avg_views = select(func.avg(Article.views_count)).scalar_subquery()

# статьи выше среднего
stmt = select(Article).where(Article.views_count > avg_views)
"""))

    A(P("CTE — именованный подзапрос", "h2"))
    A(C("""
# топ-10 статей по просмотрам, затем их теги
top = (
    select(Article.id, Article.title, Article.views_count)
    .order_by(Article.views_count.desc())
    .limit(10)
    .cte("top_articles")
)

stmt = (
    select(top.c.title, Tag.title)
    .join(article_tags, article_tags.c.article_id == top.c.id)
    .join(Tag, Tag.id == article_tags.c.tag_id)
)
"""))
    A(P("CTE читается сверху вниз и разбивает сложный запрос на понятные шаги. Обращение к "
        "колонкам — через <font name='Mono' size='9'>.c</font>: "
        "<font name='Mono' size='9'>top.c.title</font>."))

    A(PageBreak())

    # --- 23 ---
    A(P("35. Изменение данных", "h1"))

    A(P("Через объекты", "h2"))
    A(C("""
# вставка
article = Article(slug="npz", title="Мини-НПЗ", content="...")
session.add(article)
await session.commit()

# обновление — просто присваиваем
article.title = "Новый заголовок"
await session.commit()          # SQLAlchemy сама соберёт UPDATE

# удаление
await session.delete(article)
await session.commit()
"""))
    A(P("Отдельного «сохранить» нет: SQLAlchemy отслеживает изменения загруженных "
        "объектов и на <font name='Mono' size='9'>commit</font> собирает нужный SQL."))

    A(P("Массовые операции", "h2"))
    A(P("Когда объекты не нужны, работать напрямую запросом быстрее — не надо загружать "
        "строки в память."))
    A(C("""
from sqlalchemy import delete, insert, update

# атомарный инкремент
await session.execute(
    update(Article)
    .where(Article.id == article_id)
    .values(views_count=Article.views_count + 1)
)

# массовое обновление
await session.execute(
    update(Order)
    .where(Order.deadline < date.today())
    .values(status=OrderStatus.ARCHIVED)
)

# удаление по условию
await session.execute(delete(ArticleView).where(ArticleView.created_at < cutoff))

# вставка нескольких строк одним запросом
await session.execute(insert(Tag), [
    {"slug": "npz", "title": "Мини-НПЗ"},
    {"slug": "bpla", "title": "БПЛА"},
])
"""))

    A(note("<b>Массовые операции проходят мимо ORM.</b> Объекты, уже загруженные в сессию, "
           "об изменении не узнают, а <font name='Mono' size='9'>cascade</font> уровня ORM "
           "не сработает — каскадное удаление отработает только через "
           "<font name='Mono' size='9'>ondelete</font> в базе. Это плата за скорость."))

    A(P("UPSERT — вставить или обновить", "h2"))
    A(C("""
from sqlalchemy.dialects.postgresql import insert

# просмотр: если уже был, ничего не делаем
stmt = (
    insert(ArticleView)
    .values(article_id=article_id, visitor_id=visitor_id)
    .on_conflict_do_nothing(index_elements=["article_id", "visitor_id"])
)
result = await session.execute(stmt)

# сработала ли вставка — от этого зависит, увеличивать ли счётчик
if result.rowcount:
    await session.execute(
        update(Article)
        .where(Article.id == article_id)
        .values(views_count=Article.views_count + 1)
    )
""", "nedra: уникальный просмотр статьи"))

    A(C("""
# реакция: поставил лайк, потом передумал и жмёт дизлайк
stmt = (
    insert(ArticleReaction)
    .values(article_id=article_id, visitor_id=visitor_id, value=1)
    .on_conflict_do_update(
        index_elements=["article_id", "visitor_id"],
        set_={"value": 1},
    )
)
""", "nedra: смена реакции"))

    A(note("<b>Почему UPSERT, а не «проверить и вставить».</b> Между проверкой и вставкой "
           "успевает вклиниться второй запрос, и оба вставят строку. Уникальность "
           "гарантирует только ограничение <font name='Mono' size='9'>UNIQUE</font> в "
           "схеме плюс <font name='Mono' size='9'>ON CONFLICT</font>. Это не оптимизация, "
           "а корректность."))

    A(P("returning — получить данные изменённых строк", "h2"))
    A(C("""
stmt = (
    update(Article)
    .where(Article.id == article_id)
    .values(views_count=Article.views_count + 1)
    .returning(Article.views_count)
)
new_count = await session.scalar(stmt)   # актуальное значение без второго запроса
"""))

    A(PageBreak())

    # --- 24 ---
    A(P("36. Сессия: flush, commit, refresh", "h1"))
    A(P("Сессия — «черновик» изменений. Она копит их в памяти и решает, когда отправить в "
        "базу."))
    A(table([
        ["Метод", "Что делает"],
        ["add(obj)", "положить объект в сессию; SQL ещё не выполнялся"],
        ["flush()", "отправить SQL, но транзакцию не завершать; появляются id"],
        ["commit()", "зафиксировать транзакцию — данные видны всем"],
        ["rollback()", "откатить всё с начала транзакции"],
        ["refresh(obj)", "перечитать объект из базы"],
        ["expunge(obj)", "убрать объект из сессии, не удаляя из базы"],
        ["merge(obj)", "влить состояние отсоединённого объекта в сессию"],
    ], [30 * mm, 135 * mm]))

    A(Spacer(1, 8))
    A(C("""
async def create_request(self, data: RequestInSchema) -> Request:
    request = Request(name=data.name, email=data.email, ...)

    self.db.add(request)            # в сессии, в базе ещё нет
    await self.db.commit()          # INSERT выполнен, транзакция закрыта
    await self.db.refresh(request)  # подтянули id и created_at
    return request
""", "nedra: создание заявки"))

    A(P("Зачем refresh", "h2"))
    A(P("<font name='Mono' size='9'>id</font> генерирует база (автоинкремент), "
        "<font name='Mono' size='9'>created_at</font> тоже "
        "(<font name='Mono' size='9'>server_default</font>). До вставки этих значений в "
        "Python-объекте нет."))

    A(P("Зачем flush", "h2"))
    A(C("""
article = Article(title="...", slug="...")
self.db.add(article)
await self.db.flush()        # id появился, транзакция ещё открыта

for tag in tags:
    self.db.add(ArticleTag(article_id=article.id, tag_id=tag.id))

await self.db.commit()       # всё вместе одной транзакцией
"""))
    A(note("<b>Ключевая идея транзакции:</b> либо все изменения применятся, либо ни одного. "
           "Если между <font name='Mono' size='9'>flush</font> и "
           "<font name='Mono' size='9'>commit</font> произойдёт ошибка, статья тоже не "
           "сохранится. Именно поэтому связанные записи создают в одной транзакции, а не "
           "отдельными коммитами.", GOOD_BG))

    A(P("expire_on_commit=False", "h2"))
    A(C("""
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
"""))
    A(P("По умолчанию после <font name='Mono' size='9'>commit</font> SQLAlchemy помечает "
        "атрибуты устаревшими, и следующее обращение к ним лезет в базу. В async это даст "
        "<font name='Mono' size='9'>MissingGreenlet</font> при сборке ответа. Поэтому в "
        "async-проектах флаг ставят почти всегда."))

    A(P("Одна сессия на запрос", "h2"))
    A(C("""
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
""", "nedra/app/database.py"))
    A(P("Сессию открывает зависимость, а <font name='Mono' size='9'>commit</font> делает "
        "сервис — только он знает, где заканчивается бизнес-операция. При исключении "
        "внутри <font name='Mono' size='9'>async with</font> сессия закроется без "
        "commit, то есть транзакция откатится сама."))

    A(PageBreak())

    # ================= ЧАСТЬ IV =================
    A(P("Часть VII. Практика", "part"))

    # --- 25 ---
    A(P("46. Как проектировать схему", "h1"))
    A(P("Порядок действий, который экономит недели переделок."))

    A(P("Шаг 1. Выписать сущности и их поля", "h2"))
    A(P("Существительные из задачи: заявка, статья, тег, заказ, отклик. Для каждой — какие "
        "данные о ней нужны."))

    A(P("Шаг 2. Определить связи", "h2"))
    A(P("Для каждой пары сущностей задать вопрос с обеих сторон: сколько Б у одного А и "
        "сколько А у одного Б. Ответ даёт тип связи и место внешнего ключа."))

    A(P("Шаг 3. Выбрать типы", "h2"))
    A(B("Идентификаторы (ИНН, телефон, артикул) — строкой."))
    A(B("Деньги — <font name='Mono' size='9'>Numeric</font> или целое в копейках."))
    A(B("Длинный текст — <font name='Mono' size='9'>Text</font>."))
    A(B("Фиксированный набор — <font name='Mono' size='9'>Enum</font>."))
    A(B("Время — всегда с <font name='Mono' size='9'>timezone=True</font>."))

    A(P("Шаг 4. Расставить ограничения", "h2"))
    A(P("Что база <b>не должна</b> позволить записать? Каждое такое правило — "
        "<font name='Mono' size='9'>unique</font>, "
        "<font name='Mono' size='9'>CheckConstraint</font> или "
        "<font name='Mono' size='9'>NOT NULL</font>. Проверки в коде не заменяют "
        "ограничений в схеме: код можно обойти, схему — нет."))

    A(P("Шаг 5. Спланировать индексы", "h2"))
    A(P("Выписать запросы, которые будут выполняться часто, и посмотреть, по каким "
        "колонкам идёт фильтрация и сортировка. Внешние ключи индексировать почти всегда."))

    A(P("Шаг 6. Решить, что делать при удалении", "h2"))
    A(P("Для каждой связи: удалять детей "
        "(<font name='Mono' size='9'>CASCADE</font>), обнулять ссылку "
        "(<font name='Mono' size='9'>SET NULL</font>) или запрещать удаление "
        "(<font name='Mono' size='9'>RESTRICT</font>)."))

    A(Spacer(1, 6))
    A(note("<b>Денормализация — осознанное решение, а не небрежность.</b> Счётчики "
           "<font name='Mono' size='9'>views_count</font> и "
           "<font name='Mono' size='9'>likes_count</font> дублируют то, что можно "
           "посчитать запросом. Но список из 12 карточек потребовал бы 36 подзапросов "
           "<font name='Mono' size='9'>COUNT</font>. Держим агрегат в строке и обновляем "
           "его в той же транзакции, что и детальную запись. Правило: сначала нормальная "
           "схема, денормализация — когда измерили и увидели проблему.", GOOD_BG))

    # --- 26 ---
    A(P("47. Частые ошибки", "h1"))

    A(P("MissingGreenlet", "h2"))
    A(P("Обращение к незагруженной связи. Лечится "
        "<font name='Mono' size='9'>lazy=\"selectin\"</font> в модели или "
        "<font name='Mono' size='9'>selectinload</font> в запросе. Вторая причина — чтение "
        "атрибутов после <font name='Mono' size='9'>commit</font> без "
        "<font name='Mono' size='9'>expire_on_commit=False</font>."))

    A(P("Пустая миграция", "h2"))
    A(P("Модель не импортирована в <font name='Mono' size='9'>models/__init__.py</font>, "
        "значит её нет в <font name='Mono' size='9'>metadata</font>."))

    A(P("Колонка не появилась", "h2"))
    A(C("""
published_at: DateTime(timezone=True)                 # это не колонка
published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
"""))

    A(P("Потерянные обновления счётчика", "h2"))
    A(C("""
article.views_count = article.views_count + 1     # гонка
update(...).values(views_count=Article.views_count + 1)   # правильно
"""))

    A(P("Дубли при вставке под нагрузкой", "h2"))
    A(P("Проверка перед вставкой не защищает от гонок — нужен "
        "<font name='Mono' size='9'>UNIQUE</font> плюс "
        "<font name='Mono' size='9'>on_conflict_do_nothing</font>."))

    A(P("Дубли в выборке после JOIN", "h2"))
    A(P("У статьи несколько тегов — JOIN вернёт её несколько раз. Используйте "
        "<font name='Mono' size='9'>.any()</font> вместо "
        "<font name='Mono' size='9'>join</font> для фильтрации."))

    A(P("SUM вернул None", "h2"))
    A(P("Агрегат по пустой выборке даёт <font name='Mono' size='9'>NULL</font>. "
        "Оборачивайте в <font name='Mono' size='9'>func.coalesce(..., 0)</font>."))

    A(P("Запрос не изменился", "h2"))
    A(C("""
stmt.where(Article.published_at.is_not(None))     # результат выброшен
stmt = stmt.where(Article.published_at.is_not(None))   # правильно
"""))

    A(PageBreak())

    # --- 27 ---
    A(P("48. Шпаргалка", "h1"))

    A(P("Выбор связи", "h2"))
    A(C("""
один Б у А и один А у Б      ->  1:1   relationship(uselist=False)
                                       + unique=True на FK

много Б у А, один А у Б      ->  1:N   FK в таблице «многих»
                                       relationship(back_populates=...)

много Б у А и много А у Б    ->  M:N   Table(...) + secondary=...
                                       или association object,
                                       если у связи есть свои поля
"""))

    A(P("Обязательный минимум для async", "h2"))
    A(C("""
async_sessionmaker(engine, expire_on_commit=False)   # иначе падёт после commit
relationship(..., lazy="selectin")                   # иначе MissingGreenlet
ForeignKey(..., ondelete="CASCADE") + passive_deletes=True
mapped_column(ForeignKey(...), index=True)           # FK не индексируется сам
"""))

    A(P("Частые запросы", "h2"))
    A(C("""
await session.get(Model, pk)                      # по первичному ключу
select(M).where(M.f == v)                         # фильтр
select(M).where(M.rel.any(R.f == v))              # по связи, без дублей
select(M).options(selectinload(M.rel))            # загрузить связь
select(func.count()).select_from(M)               # количество
select(func.coalesce(func.sum(M.f), 0))           # сумма без None
update(M).where(...).values(f=M.f + 1)            # атомарный инкремент
insert(M).values(...).on_conflict_do_nothing()    # вставка без дублей
"""))

    A(P("Чек-лист модели", "h2"))
    A(B("Каждая колонка — <font name='Mono' size='9'>имя: Mapped[тип] = mapped_column(...)</font>"))
    A(B("Нет <font name='Mono' size='9'>index=True</font> на <font name='Mono' size='9'>primary_key</font>"))
    A(B("Нет дублирования <font name='Mono' size='9'>nullable</font> и аннотации"))
    A(B("У внешних ключей есть <font name='Mono' size='9'>index=True</font> и <font name='Mono' size='9'>ondelete</font>"))
    A(B("Идентификаторы (ИНН, телефон) — строками"))
    A(B("Длинный текст — <font name='Mono' size='9'>Text</font>"))
    A(B("Время — <font name='Mono' size='9'>DateTime(timezone=True)</font>"))
    A(B("Ограничения именованные (<font name='Mono' size='9'>name=</font>)"))
    A(B("Модель импортирована в <font name='Mono' size='9'>models/__init__.py</font>"))
    A(B("Класс в единственном числе, таблица во множественном"))

    A(Spacer(1, 8))
    A(note("<b>Проверка перед собеседованием.</b> Объясните вслух: чем "
           "<font name='Mono' size='9'>Mapped</font> отличается от "
           "<font name='Mono' size='9'>mapped_column</font>; почему для M:N нужна третья "
           "таблица; что такое N+1 и как его увидеть; чем "
           "<font name='Mono' size='9'>cascade</font> отличается от "
           "<font name='Mono' size='9'>ondelete</font>; зачем "
           "<font name='Mono' size='9'>flush</font>, если есть "
           "<font name='Mono' size='9'>commit</font>; почему проверка перед вставкой не "
           "защищает от дублей; когда <font name='Mono' size='9'>WHERE</font>, а когда "
           "<font name='Mono' size='9'>HAVING</font>.", GOOD_BG))

    return S
