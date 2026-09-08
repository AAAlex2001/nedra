"""Загрузка новостей из content/news/articles в бэкенд через админское API.

Работает на чистой стандартной библиотеке, поэтому запускается и на сервере
внутри контейнера бэкенда. По умолчанию создаёт только те статьи, которых
ещё нет в базе, и не трогает существующие: правки, сделанные в админке,
не затираются. С флагом --update существующие статьи перезаписываются
из файлов.

Все новые статьи публикуются сразу: даты расставляются назад от вчерашнего
дня по рабочим дням, по --per-week штук в неделю, в 09:00 по Новосибирску.
Первая статья в плане получает самую свежую дату.

Запуск:
  python scripts/news/seed.py --api https://nedra-npi.ru --token <ADMIN_API_TOKEN>
  python scripts/news/seed.py --api http://localhost:8000 --token test --dry-run
"""

import argparse
import json
import re
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = ROOT / "content" / "news"
ARTICLES_DIR = CONTENT_DIR / "articles"
PLAN_FILE = CONTENT_DIR / "plan.json"
CREDITS_FILE = CONTENT_DIR / "covers.json"

NOVOSIBIRSK = timezone(timedelta(hours=7))
PUBLISH_TIME = time(9, 0)

TRUSTED_SUFFIXES = (
    ".gov.ru", "government.ru", "kremlin.ru", "consultant.ru", "garant.ru",
    "regulation.gov.ru", "pravo.gov.ru", "duma.gov.ru", "council.gov.ru",
    "eaeunion.org", "eec.eaeunion.org", "tpprf.ru", "rosatom.ru", "nostroy.ru",
    "nopriz.ru", "docs.cntd.ru", "meganorm.ru", "gosuslugi.ru", "wikimedia.org",
    "flickr.com", "openverse.org", "rawpixel.com", "nedra-npi.ru",
    "tass.ru", "ria.ru", "rg.ru", "interfax.ru", "kommersant.ru", "vedomosti.ru",
    "rbc.ru", "iz.ru", "lenta.ru", "gazeta.ru", "pnp.ru", "ancb.ru", "erzrf.ru",
    "1tv.ru", "reo.ru", "gost.ru", "secnrs.ru",
)

LINK_PATTERN = re.compile(r"<a\s+[^>]*href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>", re.S)


def load_json(path: Path) -> dict | list:
    """Прочитать JSON-файл в кодировке UTF-8. Табуляции внутри строк не считаются ошибкой."""

    return json.loads(path.read_text(encoding="utf-8"), strict=False)


def is_trusted(url: str) -> bool:
    """Ссылка ведёт на официальный источник, СМИ или фотобанк, а не на сайт конкурента."""

    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]

    return any(host == suffix.lstrip(".") or host.endswith(suffix) for suffix in TRUSTED_SUFFIXES)


def clean_links(html: str) -> str:
    """Убрать ссылки на посторонние коммерческие сайты, оставив текст ссылки."""

    def replace(match: re.Match) -> str:
        url = match.group(1)
        text = match.group(2)

        if is_trusted(url):
            return match.group(0)

        return text

    return LINK_PATTERN.sub(replace, html)


def build_schedule(count: int, start: date, per_week: int) -> list[datetime]:
    """Даты публикации в прошлом: от вчерашнего дня назад по рабочим дням, per_week штук в неделю."""

    dates: list[datetime] = []

    day = start
    published_this_week = 0
    current_week = day.isocalendar()[1]

    while len(dates) < count:
        day -= timedelta(days=1)

        week = day.isocalendar()[1]
        if week != current_week:
            current_week = week
            published_this_week = 0

        is_weekend = day.weekday() >= 5
        if is_weekend or published_this_week >= per_week:
            continue

        dates.append(datetime.combine(day, PUBLISH_TIME, NOVOSIBIRSK))
        published_this_week += 1

    return dates


def credit_paragraph(credit: dict | None) -> str:
    """HTML-подпись к обложке с автором и лицензией."""

    if credit is None:
        return ""

    provider_names = {"flickr": "Flickr", "wikimedia": "Wikimedia Commons", "rawpixel": "Rawpixel"}
    provider = provider_names.get(credit.get("provider", ""), "Openverse")
    author = credit.get("author") or provider
    source = credit.get("source") or ""
    license_name = credit.get("license") or ""

    parts = [f"Фото: {author}"]
    if source:
        parts.append(f'<a href="{source}">{provider}</a>')
    if license_name:
        parts.append(license_name)

    return f"<p><em>{', '.join(parts)}</em></p>"


class AdminApi:
    """Тонкая обёртка над админскими ручками бэкенда на urllib."""

    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url.rstrip("/") + "/api/v1/admin"
        self.token = token

    def call(self, method: str, path: str, payload: dict | None = None) -> list | dict | None:
        """Выполнить запрос к админке и вернуть разобранный JSON."""

        body = None
        headers = {"X-Admin-Token": self.token, "Accept": "application/json"}

        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(self.base_url + path, data=body, method=method, headers=headers)

        try:
            with urlopen(request, timeout=120) as response:
                raw = response.read()
        except HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"{method} {path}: {error.code} {details}") from error
        except URLError as error:
            raise RuntimeError(f"{method} {path}: {error.reason}") from error

        if not raw:
            return None

        return json.loads(raw.decode("utf-8"))

    def get(self, path: str) -> list | dict:
        """GET-запрос к админке."""

        return self.call("GET", path)

    def post(self, path: str, payload: dict) -> dict:
        """POST-запрос к админке."""

        return self.call("POST", path, payload)

    def patch(self, path: str, payload: dict) -> dict:
        """PATCH-запрос к админке."""

        return self.call("PATCH", path, payload)


def ensure_tags(api: AdminApi, titles: set[str], dry_run: bool) -> dict[str, int]:
    """Вернуть словарь «название тега → id», создав недостающие теги."""

    existing = api.get("/tags")
    by_title = {tag["title"]: tag["id"] for tag in existing}

    for title in sorted(titles):
        if title in by_title:
            continue

        if dry_run:
            print(f"  [dry-run] создать тег «{title}»")
            by_title[title] = 0
            continue

        created = api.post("/tags", {"title": title})
        by_title[title] = created["id"]
        print(f"  создан тег «{title}»")

    return by_title


def load_articles(plan: list[dict]) -> list[dict]:
    """Статьи из content/news/articles в порядке плана; отсутствующие пропускаются."""

    articles = []
    missing = 0

    for item in plan:
        path = ARTICLES_DIR / f"{item['slug']}.json"
        if not path.exists():
            missing += 1
            continue

        articles.append(load_json(path))

    print(f"Статей в файлах: {len(articles)} из {len(plan)} по плану, ещё не написано: {missing}")

    return articles


def build_payload(article: dict, tag_ids: dict[str, int], credits: dict, published_at: datetime) -> dict:
    """Собрать тело запроса на создание или обновление статьи."""

    slug = article["slug"]
    credit = credits.get(slug)

    cover_image = None
    if credit is not None:
        cover_image = f"/news/{slug}.jpg"

    return {
        "title": article["title"],
        "slug": slug,
        "section": "news",
        "description": article["description"],
        "cover_image": cover_image,
        "content": clean_links(article["content"]) + credit_paragraph(credit),
        "tag_ids": [tag_ids[tag] for tag in article["tags"]],
        "published_at": published_at.isoformat(),
        "seo_title": article.get("seo_title"),
        "seo_description": article.get("seo_description"),
        "seo_keywords": article.get("seo_keywords"),
    }


def main() -> None:
    """Прочитать статьи, расставить даты и отправить новые в бэкенд."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--api", required=True, help="Адрес сайта или бэкенда, например https://nedra-npi.ru")
    parser.add_argument("--token", required=True, help="ADMIN_API_TOKEN бэкенда")
    parser.add_argument("--start", default=date.today().isoformat(), help="Дата отсчёта, ГГГГ-ММ-ДД; даты идут назад от неё")
    parser.add_argument("--per-week", type=int, default=5, help="Сколько статей приходится на одну неделю в прошлом")
    parser.add_argument("--update", action="store_true", help="Перезаписать и уже существующие статьи")
    parser.add_argument("--dry-run", action="store_true", help="Только показать, ничего не отправлять")
    args = parser.parse_args()

    plan = load_json(PLAN_FILE)
    credits = load_json(CREDITS_FILE) if CREDITS_FILE.exists() else {}
    articles = load_articles(plan)

    api = AdminApi(args.api, args.token)
    tag_ids = ensure_tags(api, {tag for article in articles for tag in article["tags"]}, args.dry_run)

    existing = api.get("/articles?section=news")
    existing_by_slug = {article["slug"]: article for article in existing}

    new_articles = [article for article in articles if article["slug"] not in existing_by_slug]
    schedule = build_schedule(len(new_articles), date.fromisoformat(args.start), args.per_week)

    created = 0
    for article, published_at in zip(new_articles, schedule):
        payload = build_payload(article, tag_ids, credits, published_at)
        when = published_at.strftime("%d.%m.%Y %H:%M")

        if args.dry_run:
            print(f"  [dry-run] создать {article['slug']} → {when}")
            continue

        api.post("/articles", payload)
        created += 1
        print(f"  создана {article['slug']} → {when}")

    updated = 0
    if args.update:
        for article in articles:
            current = existing_by_slug.get(article["slug"])
            if current is None:
                continue

            published_at = datetime.fromisoformat(current["published_at"]) if current["published_at"] else datetime.now(NOVOSIBIRSK)
            payload = build_payload(article, tag_ids, credits, published_at)

            if args.dry_run:
                print(f"  [dry-run] обновить {article['slug']}")
                continue

            api.patch(f"/articles/{current['id']}", payload)
            updated += 1
            print(f"  обновлена {article['slug']}")

    skipped = len(articles) - len(new_articles) - updated
    print(f"\nГотово: создано {created}, обновлено {updated}, оставлено без изменений {skipped}")


if __name__ == "__main__":
    main()
