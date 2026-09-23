"""Сводка по статьям на сервере: сколько залито и у скольких нет обложки.

Запускается после seed в деплое, чтобы результат был виден в логе CI
и не приходилось заходить на сервер руками.

Запуск:
  python scripts/news/report.py --api http://127.0.0.1:8000 --token <ADMIN_API_TOKEN>
"""

import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
PLAN_FILE = ROOT / "content" / "news" / "plan.json"


def load_articles(api: str, token: str) -> list[dict]:
    """Забрать список статей из админского эндпоинта."""

    request = Request(
        f"{api.rstrip('/')}/api/v1/admin/articles",
        headers={"X-Admin-Token": token},
    )

    with urlopen(request, timeout=120) as response:
        return json.loads(response.read())


def main() -> None:
    """Показать, сколько статей в базе, сколько без обложки и чего не хватает против плана."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--api", required=True, help="Адрес бэкенда")
    parser.add_argument("--token", required=True, help="ADMIN_API_TOKEN бэкенда")
    args = parser.parse_args()

    try:
        articles = load_articles(args.api, args.token)
    except (HTTPError, URLError) as error:
        print(f"Не удалось получить статьи: {error}")
        sys.exit(1)

    without_cover = [item["slug"] for item in articles if not item["cover_image"]]

    print(f"Статей в базе: {len(articles)}")
    print(f"Без обложки: {len(without_cover)}")

    if PLAN_FILE.exists():
        plan = json.loads(PLAN_FILE.read_text(encoding="utf-8"))
        known = {item["slug"] for item in articles}
        missing = [item["slug"] for item in plan if item["slug"] not in known]

        print(f"В плане: {len(plan)}, не залито: {len(missing)}")

        for slug in missing[:20]:
            print(f"  нет в базе: {slug}")

    for slug in without_cover[:20]:
        print(f"  без обложки: {slug}")


if __name__ == "__main__":
    main()
