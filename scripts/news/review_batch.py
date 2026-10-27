"""Проверка новой редакционной пачки перед включением в основной план."""

import argparse
import collections
import hashlib
import html
import json
import re
from pathlib import Path

from PIL import Image

from validate import check_article, word_count

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "content/news"


def normalized(value):
    return " ".join(re.findall(r"[а-яёa-z0-9]+", html.unescape(re.sub(r"<[^>]+>", " ", value)).lower()))


def shingles(value):
    tokens = normalized(value).split()
    return {hashlib.blake2b(" ".join(tokens[i:i+5]).encode(), digest_size=8).digest()
            for i in range(len(tokens) - 4)}


def review(batch):
    plan = json.loads((batch / "plan.json").read_text(encoding="utf-8"))
    credits = json.loads((CONTENT / "covers.json").read_text(encoding="utf-8"))
    errors, unfinished, articles = [], [], []
    paragraphs = collections.defaultdict(list)
    sources, image_hashes, title_values, descriptions = [], [], [], []
    for index, item in enumerate(plan):
        path = CONTENT / "articles" / f"{item['slug']}.json"
        try:
            article = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append({"index": index, "error": type(error).__name__})
            continue
        if "Материал посвящён документальной проверке конкретной ситуации." in article["content"]:
            unfinished.append(index)
            continue
        problems = check_article(article, item)
        if re.search(r"\?{3,}|\ufffd", article["content"]):
            problems.append("повреждённая кодировка или подстановочный текст")
        if problems:
            errors.append({"index": index, "problems": problems})
        for paragraph in re.findall(r"<p>(.*?)</p>", article["content"], re.S):
            value = normalized(paragraph)
            if len(value) >= 180:
                paragraphs[value].append(index)
        articles.append((index, article))
        title_values.append(normalized(article["title"]))
        descriptions.append(normalized(article["seo_description"]))
        cover = credits.get(item["slug"], {})
        source = cover.get("source")
        image_path = ROOT / "frontend/public/news" / f"{item['slug']}.jpg"
        if not cover.get("new_source") or not source or not cover.get("license_url"):
            errors.append({"index": index, "error": "нет нового источника/лицензии обложки"})
        if not cover.get("visual_reviewed"):
            errors.append({"index": index, "error": "обложка не прошла визуальный отбор"})
        if image_path.exists():
            image_hashes.append(hashlib.sha256(image_path.read_bytes()).hexdigest())
            with Image.open(image_path) as image:
                if image.size != (1200, 675):
                    errors.append({"index": index, "error": "размер обложки отличается от1200×675"})
        else:
            errors.append({"index": index, "error": "нет файла обложки"})
        sources.append(source)

    repeated = [{"indices": indices, "paragraph": value[:220]}
                for value, indices in paragraphs.items() if len(set(indices)) > 1]
    fingerprints = [(index, shingles(article["content"])) for index, article in articles]
    similar = []
    for position, (index, first) in enumerate(fingerprints):
        for other, second in fingerprints[position+1:]:
            intersection = len(first & second)
            similarity = intersection / max(1, len(first | second))
            if similarity >= 0.18:
                similar.append({"indices": [index, other], "five_word_jaccard": round(similarity, 3)})

    title_duplicates = [value for value, count in collections.Counter(title_values).items() if count > 1]
    description_duplicates = [value for value, count in collections.Counter(descriptions).items() if count > 1]
    report = {
        "expected": len(plan), "individually_rewritten": len(articles),
        "unfinished_indices": unfinished, "errors": errors,
        "repeated_long_paragraphs": repeated, "similar_pairs": similar,
        "duplicate_titles": title_duplicates, "duplicate_seo_descriptions": description_duplicates,
        "distinct_cover_sources": len(set(sources)), "distinct_cover_files": len(set(image_hashes)),
        "word_counts": {str(index): word_count(article["content"]) for index, article in articles},
        "external_originality_service_checked": False,
    }
    report["ready_for_import"] = (
        len(articles) == len(plan) and not any((unfinished, errors, repeated, similar, title_duplicates, description_duplicates))
        and len(set(sources)) == len(plan) and len(set(image_hashes)) == len(plan)
    )
    (batch / "quality-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=Path, default=CONTENT / "batches/2026-10-27")
    args = parser.parse_args()
    report = review(args.batch)
    print(json.dumps({key: report[key] for key in ("expected", "individually_rewritten", "ready_for_import")}, ensure_ascii=False))
    print("Unfinished:", len(report["unfinished_indices"]), "Errors:", len(report["errors"]),
          "Repeated paragraphs:", len(report["repeated_long_paragraphs"]), "Similar pairs:", len(report["similar_pairs"]))
    raise SystemExit(0 if report["ready_for_import"] else 1)


if __name__ == "__main__":
    main()
