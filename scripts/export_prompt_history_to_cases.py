from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from remotion_pipeline.case_records import DEFAULT_SYSTEM_PROMPT
from remotion_pipeline.utils import load_records, write_records

SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


def _slugify(value: str) -> str:
    return SLUG_PATTERN.sub("-", value.lower()).strip("-") or "sample"


def _duration_tags(record: dict) -> list[str]:
    frames = record.get("durationInFrames")
    fps = record.get("fps") or 30
    if not isinstance(frames, int) or not isinstance(fps, int) or fps <= 0:
        return []
    seconds = round(frames / fps)
    return [f"duration:{seconds}s"]


def _build_case(
    record: dict,
    index: int,
    *,
    row_license: str,
    source_name: str,
) -> dict:
    prompt = str(record["prompt"]).strip()
    code = str(record["code"]).strip()
    record_id = str(record.get("id") or index)
    model = str(record.get("model") or "unknown-model")
    rating = record.get("rating")
    return {
        "case_id": f"history-{_slugify(record_id)}-{_slugify(prompt)[:48]}",
        "system": DEFAULT_SYSTEM_PROMPT,
        "prompt": prompt,
        "completion": code,
        "tags": [
            f"source:{_slugify(source_name)}",
            f"model:{_slugify(model)}",
            *(_duration_tags(record)),
        ],
        "must_contain": [],
        "must_not_contain": [],
        "duration_in_frames": record.get("durationInFrames") or 90,
        "fps": record.get("fps") or 30,
        "width": 1280,
        "height": 720,
        "default_props": {},
        "source_model": model,
        "source_rating": rating,
        "source_skills": record.get("skills") or [],
        "attached_image_count": record.get("attachedImageCount") or 0,
        "license": row_license,
        "source_name": source_name,
        "source_repo_path": "history-export",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--only-rated-up", action="store_true")
    parser.add_argument(
        "--row-license",
        default="MIT",
        help="SPDX-style license label to attach to each exported row.",
    )
    parser.add_argument(
        "--source-name",
        default="prompt-history-export",
        help="Human-readable source label stored in each exported row.",
    )
    args = parser.parse_args()

    records = load_records(Path(args.input).resolve())
    selected = [
        record
        for record in records
        if not args.only_rated_up or record.get("rating") == "up"
    ]
    cases = [
        _build_case(
            record,
            index,
            row_license=args.row_license,
            source_name=args.source_name,
        )
        for index, record in enumerate(selected, start=1)
    ]
    write_records(Path(args.output).resolve(), cases)
    print(f"Wrote {len(cases)} cases to {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
