from __future__ import annotations

from pathlib import Path
from typing import Any

from remotion_pipeline.case_records import prepare_cases
from remotion_pipeline.utils import load_records, write_records

ACCEPT_DECISIONS = {"accept", "accepted", "approve", "approved"}
REJECT_DECISIONS = {"reject", "rejected", "skip", "discard"}


def promote_rated_cases(
    *,
    input_path: Path,
    output_path: Path,
    min_rating: int = 4,
    accepted_license: str = "MIT",
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for record in load_records(input_path):
        if record.get("candidate_compile_ok") is False or record.get("candidate_render_ok") is False:
            continue
        if record.get("candidate_forbidden_ok") is False:
            continue
        required_ratio = record.get("candidate_required_snippet_ratio")
        if isinstance(required_ratio, (int, float)) and required_ratio < 1:
            continue
        rating = _parse_rating(record.get("human_rating"))
        decision = str(record.get("rating_decision") or "").strip().lower()
        if decision in REJECT_DECISIONS:
            continue
        if decision not in ACCEPT_DECISIONS and (rating is None or rating < min_rating):
            continue
        promoted = dict(record)
        promoted["license"] = accepted_license
        promoted["candidate_status"] = "human-approved"
        promoted["rating_decision"] = "accepted"
        promoted["source_rating"] = f"human:{rating}" if rating is not None else "human:accepted"
        promoted["tags"] = _append_unique(promoted.get("tags", []), "human-approved")
        selected.append(promoted)

    prepared = prepare_cases(selected, source_label=str(input_path))
    write_records(output_path, prepared)
    return prepared


def _parse_rating(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _append_unique(values: Any, value: str) -> list[str]:
    items = list(values) if isinstance(values, list) else []
    return items if value in items else [*items, value]
