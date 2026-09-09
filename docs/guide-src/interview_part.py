"""Часть VIII. Топ-50 вопросов с собеседований с примерами кода: глава 49."""


def mono(text):
    return f"<font name='Mono' size='9'>{text}</font>"


class Code(str):
    """Строка, которую надо отрисовать как блок кода, а не как абзац."""


def build(P, B, C, note, table, Spacer, PageBreak, mm, CODE_BG, GOOD_BG):
    S = []
    A = S.append
    m = mono

    def q(number, question, *parts, ref=None):
        title = f"{number}. {question}"
        if ref:
            title += f" <font color='#8a8f9c' size='9'>→ глава {ref}</font>"
        A(P(title, "h2"))
        for part in parts:
            if isinstance(part, Code):
                A(C(part))
            else:
                A(P(part))

    A(PageBreak())
    A(P("Часть VIII. Вопросы с собеседований", "part"))
    A(P("49. Топ-50 вопросов, коротких ответов и примеров", "h1"))
    A(P("Формат: вопрос, ответ на две-пять фраз, который можно произнести вслух, пример кода "
        "из проекта и ссылка на главу с подробностями. Отвечать заученно не нужно: интервьюер "
        "ждёт, что вы назовёте суть и покажете, где применили. Примеры здесь — из nedra, ими "
        "и пользуйтесь."))

    # ================= сервер и асинхронность =================
    A(P("Веб-сервер и асинхронность", "h1"))

    q(1, "Что такое WSGI и ASGI и чем они отличаются?",
      "Это два стандарта интерфейса между веб-сервером и Python-приложением. WSGI — "
      "синхронный: сервер вызывает функцию приложения, та возвращает ответ, один поток "
      "обслуживает один запрос; на нём Flask и классический Django. ASGI — асинхронный "
      "наследник: приложение — " + m("async") + "-функция, которая отдаёт управление на время "
      "ожидания, поэтому один процесс держит много запросов, плюс WebSocket. FastAPI — "
      "ASGI-приложение.",
      Code("""
# WSGI: одна функция, синхронно
def app(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"hello"]

# ASGI: корутина, три аргумента
async def app(scope, receive, send):
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"hello"})
"""), ref=37)

    q(2, "Зачем нужен uvicorn, если есть FastAPI?",
      "FastAPI — приложение: маршруты, валидация, зависимости. Слушать порт и разбирать HTTP "
      "оно не умеет, это делает ASGI-сервер uvicorn: принимает соединения, парсит запросы, "
      "вызывает приложение, отправляет ответы. Перед ним стоит nginx: TLS, статика, прокси.",
      Code("""
# docker-compose.yml, сервис backend
command: >
  sh -c "alembic upgrade head &&
         uvicorn app.main:app --host 0.0.0.0 --port 8000"

# app.main:app — путь к объекту FastAPI: модуль app/main.py, переменная app
"""))

    q(3, "Что такое event loop и что делает await?",
      "Event loop — цикл, который выполняет задачи в одном потоке по очереди. На "
      + m("await") + " операции ввода-вывода задача говорит «я жду», цикл переключается на "
      "другую; когда данные пришли, первая продолжается с того же места. Код между двумя "
      + m("await") + " выполняется без прерываний.",
      Code("""
import asyncio

async def fetch(name: str, seconds: float) -> str:
    await asyncio.sleep(seconds)        # здесь цикл занимается другими задачами
    return name

async def main() -> None:
    results = await asyncio.gather(fetch("a", 1), fetch("b", 1), fetch("c", 1))
    print(results)                      # ['a', 'b', 'c'] через ~1 секунду, а не 3

asyncio.run(main())
"""), ref=37)

    q(4, "Что такое GIL и почему асинхронность помогает, несмотря на него?",
      "GIL — глобальная блокировка интерпретатора: байткод Python в один момент выполняет "
      "один поток, поэтому потоки не ускоряют вычисления. Но бэкенд в основном ждёт базу и "
      "сеть, а во время ожидания GIL не нужен. Асинхронность заполняет паузы другой работой. "
      "Для процессорных задач нужны процессы.",
      Code("""
# ждёт сеть — асинхронность помогает
articles = await db.execute(select(Article))

# считает — GIL мешает, асинхронность не поможет
result = sum(i * i for i in range(50_000_000))
# выносить в процесс: ProcessPoolExecutor или отдельный воркер
"""))

    q(5, "Чем в FastAPI отличается ручка def от async def?",
      m("async def") + " выполняется в event loop, внутри можно только неблокирующие вызовы. "
      "Обычную " + m("def") + " FastAPI запускает в пуле потоков, чтобы она не останавливала "
      "цикл; там можно блокирующий код, но пул ограничен. Блокирующий вызов внутри "
      + m("async def") + " останавливает всё приложение.",
      Code("""
@router.get("/articles/{slug}")
async def get_article(slug: str, service: ArticleService = Depends(get_article_service)):
    article = await service.get_published(slug)     # asyncpg, не блокирует
    return ArticleSchema.model_validate(article)

@router.get("/report")
def build_report():                                 # без async: уйдёт в пул потоков
    return heavy_sync_library.render()              # блокирующий код здесь допустим
"""), ref=37)

    q(6, "Что случится, если внутри async def вызвать time.sleep(5)?",
      "Event loop заблокируется на пять секунд: другие запросы не обрабатываются, health "
      "check не отвечает. В асинхронном коде используют " + m("asyncio.sleep") + ", "
      "асинхронные драйверы, а тяжёлую синхронную работу выносят в пул потоков.",
      Code("""
import asyncio
from fastapi.concurrency import run_in_threadpool

async def handler():
    time.sleep(5)                                   # плохо: встал весь сервер
    await asyncio.sleep(5)                          # хорошо: ждём, не блокируя
    data = await run_in_threadpool(parse_big_pdf, path)   # синхронную функцию — в поток
"""))

    q(7, "Сколько воркеров uvicorn запускать?",
      "Один воркер — один процесс с одним event loop, одно ядро. Правило: число воркеров "
      "около числа ядер. У каждого свой пул соединений, поэтому суммарно "
      + m("workers × pool_size") + " не должно превышать лимит PostgreSQL, по умолчанию сто.",
      Code("""
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 4 воркера × pool_size 5 + max_overflow 10 = до 60 соединений
# PostgreSQL max_connections по умолчанию 100 — запас есть
"""), ref=37)

    q(8, "Зачем BackgroundTasks и чем они отличаются от Celery?",
      m("BackgroundTasks") + " выполняет функцию после отправки ответа, в том же процессе: "
      "быстро и без инфраструктуры, но без очереди и повторов. Celery — отдельные воркеры с "
      "брокером: надёжно, с повторами и расписанием, но сложнее. Начинают с первого.",
      Code("""
@router.post("/request", status_code=201)
async def create_request(
    payload: RequestCreateSchema,
    background: BackgroundTasks,
    service: RequestService = Depends(get_request_service),
) -> RequestOutSchema:
    request = await service.create(payload)
    background.add_task(send_request_email, request)   # клиент ответ уже получил
    return RequestOutSchema.model_validate(request)
"""))

    q(9, "Как работает Depends и когда вызываются зависимости?",
      "Перед ручкой FastAPI строит дерево зависимостей и вызывает каждую один раз на "
      "запрос, результат кэшируется. Зависимость с " + m("yield") + " получает «после»: код "
      "после " + m("yield") + " выполняется, когда ответ отправлен. Зависимости можно вешать "
      "на весь роутер.",
      Code("""
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session                     # ← ручка работает здесь
                                          # ← после ответа: сессия закрыта

router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
# каждая ручка роутера сначала пройдёт проверку токена
"""), ref=38)

    q(10, "Опишите путь запроса от браузера до базы в вашем проекте.",
      "Браузер → nginx (TLS, статика, " + m("/api/") + " проксируется) → uvicorn → FastAPI: "
      "роутер, валидация Pydantic, зависимости создают сессию и сервис → сервис строит "
      "запрос SQLAlchemy → asyncpg шлёт SQL в PostgreSQL → объекты модели → схема ответа → "
      "JSON. Для страниц сайта перед этим ещё Next.js, который ходит в тот же API с сервера.",
      Code("""
# deploy/nginx/nedra.conf
location /api/   { proxy_pass http://backend:8000; }
location /media/ { alias /var/www/media/; expires 30d; }
location /       { proxy_pass http://frontend:3000; }
"""), ref=38)

    # ================= PostgreSQL =================
    A(P("PostgreSQL", "h1"))

    q(11, "Расшифруйте ACID.",
      "Atomicity — целиком или откат. Consistency — после транзакции все ограничения "
      "выполнены. Isolation — параллельные транзакции не видят промежуточных состояний друг "
      "друга. Durability — после COMMIT данные не потеряются. Лайк у нас — вставка и "
      "увеличение счётчика в одной транзакции.",
      Code("""
BEGIN;
INSERT INTO article_reactions (article_id, visitor_id, value) VALUES (42, 'x', 1);
UPDATE articles SET likes_count = likes_count + 1 WHERE id = 42;
COMMIT;   -- обе строки видны одновременно; упало посередине — не видна ни одна
"""), ref=11)

    q(12, "Какие уровни изоляции есть и какой по умолчанию?",
      "Read Committed (по умолчанию): каждый запрос видит закоммиченное к его началу. "
      "Repeatable Read: снимок на момент начала транзакции. Serializable: как будто по "
      "очереди, при конфликте откат. Read Uncommitted в PostgreSQL ведёт себя как Read "
      "Committed. Чем строже, тем больше откатов.",
      Code("""
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT sum(likes_count) FROM articles;   -- оба SELECT увидят один снимок,
SELECT count(*) FROM article_reactions;  -- даже если параллельно кто-то коммитит
COMMIT;
"""), ref=11)

    q(13, "Что такое MVCC?",
      "Multi-Version Concurrency Control: UPDATE не перезаписывает строку, а создаёт новую "
      "версию; старую видят транзакции, начавшиеся раньше. Читатели не блокируют писателей. "
      "Плата — мёртвые версии, которые убирает VACUUM.",
      Code("""
-- скрытые системные колонки показывают версии строк
SELECT xmin, xmax, id, likes_count FROM articles WHERE id = 42;
-- xmin: транзакция, создавшая версию; xmax: транзакция, её удалившая (0 — живая)
"""), ref=12)

    q(14, "Что такое грязное, неповторяющееся и фантомное чтение?",
      "Грязное — увидеть незакоммиченное; в PostgreSQL невозможно. Неповторяющееся — одна "
      "строка дважды прочитана с разными значениями внутри транзакции; возможно на Read "
      "Committed. Фантомное — повторный запрос по условию вернул другое число строк. "
      "Repeatable Read закрывает оба последних.",
      Code("""
-- сессия 1 (Read Committed)            -- сессия 2
BEGIN;
SELECT likes_count FROM articles
WHERE id = 42;               -- 10
                                          UPDATE articles SET likes_count = 11 WHERE id = 42;
                                          COMMIT;
SELECT likes_count FROM articles
WHERE id = 42;               -- 11  ← неповторяющееся чтение
COMMIT;
"""), ref=11)

    q(15, "Что такое дедлок и как его избежать?",
      "Две транзакции ждут друг друга: первая держит строку A и хочет B, вторая наоборот. "
      "PostgreSQL находит цикл и откатывает одну. Профилактика: обновлять строки в одном "
      "порядке, держать транзакции короткими, не делать сетевых вызовов внутри.",
      Code("""
-- сессия 1                               -- сессия 2
UPDATE articles SET ... WHERE id = 1;     UPDATE articles SET ... WHERE id = 2;
UPDATE articles SET ... WHERE id = 2;     UPDATE articles SET ... WHERE id = 1;
-- ждёт сессию 2                          -- ждёт сессию 1 → ERROR: deadlock detected

-- лечение: всегда в порядке возрастания id
UPDATE articles SET ... WHERE id IN (1, 2) ORDER BY id;  -- или два UPDATE по порядку
"""), ref=11)

    q(16, "Какие типы индексов есть в PostgreSQL?",
      "B-tree по умолчанию: равенство, диапазоны, сортировка. Hash — только равенство. GIN — "
      "«содержит»: JSONB, массивы, полнотекст. GiST — геометрия, диапазоны. BRIN — огромные "
      "таблицы с естественным порядком. Плюс уникальные, составные, частичные и "
      "функциональные.",
      Code("""
CREATE INDEX ix_articles_published_at ON articles (published_at);            -- B-tree
CREATE INDEX ix_articles_toc ON articles USING GIN (toc);                     -- JSONB
CREATE UNIQUE INDEX uq_tags_slug ON tags (slug);                              -- уникальный
CREATE INDEX ix_articles_live ON articles (published_at) WHERE published_at IS NOT NULL;  -- частичный
CREATE INDEX ix_articles_title_lower ON articles (lower(title));              -- функциональный
"""), ref=5)

    q(17, "Когда индекс не используется, хотя он есть?",
      "Маленькая таблица — перебор дешевле. Условие не совпадает с индексом: процент в начале "
      "LIKE, функция над колонкой без функционального индекса, приведение типа. Составной "
      "индекс начинается не с той колонки. Низкая селективность. Проверка — EXPLAIN.",
      Code("""
WHERE title LIKE '%надзор%'        -- индекс по title бесполезен: неизвестно начало
WHERE lower(title) = 'ovos'        -- нужен индекс по lower(title)
WHERE published_at::date = '2026-09-07'   -- приведение ломает индекс по published_at
WHERE published_at >= '2026-09-07' AND published_at < '2026-09-08'   -- так индекс работает
"""), ref=5)

    q(18, "Как выбрать порядок колонок в составном индексе?",
      "Сначала колонки с равенством, потом колонка диапазона или сортировки. Индекс по "
      "(a, b) работает для запросов по a, но не только по b.",
      Code("""
-- запрос
SELECT * FROM articles
WHERE section = 'news' AND published_at <= now()
ORDER BY published_at DESC LIMIT 12;

CREATE INDEX ix_articles_section_published ON articles (section, published_at DESC);
-- равенство по section → блок раздела, внутри уже отсортировано по дате
"""), ref=5)

    q(19, "Как читать EXPLAIN ANALYZE?",
      "Снизу вверх, изнутри наружу. Смотрим тип узла (Seq Scan, Index Scan, Hash Join), "
      "оценку строк против фактической и время. Большое расхождение — устаревшая статистика, "
      "нужен ANALYZE. Для UPDATE оборачивать в транзакцию с ROLLBACK.",
      Code("""
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM articles WHERE section = 'news' ORDER BY published_at DESC LIMIT 12;

Limit (actual time=0.05..0.09 rows=12)
  -> Index Scan Backward using ix_articles_published_at on articles
       Filter: (section = 'news')
       Rows Removed by Filter: 2          ← сколько прочитали зря
"""), ref=5)

    q(20, "Что такое нормализация и когда её нарушают?",
      "Каждый факт хранится один раз: название тега в " + m("tags") + ", связь в "
      + m("article_tags") + ". 1НФ — нет списков в ячейке, 2НФ — нет зависимостей от части "
      "ключа, 3НФ — нет зависимостей между неключевыми колонками. Нарушают ради скорости "
      "чтения: наши счётчики — денормализация.",
      Code("""
-- нарушение 1НФ: список в ячейке, не поискать и не проверить
tags TEXT  -- 'промбез, экология, опо'

-- нормально: промежуточная таблица
CREATE TABLE article_tags (
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    tag_id     INTEGER REFERENCES tags(id)     ON DELETE CASCADE,
    PRIMARY KEY (article_id, tag_id)
);

-- осознанная денормализация: счётчик вместо count(*) по реакциям на каждый показ
likes_count INTEGER NOT NULL DEFAULT 0
"""), ref=4)

    q(21, "Чем PRIMARY KEY отличается от UNIQUE?",
      "Оба гарантируют уникальность и создают индекс. Первичный ключ один, не допускает NULL "
      "и идентифицирует строку, на него ссылаются внешние ключи. UNIQUE-ограничений много, и "
      "NULL там допускается сколько угодно раз.",
      Code("""
CREATE TABLE articles (
    id   SERIAL PRIMARY KEY,               -- один, NOT NULL, цель внешних ключей
    slug VARCHAR(255) NOT NULL UNIQUE,     -- второй уникальный признак
    ...
);
INSERT INTO tags (slug, title) VALUES (NULL, 'a'), (NULL, 'b');  -- UNIQUE пропустит оба NULL
"""), ref=4)

    q(22, "Что делает внешний ключ и какие варианты ON DELETE бывают?",
      "Гарантирует, что ссылка указывает на существующую строку, и задаёт поведение при "
      "удалении родителя: RESTRICT, CASCADE, SET NULL, SET DEFAULT. Индекс на колонку "
      "внешнего ключа надо создавать вручную.",
      Code("""
article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE
-- удалили статью → её реакции и просмотры исчезли

executor_id INTEGER REFERENCES users(id) ON DELETE SET NULL
-- удалили пользователя → заказ остался без исполнителя

INSERT INTO article_tags VALUES (999, 1);
-- ERROR: violates foreign key constraint — статьи 999 нет
"""), ref=4)

    q(23, "Что такое VACUUM и зачем он нужен?",
      "После UPDATE и DELETE остаются мёртвые версии строк (MVCC). VACUUM освобождает их "
      "место для повторного использования и обновляет статистику планировщика. Autovacuum "
      "делает это сам. VACUUM FULL сжимает файл, но блокирует таблицу.",
      Code("""
VACUUM ANALYZE articles;              -- убрать мёртвые версии, обновить статистику

SELECT relname, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;             -- где накопился мусор
"""), ref=12)

    q(24, "Когда хранить данные в JSONB, а когда в отдельной таблице?",
      "JSONB — для переменной структуры, которая читается целиком и на которую не ссылаются: "
      "оглавление, настройки, сырой ответ API. Таблица — когда нужно искать, соединять, "
      "агрегировать, ограничивать уникальность и ссылаться внешними ключами.",
      Code("""
-- оглавление: читается целиком вместе со статьёй → JSONB
toc JSONB   -- [{"id": "chto-menyaetsya", "title": "Что меняется"}, ...]

SELECT title FROM articles WHERE toc @> '[{"id": "riski"}]';      -- поиск по GIN-индексу
SELECT title, toc->0->>'title' AS first_h2 FROM articles;          -- достать поле

-- теги: нужны фильтр, уникальность, каскад → таблица, не JSONB
"""), ref=3)

    q(25, "Чем timestamp отличается от timestamptz?",
      m("timestamp") + " хранит настенное время без пояса. " + m("timestamptz") + " — момент "
      "времени, внутри UTC, при показе переводится в пояс сессии. Правило: всегда "
      "timestamptz, в SQLAlchemy " + m("DateTime(timezone=True)") + ".",
      Code("""
SELECT '2026-09-07 09:00+07'::timestamptz;   -- 2026-09-07 02:00:00+00 в сессии UTC
SET TIME ZONE 'Asia/Novosibirsk';
SELECT '2026-09-07 09:00+07'::timestamptz;   -- 2026-09-07 09:00:00+07 — то же значение

published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
"""), ref=3)

    q(26, "Как делаются бэкапы PostgreSQL?",
      m("pg_dump") + " — логический дамп в SQL, просто восстанавливается. Физический бэкап "
      "плюс архив WAL даёт восстановление на любой момент времени. Репликация — копия на "
      "другом сервере для отказоустойчивости, бэкап не заменяет.",
      Code("""
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean' \\
  > backup-$(date +%F).sql

docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < backup-2026-09-09.sql
"""), ref=12)

    # ================= SQL =================
    A(P("SQL", "h1"))

    q(27, "Какие виды JOIN бывают?",
      "INNER — только совпавшие пары. LEFT — все строки слева, справа NULL без пары. RIGHT — "
      "зеркально. FULL — всё с обеих сторон. CROSS — каждая с каждой.",
      Code("""
-- статьи с числом тегов, включая статьи без тегов
SELECT a.slug, count(at.tag_id) AS tags_count
FROM articles a
LEFT JOIN article_tags at ON at.article_id = a.id
GROUP BY a.id, a.slug;

-- с INNER JOIN статьи без тегов пропали бы
"""), ref=7)

    q(28, "Чем WHERE отличается от HAVING?",
      "WHERE фильтрует строки до группировки и не видит агрегатов. HAVING фильтрует группы "
      "после GROUP BY. Что можно выразить в WHERE — туда: меньше строк дойдёт до группировки.",
      Code("""
SELECT t.title, count(*) AS articles
FROM tags t
JOIN article_tags at ON at.tag_id = t.id
JOIN articles a      ON a.id = at.article_id
WHERE a.published_at <= now()          -- до группировки: только опубликованные
GROUP BY t.id, t.title
HAVING count(*) >= 5                   -- после: только популярные теги
ORDER BY articles DESC;
"""), ref=8)

    q(29, "В чём разница между count(*), count(колонка) и count(DISTINCT)?",
      m("count(*)") + " — строки. " + m("count(колонка)") + " — строки, где колонка не NULL. "
      + m("count(DISTINCT колонка)") + " — число разных значений.",
      Code("""
SELECT
    count(*)                      AS total,          -- 100
    count(cover_image)            AS with_cover,     -- 100 (NULL не считается)
    count(DISTINCT section)       AS sections,       -- 2
    count(*) FILTER (WHERE published_at > now()) AS scheduled
FROM articles;
"""), ref=8)

    q(30, "Подзапрос, JOIN или EXISTS — что выбрать?",
      "Нужны колонки второй таблицы — JOIN. Нужно только проверить наличие — EXISTS: "
      "останавливается на первой строке и не размножает результат. IN читается проще, но на "
      "больших списках медленнее.",
      Code("""
-- SQL
SELECT slug FROM articles a
WHERE EXISTS (SELECT 1 FROM article_tags at JOIN tags t ON t.id = at.tag_id
              WHERE at.article_id = a.id AND t.slug = 'ekologiya');

# SQLAlchemy: то же самое одной строкой
stmt = select(Article).where(Article.tags.any(Tag.slug == tag_slug))
"""), ref=9)

    q(31, "Что такое оконные функции?",
      "Считают значение по группе строк, не сворачивая их: каждая строка остаётся, рядом "
      "появляется " + m("row_number()") + ", " + m("sum() OVER") + ", " + m("lag()") + ". "
      + m("PARTITION BY") + " делит на группы, " + m("ORDER BY") + " задаёт порядок внутри окна.",
      Code("""
SELECT slug, section, views_count,
       row_number() OVER (PARTITION BY section ORDER BY views_count DESC) AS place,
       sum(views_count) OVER (PARTITION BY section) AS section_views
FROM articles;

# SQLAlchemy
from sqlalchemy import func, over
place = func.row_number().over(partition_by=Article.section, order_by=Article.views_count.desc())
stmt = select(Article.slug, place.label("place"))
"""), ref=9)

    q(32, "Как сделать «вставить или обновить» одним запросом?",
      m("INSERT ... ON CONFLICT (колонки) DO UPDATE") + " или " + m("DO NOTHING") + ". "
      "Конфликт определяется по уникальному ограничению. Атомарно, снимает гонку "
      "«проверил — вставил».",
      Code("""
INSERT INTO article_reactions (article_id, visitor_id, value)
VALUES (42, 'x', 1)
ON CONFLICT (article_id, visitor_id) DO UPDATE SET value = EXCLUDED.value;

# SQLAlchemy: диалектный insert
from sqlalchemy.dialects.postgresql import insert

stmt = insert(ArticleReaction).values(article_id=42, visitor_id="x", value=1)
stmt = stmt.on_conflict_do_update(
    index_elements=[ArticleReaction.article_id, ArticleReaction.visitor_id],
    set_={"value": stmt.excluded.value},
)
await db.execute(stmt)
"""), ref=10)

    # ================= SQLAlchemy =================
    A(P("SQLAlchemy", "h1"))

    q(33, "Что такое Core и ORM в SQLAlchemy?",
      "Core — конструктор SQL: " + m("select") + ", " + m("Table") + ", результат — строки. "
      "ORM надстроен над Core: классы-модели, объекты, сессия с identity map и unit of work. В "
      "2.0 у них один язык запросов.",
      Code("""
# Core: таблица без класса, результат — строки
article_tags = Table("article_tags", Base.metadata, Column(...), Column(...))
rows = await db.execute(select(article_tags.c.tag_id).where(article_tags.c.article_id == 42))

# ORM: класс, результат — объекты
class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)

tags = (await db.execute(select(Tag))).scalars().all()
"""), ref=13)

    q(34, "Engine, Connection, Session — кто за что отвечает?",
      "Engine — один на приложение: URL, диалект, пул. Connection — одно соединение из пула, "
      "уровень Core. Session — рабочее пространство ORM: берёт соединение, ведёт транзакцию, "
      "хранит объекты.",
      Code("""
engine = create_async_engine(settings.database_url, pool_pre_ping=True)   # один раз
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async with SessionLocal() as db:            # сессия на запрос
    article = await db.get(Article, 42)     # соединение взято из пула здесь

async with engine.connect() as conn:        # чистый Core без ORM, редко
    await conn.execute(text("SELECT 1"))
"""), ref=37)

    q(35, "Что такое identity map?",
      "Словарь «первичный ключ → объект» внутри сессии: одна строка — один объект Python. "
      "Повторный " + m("get") + " не ходит в базу. Отсюда ловушка: после commit объект в карте "
      "остался, а вычисленные базой колонки протухли.",
      Code("""
first = await db.get(Article, 42)
second = await db.get(Article, 42)
assert first is second                      # тот же объект, второго запроса не было

await db.commit()
again = await db.get(Article, 42)           # снова тот же объект, updated_at устарел
stmt = select(Article).where(Article.id == 42).execution_options(populate_existing=True)
fresh = (await db.execute(stmt)).scalar_one()   # перечитали и перезаписали объект
"""), ref=38)

    q(36, "Чем flush отличается от commit?",
      m("flush") + " отправляет накопленные изменения в базу внутри открытой транзакции: "
      "появляется id, ловится IntegrityError. " + m("commit") + " делает flush и фиксирует "
      "транзакцию.",
      Code("""
self.db.add(ArticleView(article_id=article.id, visitor_id=visitor_id))

try:
    await self.db.flush()                  # INSERT ушёл; дубль по первичному ключу упадёт здесь
except IntegrityError:
    await self.db.rollback()
    return                                 # просмотр уже учтён параллельным запросом

await self.db.execute(update(Article).where(Article.id == article.id)
                      .values(views_count=Article.views_count + 1))
await self.db.commit()                     # оба изменения зафиксированы вместе
"""), ref=38)

    q(37, "Что такое expire_on_commit и почему в async его выключают?",
      "После commit сессия по умолчанию помечает атрибуты устаревшими, следующее обращение "
      "делает запрос. В async обращение к атрибуту — не await, запрос невозможен → "
      "MissingGreenlet. Поэтому " + m("expire_on_commit=False") + ", а вычисленные базой "
      "колонки перечитываем явно.",
      Code("""
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

await db.commit()
print(article.title)        # ок: атрибут не протух
print(article.updated_at)   # onupdate=func.now() — значение знает только база → reload()
"""), ref=38)

    q(38, "Что такое N+1 и как его увидеть?",
      "Загрузили N статей одним запросом, потом для каждой обратились к связи — ещё N "
      "запросов. Видно через " + m("echo=True") + ": десятки одинаковых SELECT. Лечится "
      "стратегией загрузки.",
      Code("""
# плохо: 1 запрос за статьями + по запросу на теги каждой
articles = (await db.execute(select(Article))).scalars().all()
for article in articles:
    print(article.tags)       # в async это ещё и MissingGreenlet

# хорошо: теги одним дополнительным запросом
stmt = select(Article).options(selectinload(Article.tags))
# или раз и навсегда в модели:
tags: Mapped[list["Tag"]] = relationship(secondary=article_tags, lazy="selectin")
"""), ref=27)

    q(39, "selectinload или joinedload?",
      m("joinedload") + " — один запрос с JOIN, хорош для связей «к одному». "
      + m("selectinload") + " — второй запрос по списку id, лучше для коллекций: строки не "
      "дублируются. В async ленивой загрузки нет, стратегию задают явно.",
      Code("""
-- selectinload: два запроса
SELECT * FROM articles WHERE ... LIMIT 12;
SELECT * FROM article_tags JOIN tags ... WHERE article_tags.article_id IN (1, 2, ..., 12);

-- joinedload: один запрос, строки статей повторяются по числу тегов
SELECT articles.*, tags.* FROM articles LEFT JOIN article_tags ... LEFT JOIN tags ...;

# к одному — joinedload
stmt = select(Order).options(joinedload(Order.customer))
"""), ref=27)

    q(40, "Чем cascade у relationship отличается от ondelete у ForeignKey?",
      m("ondelete='CASCADE'") + " — правило базы, работает при любом удалении и одним "
      "запросом. " + m("cascade='all, delete-orphan'") + " — правило ORM: только при удалении "
      "через сессию и только для загруженных объектов. Надёжнее полагаться на базу.",
      Code("""
# база: сработает даже из psql
article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"))

# ORM: сессия сама удалит детей, если удаляем через неё
items: Mapped[list["Item"]] = relationship(cascade="all, delete-orphan")

await db.delete(article)      # ORM удалит статью; связи снесёт база каскадом
await db.commit()
"""), ref=28)

    q(41, "Почему сессия создаётся на каждый запрос, а не одна на приложение?",
      "Сессия — это транзакция и состояние объектов. Общая сессия смешала бы данные разных "
      "пользователей, не потокобезопасна, копила бы объекты и держала транзакцию вечно. "
      "Сессия на запрос даёт изоляцию и автоматическую уборку.",
      Code("""
# плохо
db = SessionLocal()                     # одна на модуль

# хорошо: зависимость с yield
async def get_session():
    async with SessionLocal() as session:
        yield session

def get_article_service(session: AsyncSession = Depends(get_session)) -> ArticleService:
    return ArticleService(session)
"""), ref=38)

    q(42, "Как подобрать размер пула соединений?",
      "Столько, сколько запросов реально ждут базу одновременно, обычно 5–20 на воркер. "
      "Больше — не быстрее: PostgreSQL ограничен ядрами и " + m("max_connections") + ". "
      "Считать суммарно по воркерам и сервисам.",
      Code("""
engine = create_async_engine(
    url,
    pool_size=5,          # постоянные
    max_overflow=10,      # временные под пик
    pool_pre_ping=True,   # проверять живость перед выдачей
    pool_recycle=1800,    # пересоздавать старые
)
# симптом нехватки: sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached
"""), ref=37)

    q(43, "Когда лучше написать сырой SQL вместо ORM?",
      "Сложная аналитика с окнами и CTE, массовые обновления, диалектные возможности. Через "
      + m("text()") + " с параметрами, а не f-строками — иначе SQL-инъекция.",
      Code("""
from sqlalchemy import text

stmt = text(\"\"\"
    WITH scheduled AS (
        SELECT id, row_number() OVER (ORDER BY published_at) AS n
        FROM articles WHERE section = :section AND published_at > now()
    )
    UPDATE articles a SET published_at = :start - scheduled.n * interval '1 day'
    FROM scheduled WHERE a.id = scheduled.id
\"\"\")
await db.execute(stmt, {"section": "news", "start": start})   # параметры, не f-строка
"""), ref=31)

    q(44, "Зачем миграции, если есть create_all? Что не умеет autogenerate?",
      m("create_all") + " только создаёт отсутствующие таблицы и не меняет существующие. "
      "Миграции — версионированные шаги с откатом. Autogenerate не видит переименований, не "
      "всегда видит смену типа и default, не пишет миграции данных.",
      Code("""
def upgrade() -> None:
    op.add_column("articles",
        sa.Column("section", sa.String(16), nullable=False, server_default="blog"))
    op.create_index("ix_articles_section", "articles", ["section"])

def downgrade() -> None:
    op.drop_index("ix_articles_section", table_name="articles")
    op.drop_column("articles", "section")

# server_default обязателен: в таблице уже 100 строк, NOT NULL без него упадёт
"""), ref=43)

    q(45, "Что такое Mapped и mapped_column и как определяется nullable?",
      m("Mapped[T]") + " — аннотация: тип и обязательность. " + m("Mapped[str]") + " даёт NOT "
      "NULL, " + m("Mapped[str | None]") + " разрешает NULL. " + m("mapped_column") + " добавляет "
      "то, чего нет в типе: длину, индекс, default, внешний ключ.",
      Code("""
title: Mapped[str] = mapped_column(String(255))                 # NOT NULL
description: Mapped[str | None] = mapped_column(String(400))    # NULL разрешён
views_count: Mapped[int] = mapped_column(Integer, default=0)    # default в Python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now()          # default в базе
)
"""), ref=14)

    # ================= архитектура =================
    A(P("Архитектура", "h1"))

    q(46, "Зачем слой сервисов между роутером и моделями?",
      "Роутер отвечает за HTTP, сервис — за данные и правила. Логику можно вызвать из "
      "скриптов и тестов без HTTP, роутеры короткие, зависимости идут в одну сторону: "
      "роутеры → сервисы → модели.",
      Code("""
# сервис: не знает про HTTP
async def get_published(self, slug: str) -> Article:
    result = await self.db.execute(select(Article).where(Article.slug == slug, PUBLISHED))
    article = result.scalar_one_or_none()
    if article is None:
        raise ArticleNotFoundError(f"Статья «{slug}» не найдена")
    return article

# роутер: только HTTP
try:
    article = await service.get_published(slug)
except ArticleNotFoundError as error:
    raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
"""), ref=38)

    q(47, "Где ловить ошибки и как превращать их в HTTP-ответы?",
      "Сервис бросает доменные исключения, роутер переводит их в HTTPException с кодом. "
      "Валидацию входа делает Pydantic (422). Непредвиденные исключения не ловим — пусть "
      "будет 500 с записью в лог.",
      Code("""
# services/exceptions.py
class ArticleNotFoundError(LookupError):
    \"\"\"Статья не найдена или не опубликована.\"\"\"

class UploadError(ValueError):
    \"\"\"Файл не подходит: неверный тип или превышен размер.\"\"\"

# роутер
except UploadError as error:
    raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error
"""), ref=39)

    q(48, "Зачем ограничения в базе, если есть валидация Pydantic?",
      "Pydantic защищает вход API. База защищает данные от всех источников: миграций, "
      "скриптов, ручных правок, будущего кода. Только база гарантирует уникальность при "
      "параллельных запросах.",
      Code("""
# вход API
class ReactionInSchema(BaseModel):
    value: Literal[1, -1]

# данные
class ArticleReaction(Base):
    value: Mapped[int] = mapped_column(SmallInteger)
    __table_args__ = (CheckConstraint("value IN (-1, 1)", name="ck_article_reactions_value"),)
"""), ref=4)

    q(49, "Как бороться с гонками при параллельных запросах?",
      "Не проверять «есть ли уже» в коде, а полагаться на уникальный ключ и ловить "
      "IntegrityError или ON CONFLICT. Счётчики менять выражением в базе. Транзакции короткие. "
      "Операции идемпотентные.",
      Code("""
# плохо: между чтением и записью другой запрос успеет
article.views_count = article.views_count + 1

# хорошо: арифметика в базе под блокировкой строки
await db.execute(
    update(Article).where(Article.id == article_id)
    .values(views_count=Article.views_count + 1)
)
# идемпотентность: повторный лайк тем же значением ничего не меняет
if reaction is not None and reaction.value == value:
    return
"""), ref=11)

    q(50, "Как вы проектируете схему под новую функцию?",
      "Сущности и связи словами → для каждой колонки тип, обязательность, уникальность, "
      "ограничения, индексы под известные запросы → правила удаления → модель → миграция → "
      "сервис → схемы API → тест. Раздел «Новости» потребовал одну колонку, а не вторую "
      "таблицу.",
      Code("""
# 1. модель
section: Mapped[str] = mapped_column(String(16), default="blog", server_default="blog", index=True)
# 2. миграция 0004: add_column + create_index
# 3. сервис: фильтр
if section:
    stmt = stmt.where(Article.section == section)
# 4. API: Query-параметр с Literal
section: Section | None = Query(None)
# 5. тест
r = client.get("/api/v1/articles?section=news")
assert all(a["section"] == "news" for a in r.json()["articles"])
"""), ref=46)

    A(Spacer(1, 8))
    A(note("<b>Как готовиться.</b> Не зубрите ответы. По каждому вопросу откройте место в "
           "своём коде, где это применено, и объясните вслух, почему сделано именно так. "
           "Интервьюер почти всегда уходит с вопроса на проект: «а у вас как?» — и это лучший "
           "момент собеседования.", GOOD_BG))

    return S
