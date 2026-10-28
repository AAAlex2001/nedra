"""Compare a batch against existing articles without calling external services."""

import argparse
import collections
import json
import re
from pathlib import Path

from review_batch import CONTENT, normalized, shingles


def compare(batch):
    plan = json.loads((batch / "plan.json").read_text(encoding="utf8"))
    batch_slugs = {item["slug"] for item in plan}
    existing_plan = [item for item in json.loads((CONTENT / "plan.json").read_text(encoding="utf8"))
                     if item["slug"] not in batch_slugs]
    existing_sets = []
    inverted = collections.defaultdict(list)
    paragraphs = collections.defaultdict(set)
    for index, item in enumerate(existing_plan):
        article = json.loads((CONTENT / "articles" / (item["slug"] + ".json")).read_text(encoding="utf8"))
        values = shingles(article["content"])
        existing_sets.append(len(values))
        for value in values:
            inverted[value].append(index)
        for value in re.findall(r"<p>(.*?)</p>", article["content"], re.S):
            text = normalized(value)
            if len(text) >= 180:
                paragraphs[text].add(item["slug"])

    near, exact, missing = [], [], []
    for item in plan:
        path = CONTENT / "articles" / (item["slug"] + ".json")
        if not path.exists():
            missing.append(item["slug"])
            continue
        article = json.loads(path.read_text(encoding="utf8"))
        values = shingles(article["content"])
        counts = collections.Counter(index for value in values for index in inverted.get(value, ()))
        for index, common in counts.items():
            score = common / (len(values) + existing_sets[index] - common)
            if score >= 0.18:
                near.append({"new": item["slug"], "existing": existing_plan[index]["slug"],
                             "similarity": round(score, 4)})
        for value in re.findall(r"<p>(.*?)</p>", article["content"], re.S):
            text = normalized(value)
            if text in paragraphs:
                exact.append({"new": item["slug"], "existing": sorted(paragraphs[text])})
    report = {
        "articles_checked": len(plan) - len(missing),
        "existing_articles_compared": len(existing_plan),
        "missing": missing,
        "near_existing_articles": near,
        "exact_long_paragraph_matches": exact,
        "external_uniqueness_service_used": False,
    }
    (batch / "existing-overlap.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True, type=Path)
    report = compare(parser.parse_args().batch)
    print("Checked:", report["articles_checked"], "Existing:", report["existing_articles_compared"],
          "Similar:", len(report["near_existing_articles"]), "Copied paragraphs:", len(report["exact_long_paragraph_matches"]))
    raise SystemExit(bool(report["missing"] or report["near_existing_articles"] or report["exact_long_paragraph_matches"]))
