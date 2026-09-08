"""Подбор обложек для новостей из свободных фотобанков.

Сначала ищет в Openverse (Flickr и другие источники под CC0, Public domain,
CC BY, CC BY-SA), если не нашлось — в Wikimedia Commons. Картинка обрезается
до 1200×675 и сохраняется в frontend/public/news/<slug>.jpg. Автор, источник
и лицензия пишутся в content/news/covers.json для подписи под фото.

Запуск: python scripts/news/fetch_covers.py [--plan content/news/plan.json]
"""

import argparse
import io
import json
import re
import sys
import time
from pathlib import Path

import requests
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DIR = ROOT / "frontend" / "public" / "news"
CREDITS_FILE = ROOT / "content" / "news" / "covers.json"

OPENVERSE_API = "https://api.openverse.org/v1/images/"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "nedra-news-covers/1.0 (https://nedra-npi.ru; site editor)"}

COVER_WIDTH = 1200
COVER_HEIGHT = 675
MIN_SOURCE_WIDTH = 900
MIN_YEAR = 2000
MIN_SATURATION = 12
MAX_CANDIDATES_TO_TRY = 4

OPENVERSE_LICENSES = {
    "cc0": ("CC0", 0),
    "pdm": ("Public domain", 0),
    "by": ("CC BY", 2),
    "by-sa": ("CC BY-SA", 4),
}

COMMONS_LICENSES = {
    "public domain": 0,
    "pd": 0,
    "cc0": 0,
    "cc by 4.0": 2,
    "cc by 3.0": 2,
    "cc by 2.5": 2,
    "cc by 2.0": 2,
    "cc by-sa 4.0": 4,
    "cc by-sa 3.0": 4,
    "cc by-sa 2.5": 4,
    "cc by-sa 2.0": 4,
}

STOP_WORDS = (
    "navy", "army", "air force", "marine", "usmc", "soldier", "military", "usace",
    "corps", "award", "ceremony", "statelib", "bundesarchiv", "library of congress",
    "postcard", "painting", "drawing", "map", "logo", "diagram", "screenshot",
    "panorama", "360", "poly haven", "flag", "coat of arms", "rescue", "dog", "cat",
    "fountain", "space", "iss ", "shuttle", "astronaut", "aircraft", "jet", "nail",
    "mosque", "children", "kids", "porsche", "car ", "deal", "portrait", "toilet",
    "hand", "speaker", "conference", "meeting of", "visit", "tag!", "you're it",
)

STOP_AUTHORS = ("usdagov", "dvidshub", "nasa", "u.s. army", "u.s. navy", "defence images")

CODED_TITLE = re.compile(r"^\d{6,}[-_ ]")

FALLBACK_QUERIES = {
    "Проектирование и инженерные изыскания": ["construction site cranes", "engineers blueprint hard hats", "soil drilling rig"],
    "Научно-техническое сопровождение": ["high-rise construction site", "construction engineers inspection", "concrete formwork"],
    "Промышленная безопасность": ["chemical plant pipelines", "oil refinery towers", "industrial boiler", "gas plant valves"],
    "Объекты культурного наследия": ["historic building restoration scaffolding", "old church facade restoration", "historic monument"],
    "Экологическое проектирование": ["factory smokestacks", "wastewater treatment plant", "landfill excavator", "industrial river pollution"],
    "Сертификация": ["industrial valves pipes", "pressure vessel", "electrical switchgear"],
    "Научно-испытательная лаборатория": ["materials testing laboratory", "chemistry laboratory glassware", "concrete testing"],
    "Образовательная деятельность": ["industrial safety training", "engineers meeting hard hats", "workers helmets factory"],
    "Атомная лицензия": ["nuclear power plant cooling tower", "nuclear power station", "nuclear reactor hall"],
}


def strip_html(text: str) -> str:
    """Убрать теги из HTML-строки метаданных."""

    return re.sub(r"<[^>]+>", "", text).strip()


def has_stop_word(title: str, author: str = "") -> bool:
    """Проверить, нет ли в названии или авторе признаков, по которым картинка точно не подходит."""

    lowered = title.lower()
    if any(word in lowered for word in STOP_WORDS):
        return True

    if CODED_TITLE.match(title):
        return True

    lowered_author = author.lower()

    return any(word in lowered_author for word in STOP_AUTHORS)


def good_shape(width: int, height: int) -> bool:
    """Горизонтальная картинка достаточного размера."""

    if width < MIN_SOURCE_WIDTH or height == 0:
        return False

    ratio = width / height

    return 1.2 <= ratio <= 1.9


def search_openverse(query: str) -> list[dict]:
    """Кандидаты из Openverse, отсортированные по релевантности с поправкой на лицензию."""

    params = {
        "q": query,
        "license": ",".join(OPENVERSE_LICENSES),
        "page_size": 20,
        "mature": "false",
    }

    response = requests.get(OPENVERSE_API, params=params, headers=HEADERS, timeout=60)
    if response.status_code == 429:
        print("    Openverse: лимит запросов, пауза 60 секунд")
        time.sleep(60)
        response = requests.get(OPENVERSE_API, params=params, headers=HEADERS, timeout=60)
    response.raise_for_status()

    candidates = []
    seen_titles = set()

    for index, item in enumerate(response.json().get("results", [])):
        title = item.get("title") or ""
        author = item.get("creator") or ""
        if title in seen_titles or has_stop_word(title, author):
            continue

        if not good_shape(item.get("width") or 0, item.get("height") or 0):
            continue

        license_code = item.get("license", "")
        if license_code not in OPENVERSE_LICENSES:
            continue

        license_name, penalty = OPENVERSE_LICENSES[license_code]
        version = item.get("license_version") or ""
        if penalty and version:
            license_name = f"{license_name} {version}"

        seen_titles.add(title)
        candidates.append(
            {
                "score": index + penalty,
                "title": title,
                "url": item["url"],
                "source": item.get("foreign_landing_url") or item["url"],
                "author": item.get("creator") or "",
                "license": license_name,
                "license_url": item.get("license_url") or "",
                "provider": item.get("source") or "openverse",
            }
        )

    candidates.sort(key=lambda candidate: candidate["score"])

    return candidates


def photo_year(meta: dict) -> int | None:
    """Год съёмки из метаданных Commons, если он указан."""

    raw = meta.get("DateTimeOriginal", {}).get("value", "")
    match = re.search(r"(1[89]\d\d|20\d\d)", raw)

    if match is None:
        return None

    return int(match.group(1))


def search_commons(query: str) -> list[dict]:
    """Кандидаты из Wikimedia Commons, отсортированные так же, как в Openverse."""

    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": f"{query} filetype:bitmap",
        "gsrnamespace": 6,
        "gsrlimit": 50,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": 1600,
        "format": "json",
    }

    response = requests.get(COMMONS_API, params=params, headers=HEADERS, timeout=60)
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", {}).values()

    candidates = []

    for page in pages:
        title = page.get("title", "")
        if has_stop_word(title):
            continue

        infos = page.get("imageinfo") or []
        if not infos:
            continue

        info = infos[0]
        if info.get("mime") not in ("image/jpeg", "image/png"):
            continue

        if not good_shape(info.get("width", 0), info.get("height", 0)):
            continue

        meta = info.get("extmetadata", {})
        author = strip_html(meta.get("Artist", {}).get("value", ""))
        if has_stop_word("", author):
            continue

        short_name = meta.get("LicenseShortName", {}).get("value", "")
        penalty = COMMONS_LICENSES.get(short_name.strip().lower())
        if penalty is None:
            continue

        year = photo_year(meta)
        if year is not None and year < MIN_YEAR:
            continue

        candidates.append(
            {
                "score": page.get("index", 50) + penalty,
                "title": title,
                "url": info.get("thumburl") or info.get("url"),
                "source": info.get("descriptionurl"),
                "author": author,
                "license": short_name,
                "license_url": meta.get("LicenseUrl", {}).get("value", ""),
                "provider": "wikimedia",
            }
        )

    candidates.sort(key=lambda candidate: candidate["score"])

    return candidates


def is_colorful(image: Image.Image) -> bool:
    """Отсеять чёрно-белые и почти монохромные снимки."""

    small = image.resize((200, 112)).convert("HSV")
    saturation = ImageStat.Stat(small).mean[1]

    return saturation >= MIN_SATURATION


def download_cover(url: str, target: Path) -> bool:
    """Скачать картинку, проверить цветность, обрезать до 1200×675 и сохранить как JPEG."""

    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()

    image = Image.open(io.BytesIO(response.content)).convert("RGB")
    if not is_colorful(image):
        return False

    source_width, source_height = image.size

    target_ratio = COVER_WIDTH / COVER_HEIGHT
    source_ratio = source_width / source_height

    if source_ratio > target_ratio:
        crop_width = int(source_height * target_ratio)
        left = (source_width - crop_width) // 2
        box = (left, 0, left + crop_width, source_height)
    else:
        crop_height = int(source_width / target_ratio)
        top = (source_height - crop_height) // 2
        box = (0, top, source_width, top + crop_height)

    cover = image.crop(box).resize((COVER_WIDTH, COVER_HEIGHT), Image.LANCZOS)
    cover.save(target, "JPEG", quality=82, optimize=True, progressive=True)

    return True


def find_cover(queries: list[str], used_urls: set[str], target: Path) -> dict | None:
    """Перебрать источники, запросы и кандидатов, пока картинка не скачается и не пройдёт проверку."""

    for search in (search_openverse, search_commons):
        for query in queries:
            if not query:
                continue

            try:
                candidates = search(query)
            except requests.RequestException as error:
                print(f"    {search.__name__} «{query}»: {error}")
                continue

            fresh = [candidate for candidate in candidates if candidate["url"] not in used_urls]

            for candidate in fresh[:MAX_CANDIDATES_TO_TRY]:
                try:
                    saved = download_cover(candidate["url"], target)
                except (requests.RequestException, OSError) as error:
                    print(f"    не скачалась {candidate['title'][:60]}: {error}")
                    continue

                if saved:
                    return candidate

            time.sleep(3)

    return None


def load_credits() -> dict:
    """Прочитать уже собранные подписи, чтобы не скачивать обложки повторно."""

    if CREDITS_FILE.exists():
        return json.loads(CREDITS_FILE.read_text(encoding="utf-8"))

    return {}


def main() -> None:
    """Пройти по плану и подобрать обложку каждой статье без обложки."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", default=str(ROOT / "content" / "news" / "plan.json"))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--overrides",
        default="",
        help="JSON со своими запросами: slug → список запросов. Обложки этих статей подбираются заново",
    )
    args = parser.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    if args.limit:
        plan = plan[: args.limit]

    overrides = {}
    if args.overrides:
        overrides = json.loads(Path(args.overrides).read_text(encoding="utf-8"))

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    CREDITS_FILE.parent.mkdir(parents=True, exist_ok=True)

    credits = load_credits()

    for slug in overrides:
        credits.pop(slug, None)

    used_urls = {item["url"] for item in credits.values()}

    for index, item in enumerate(plan, start=1):
        slug = item["slug"]
        target = PUBLIC_DIR / f"{slug}.jpg"

        if slug in credits and target.exists():
            print(f"[{index}/{len(plan)}] {slug}: уже есть")
            continue

        queries = overrides.get(slug, [item.get("cover_query", "")])
        queries = queries + FALLBACK_QUERIES.get(item.get("direction", ""), [])
        chosen = find_cover(queries, used_urls, target)

        if chosen is None:
            print(f"[{index}/{len(plan)}] {slug}: обложка не найдена")
            continue

        used_urls.add(chosen["url"])
        credits[slug] = {
            "title": chosen["title"],
            "url": chosen["url"],
            "source": chosen["source"],
            "author": chosen["author"],
            "license": chosen["license"],
            "license_url": chosen["license_url"],
            "provider": chosen["provider"],
        }
        CREDITS_FILE.write_text(
            json.dumps(credits, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        print(f"[{index}/{len(plan)}] {slug}: {chosen['provider']}, {chosen['license']} — {chosen['title'][:70]}")
        time.sleep(3)

    missing = [item["slug"] for item in plan if item["slug"] not in credits]
    print(f"\nГотово: {len(plan) - len(missing)} обложек, без обложки: {len(missing)}")
    if missing:
        print("\n".join(missing))
        sys.exit(1)


if __name__ == "__main__":
    main()
