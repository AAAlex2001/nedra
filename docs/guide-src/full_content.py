"""Полное руководство PostgreSQL + SQLAlchemy: обложка, содержание и сборка частей."""

import alembic_part
import engine_part
import pg_part
import sa_body


def build(P, B, C, note, table, Spacer, PageBreak, mm, CODE_BG, GOOD_BG):
    S = []
    A = S.append

    A(Spacer(1, 30 * mm))
    A(P("PostgreSQL и SQLAlchemy 2.0", "title"))
    A(P("Полное руководство: как устроена база, как её описать в Python, как хранить, "
        "связывать, запрашивать и мигрировать данные.<br/>Все примеры — рабочий код проекта "
        "nedra.", "subtitle"))
    A(Spacer(1, 4 * mm))
    A(note("<b>Как читать.</b> Часть I — сама база: типы, ограничения, индексы, SQL. Части "
           "II–IV — SQLAlchemy: модели, связи, запросы. Часть V — движок, сессии и стык с "
           "FastAPI. Часть VI — миграции Alembic и тесты. Часть VII — практика и шпаргалка. "
           "Каждый импорт объясняется в месте первого использования, а глава 39 собирает их "
           "в одну карту.", CODE_BG))
    A(Spacer(1, 5 * mm))
    A(P("Содержание", "h2"))

    toc = [
        ("Часть I. PostgreSQL", None),
        (None, "Что такое СУБД и зачем нам PostgreSQL"),
        (None, "Как поднять PostgreSQL и подключиться"),
        (None, "Таблицы и типы данных"),
        (None, "Ограничения: как база защищает данные"),
        (None, "Индексы: как база ищет быстро"),
        (None, "SELECT: читаем данные"),
        (None, "JOIN: соединяем таблицы"),
        (None, "Агрегаты и группировка"),
        (None, "Подзапросы, CTE и оконные функции"),
        (None, "INSERT, UPDATE, DELETE"),
        (None, "Транзакции"),
        (None, "Эксплуатация: бэкапы, роли, часовые пояса"),
        ("Часть II. Основы SQLAlchemy", None),
        (None, "Что такое ORM и зачем он нужен"),
        (None, "Три кирпича: Base, Mapped, mapped_column"),
        (None, "metadata — реестр схемы"),
        (None, "Типы колонок"),
        (None, "Параметры колонок: default, server_default, onupdate"),
        (None, "Ограничения и индексы: __table_args__"),
        (None, "Enum в моделях"),
        (None, "Миксины: переиспользование колонок"),
        ("Часть III. Связи", None),
        (None, "Как понять, какая связь нужна"),
        (None, "Один ко многим (1:N)"),
        (None, "Один к одному (1:1)"),
        (None, "Многие ко многим (M:N)"),
        (None, "Промежуточная таблица: Table или модель"),
        (None, "Параметры relationship"),
        (None, "Загрузка данных: lazy, N+1 и async"),
        (None, "Удаление: cascade и ondelete"),
        ("Часть IV. Запросы", None),
        (None, "select: основы"),
        (None, "Операторы и условия"),
        (None, "Функции SQL: func"),
        (None, "Агрегация и группировка"),
        (None, "JOIN: соединение таблиц"),
        (None, "Подзапросы, CTE и exists"),
        (None, "Изменение данных: insert, update, delete, UPSERT"),
        (None, "Сессия: flush, commit, refresh"),
        ("Часть V. Движок, сессии и FastAPI", None),
        (None, "Engine: соединения, пул и async"),
        (None, "Сессия: жизненный цикл, identity map, expire_on_commit"),
        (None, "Карта импортов: что откуда и почему"),
        ("Часть VI. Миграции Alembic", None),
        (None, "Зачем миграции и как Alembic устроен"),
        (None, "Настройка: alembic.ini и env.py"),
        (None, "Пишем миграцию руками"),
        (None, "Autogenerate и alembic check"),
        (None, "Эксплуатация миграций"),
        (None, "Тестирование: SQLite, TestClient и подмена сессии"),
        ("Часть VII. Практика", None),
        (None, "Как проектировать схему"),
        (None, "Частые ошибки"),
        (None, "Шпаргалка"),
    ]
    number = 0
    for part, name in toc:
        if part:
            A(Spacer(1, 4))
            A(P(f"<b>{part}</b>", "toc"))
        else:
            number += 1
            A(P(f"{number}.&nbsp;&nbsp;{name}", "toc"))

    A(PageBreak())

    args = (P, B, C, note, table, Spacer, PageBreak, mm, CODE_BG, GOOD_BG)

    S.extend(pg_part.build(*args))

    body = sa_body.build(*args)
    split = next(
        index for index, flowable in enumerate(body)
        if getattr(flowable, "text", "").startswith("Часть VII")
    )
    S.extend(body[:split])
    S.extend(engine_part.build(*args))
    S.extend(alembic_part.build(*args))
    S.extend(body[split:])

    return S
