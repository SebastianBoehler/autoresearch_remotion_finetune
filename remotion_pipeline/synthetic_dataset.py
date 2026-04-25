from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from remotion_pipeline.case_records import DEFAULT_SYSTEM_PROMPT, prepare_cases
from remotion_pipeline.utils import resolve_path, write_records

DEFAULT_SYNTHETIC_SOURCE_NAME = "codex-synthetic-v1"
DEFAULT_SYNTHETIC_SOURCE_MODEL = "codex-gpt-5"
DEFAULT_SYNTHETIC_METHOD = "codex-authored-from-remotion-principles"


def load_synthetic_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    entries = payload.get("cases")
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"{path} must contain a non-empty `cases` list.")
    return payload


def build_synthetic_records(
    *,
    manifest_path: Path,
    row_license: str = "MIT",
    source_name: str = DEFAULT_SYNTHETIC_SOURCE_NAME,
    source_model: str = DEFAULT_SYNTHETIC_SOURCE_MODEL,
) -> list[dict[str, Any]]:
    manifest = load_synthetic_manifest(manifest_path)
    base_dir = manifest_path.parent
    inspiration_sources = manifest.get("inspiration_sources", [])
    if not isinstance(inspiration_sources, list):
        raise ValueError("Manifest field `inspiration_sources` must be a list.")
    manifest_source_model = str(manifest.get("source_model", source_model))

    records = [
        _build_record(
            entry=entry,
            base_dir=base_dir,
            row_license=row_license,
            source_name=source_name,
            source_model=manifest_source_model,
            inspiration_sources=inspiration_sources,
        )
        for entry in manifest["cases"]
    ]
    return prepare_cases(records, source_label=str(manifest_path))


def write_synthetic_dataset(
    *,
    manifest_path: Path,
    output_path: Path,
    row_license: str = "MIT",
    source_name: str = DEFAULT_SYNTHETIC_SOURCE_NAME,
    source_model: str = DEFAULT_SYNTHETIC_SOURCE_MODEL,
) -> list[dict[str, Any]]:
    records = build_synthetic_records(
        manifest_path=manifest_path,
        row_license=row_license,
        source_name=source_name,
        source_model=source_model,
    )
    write_records(output_path, records)
    return records


def _build_record(
    *,
    entry: dict[str, Any],
    base_dir: Path,
    row_license: str,
    source_name: str,
    source_model: str,
    inspiration_sources: list[Any],
) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValueError("Every synthetic case entry must be an object.")
    required = {"case_id", "prompt", "template_path", "tags"}
    missing = sorted(required - entry.keys())
    if missing:
        raise ValueError(f"Synthetic case entry is missing keys: {missing}")

    template_path = resolve_path(base_dir, str(entry["template_path"]))
    code = template_path.read_text().strip()
    if not isinstance(entry["tags"], list):
        raise ValueError(f"Synthetic case {entry['case_id']} has non-list field: tags")
    tags = ["codex-synthetic", *entry["tags"]]
    record = {
        "case_id": entry["case_id"],
        "system": entry.get("system", DEFAULT_SYSTEM_PROMPT),
        "prompt": entry["prompt"],
        "completion": f"{code}\n",
        "tags": tags,
        "must_contain": entry.get("must_contain", []),
        "must_not_contain": entry.get("must_not_contain", []),
        "duration_in_frames": entry.get("duration_in_frames", 90),
        "fps": entry.get("fps", 30),
        "width": entry.get("width", 1280),
        "height": entry.get("height", 720),
        "default_props": entry.get("default_props", {}),
        "license": row_license,
        "source_name": source_name,
        "source_model": entry.get("source_model", source_model),
        "source_rating": entry.get("source_rating", "codex-authored"),
        "source_repo_path": str(Path(entry["template_path"])),
        "synthetic_generation_method": entry.get(
            "synthetic_generation_method",
            DEFAULT_SYNTHETIC_METHOD,
        ),
        "inspiration_sources": [str(source) for source in inspiration_sources],
    }
    if entry.get("entry_component"):
        record["entry_component"] = entry["entry_component"]
    return record
