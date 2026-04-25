from __future__ import annotations

import random
import re
from typing import Any, Iterable

from remotion_pipeline.types import DatasetFilterConfig, SplitConfig

DEFAULT_SYSTEM_PROMPT = (
    "You write compact runnable Remotion React/TSX components. "
    "Return only TSX code, start with imports, export exactly one component, "
    "and rely only on React plus Remotion packages. Keep the component concise "
    "and syntactically complete with closed JSX. Use spring(...) from remotion "
    "when spring motion is needed; never import or call useSpring."
)
DEFAULT_DURATION_IN_FRAMES = 90
DEFAULT_FPS = 30
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
NAMED_EXPORT_PATTERN = re.compile(
    r"export\s+(?:const|function)\s+(?P<name>[A-Z][A-Za-z0-9_]*)"
)
DEFAULT_EXPORT_PATTERN = re.compile(r"export\s+default\b")
PASSTHROUGH_FIELDS = [
    "source_name",
    "source_url",
    "source_anchor",
    "license",
    "source_domain",
    "source_repo_path",
    "source_ref",
    "entry_component",
    "duration_in_frames",
    "fps",
    "width",
    "height",
    "default_props",
    "source_model",
    "source_rating",
    "source_skills",
    "attached_image_count",
    "synthetic_generation_method",
    "inspiration_sources",
    "prompt_id",
    "candidate_batch",
    "candidate_status",
    "candidate_compile_ok",
    "candidate_render_ok",
    "candidate_required_snippet_ratio",
    "candidate_forbidden_ok",
    "candidate_line_count",
    "candidate_line_count_ok",
    "candidate_ascii_ok",
    "candidate_preview_path",
    "candidate_preview_frame",
    "rating_decision",
    "human_rating",
    "human_notes",
    "generation_latency_ms",
    "generation_first_token_ms",
    "generation_prompt_tokens",
    "generation_completion_tokens",
    "generation_total_tokens",
    "openrouter_generation_id",
    "openrouter_response_model",
    "sample_index",
    "style_id",
    "style_name",
    "style_family",
    "audience",
    "visual_contract",
]


def _extract_message_fields(case: dict[str, Any]) -> dict[str, str]:
    values: dict[str, str] = {}
    for message in case.get("messages", []):
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        content = message.get("content")
        if role not in {"system", "user", "assistant"} or not isinstance(content, str):
            continue
        values.setdefault(role, content)
    return values


def _extract_entry_component(code: str) -> str:
    named_export = NAMED_EXPORT_PATTERN.search(code)
    if named_export:
        return named_export.group("name")
    if DEFAULT_EXPORT_PATTERN.search(code):
        return "GeneratedComposition"
    return "GeneratedComposition"


def _normalize_int(
    value: Any,
    *,
    fallback: int,
    field_name: str,
    case_id: str,
) -> int:
    if value is None:
        return fallback
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"Case {case_id} has invalid integer field: {field_name}")
    return value


def normalize_case_record(case: dict[str, Any]) -> dict[str, Any]:
    cleaned = dict(case)
    message_fields = _extract_message_fields(cleaned)
    if "system" not in cleaned and "system" in message_fields:
        cleaned["system"] = message_fields["system"]
    if "prompt" not in cleaned and "user" in message_fields:
        cleaned["prompt"] = message_fields["user"]
    if "completion" not in cleaned and "assistant" in message_fields:
        cleaned["completion"] = message_fields["assistant"]

    required = {"case_id", "prompt", "completion"}
    missing = sorted(required - cleaned.keys())
    if missing:
        raise ValueError(f"Case {case!r} is missing required keys: {missing}")
    if not str(cleaned["completion"]).strip():
        raise ValueError(f"Case {cleaned['case_id']} has an empty completion.")

    cleaned["system"] = cleaned.get("system", DEFAULT_SYSTEM_PROMPT)
    cleaned["entry_component"] = cleaned.get(
        "entry_component",
        _extract_entry_component(str(cleaned["completion"])),
    )
    cleaned["duration_in_frames"] = _normalize_int(
        cleaned.get("duration_in_frames"),
        fallback=DEFAULT_DURATION_IN_FRAMES,
        field_name="duration_in_frames",
        case_id=str(cleaned["case_id"]),
    )
    cleaned["fps"] = _normalize_int(
        cleaned.get("fps"),
        fallback=DEFAULT_FPS,
        field_name="fps",
        case_id=str(cleaned["case_id"]),
    )
    cleaned["width"] = _normalize_int(
        cleaned.get("width"),
        fallback=DEFAULT_WIDTH,
        field_name="width",
        case_id=str(cleaned["case_id"]),
    )
    cleaned["height"] = _normalize_int(
        cleaned.get("height"),
        fallback=DEFAULT_HEIGHT,
        field_name="height",
        case_id=str(cleaned["case_id"]),
    )
    default_props = cleaned.get("default_props")
    if default_props is None:
        cleaned["default_props"] = {}
    elif not isinstance(default_props, dict):
        raise ValueError(f"Case {cleaned['case_id']} has non-object field: default_props")
    for key in ("must_contain", "must_not_contain", "tags"):
        value = cleaned.get(key, [])
        if not isinstance(value, list):
            raise ValueError(f"Case {cleaned['case_id']} has non-list field: {key}")
        cleaned[key] = list(value)
    return cleaned


def split_cases(
    cases: list[dict[str, Any]],
    split_config: SplitConfig,
) -> dict[str, list[dict[str, Any]]]:
    if len(cases) < 3:
        raise ValueError("Need at least three Remotion examples to create train/valid/test splits.")
    shuffled = list(cases)
    random.Random(split_config.seed).shuffle(shuffled)
    train_count = max(1, int(len(shuffled) * split_config.train_fraction))
    valid_count = max(1, int(len(shuffled) * split_config.valid_fraction))
    train_count = min(train_count, len(shuffled) - 2)
    valid_count = min(valid_count, len(shuffled) - train_count - 1)
    return {
        "train": shuffled[:train_count],
        "valid": shuffled[train_count : train_count + valid_count],
        "test": shuffled[train_count + valid_count :],
    }


def matches_filter(case: dict[str, Any], dataset_filter: DatasetFilterConfig) -> bool:
    tags = set(case.get("tags", []))
    if dataset_filter.include_tags and not set(dataset_filter.include_tags).issubset(tags):
        return False
    if dataset_filter.exclude_tags and set(dataset_filter.exclude_tags) & tags:
        return False
    return True


def prepare_cases(
    source_records: Iterable[dict[str, Any]],
    dataset_filter: DatasetFilterConfig | None = None,
    source_label: str = "dataset",
) -> list[dict[str, Any]]:
    normalized_cases = [normalize_case_record(case) for case in source_records]
    effective_filter = dataset_filter or DatasetFilterConfig()
    filtered_cases = [
        case for case in normalized_cases if matches_filter(case, effective_filter)
    ]
    if not filtered_cases:
        raise ValueError(f"No dataset cases matched filter for {source_label}.")
    case_ids = [case["case_id"] for case in filtered_cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError(f"Duplicate case_id values found in {source_label}.")
    return filtered_cases


def case_to_chat_record(case: dict[str, Any]) -> dict[str, Any]:
    record = {
        "case_id": case["case_id"],
        "tags": case["tags"],
        "entry_component": case["entry_component"],
        "duration_in_frames": case["duration_in_frames"],
        "fps": case["fps"],
        "width": case["width"],
        "height": case["height"],
        "default_props": case["default_props"],
        "must_contain": case["must_contain"],
        "must_not_contain": case["must_not_contain"],
        "messages": [
            {"role": "system", "content": case["system"]},
            {"role": "user", "content": case["prompt"]},
            {"role": "assistant", "content": case["completion"]},
        ],
    }
    for field in PASSTHROUGH_FIELDS:
        record[field] = case.get(field)
    return record
