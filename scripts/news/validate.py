"""Проверка статей в content/news/articles перед загрузкой.

Смотрит, что у каждой темы из плана есть файл, JSON валиден, поля заполнены,
длины в норме, HTML содержит только разрешённые теги, есть заголовки H2,
ссылки на источники и упоминание института.

Запуск: python scripts/news/validate.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = ROOT / "content" / "news"
ARTICLES_DIR = CONTENT_DIR / "articles"
PLAN_FILE = CONTENT_DIR / "plan.json"

ALLOWED_TAGS = {
    "p", "h2", "h3", "ul", "ol", "li", "strong", "em", "a",
    "blockquote", "table", "thead", "tbody", "tr", "th", "td", "br",
}
REQUIRED = ("slug", "title", "description", "seo_title", "seo_description", "seo_keywords", "tags", "content")

MIN_WORDS = 650
MAX_WORDS = 1700


def word_count(html: str) -> int:
    """Количество слов в тексте без тегов."""

    text = re.sub(r"<[^>]+>", " ", html)

    return len(re.findall(r"\w+", text))


def check_article(article: dict, plan_item: dict) -> list[str]:
    """Вернуть список проблем статьи; пустой список — статья в порядке."""

    problems = []

    for field in REQUIRED:
        if not article.get(field):
            problems.append(f"пустое поле {field}")

    if problems:
        return problems

    if article["slug"] != plan_item["slug"]:
        problems.append("slug не совпадает с планом")

    if article.get("section") != "news":
        problems.append("section должен быть news")

    if article["tags"] != [plan_item["direction"]]:
        problems.append(f"tags должны быть [{plan_item['direction']!r}]")

    if not 40 <= len(article["title"]) <= 120:
        problems.append(f"title {len(article['title'])} символов")

    if not 100 <= len(article["description"]) <= 400:
        problems.append(f"description {len(article['description'])} символов")

    if len(article["seo_title"]) > 80:
        problems.append(f"seo_title {len(article['seo_title'])} символов")

    if not 90 <= len(article["seo_description"]) <= 200:
        problems.append(f"seo_description {len(article['seo_description'])} символов")

    content = article["content"]

    used_tags = {tag.lower() for tag in re.findall(r"</?([a-zA-Z][a-zA-Z0-9]*)", content)}
    forbidden = used_tags - ALLOWED_TAGS
    if forbidden:
        problems.append(f"запрещённые теги: {', '.join(sorted(forbidden))}")

    if re.search(r"\s(style|class|onclick)=", content):
        problems.append("есть атрибуты style/class/onclick")

    h2_count = len(re.findall(r"<h2[\s>]", content))
    if h2_count < 3:
        problems.append(f"мало разделов H2: {h2_count}")

    words = word_count(content)
    if not MIN_WORDS <= words <= MAX_WORDS:
        problems.append(f"объём {words} слов")

    if "<a " not in content:
        problems.append("нет ни одной ссылки на источник")

    if "Недра" not in content:
        problems.append("нет упоминания НПИ «Недра»")

    if "<h1" in content or "<img" in content:
        problems.append("есть h1 или img")

    return problems


def main() -> None:
    """Проверить все статьи из плана и вывести отчёт."""

    plan = json.loads(PLAN_FILE.read_text(encoding="utf-8"))

    missing = []
    broken = {}
    ok = 0

    for item in plan:
        path = ARTICLES_DIR / f"{item['slug']}.json"

        if not path.exists():
            missing.append(item["slug"])
            continue

        try:
            article = json.loads(path.read_text(encoding="utf-8"), strict=False)
        except json.JSONDecodeError as error:
            broken[item["slug"]] = [f"невалидный JSON: {error}"]
            continue

        problems = check_article(article, item)
        if problems:
            broken[item["slug"]] = problems
        else:
            ok += 1

    print(f"В порядке: {ok}, с замечаниями: {len(broken)}, отсутствуют: {len(missing)}")

    for slug, problems in broken.items():
        print(f"\n{slug}")
        for problem in problems:
            print(f"  - {problem}")

    if missing:
        print("\nНет файлов:")
        print("\n".join(f"  {slug}" for slug in missing))

    if broken or missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
