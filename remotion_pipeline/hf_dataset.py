from __future__ import annotations

from pathlib import Path
from typing import Any

from remotion_pipeline.case_records import case_to_chat_record, prepare_cases, split_cases
from remotion_pipeline.dataset_card import build_dataset_card
from remotion_pipeline.dataset_sources import load_source_records
from remotion_pipeline.license_metadata import (
    DEFAULT_DATASET_LICENSE_ID,
    ensure_records_have_licenses,
)
from remotion_pipeline.types import DatasetFilterConfig, DatasetSourceConfig, SplitConfig
from remotion_pipeline.utils import ensure_dir, write_json, write_jsonl


def export_hf_dataset(
    *,
    source: DatasetSourceConfig,
    output_dir: Path,
    split_config: SplitConfig,
    dataset_filter: DatasetFilterConfig | None = None,
    repo_id: str | None = None,
    pretty_name: str | None = None,
    license_name: str | None = None,
    languages: list[str] | None = None,
    task_categories: list[str] | None = None,
    size_categories: list[str] | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    source_records, source_label = load_source_records(source)
    cases = prepare_cases(source_records, dataset_filter, source_label)
    ensure_records_have_licenses(cases, source_label=source_label)
    split_map = split_cases(cases, split_config)

    ensure_dir(output_dir)
    write_jsonl(output_dir / "cases.jsonl", [dict(case) for case in cases])
    chat_dir = ensure_dir(output_dir / "chat")
    split_counts: dict[str, int] = {}
    for split_name, split_cases_payload in split_map.items():
        hf_split_name = "validation" if split_name == "valid" else split_name
        records = [case_to_chat_record(case) for case in split_cases_payload]
        write_jsonl(chat_dir / f"{hf_split_name}.jsonl", records)
        split_counts[hf_split_name] = len(records)

    metadata = {
        "source_dataset": source.describe(),
        "counts": {
            "cases": len(cases),
            "chat": split_counts,
        },
        "split_seed": split_config.seed,
        "dataset_filter": {
            "include_tags": (dataset_filter or DatasetFilterConfig()).include_tags,
            "exclude_tags": (dataset_filter or DatasetFilterConfig()).exclude_tags,
        },
        "repo_id": repo_id,
        "pretty_name": pretty_name,
        "license": license_name or DEFAULT_DATASET_LICENSE_ID,
        "languages": languages or [],
        "task_categories": task_categories or [],
        "size_categories": size_categories or [],
        "tags": tags or [],
    }
    write_json(output_dir / "hf_dataset_manifest.json", metadata)
    (output_dir / "README.md").write_text(build_dataset_card(metadata, output_dir))
    return metadata
