from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from remotion_pipeline.utils import load_records, write_jsonl

GLOBAL_VISUAL_CONTRACT = (
    "Accessibility and polish constraints: all important text must be high contrast, "
    "large enough to read in a video preview, and never rely on opacity below 0.72. "
    "Avoid gray-on-dark labels, tiny captions, crowded layouts, and black intro frames. "
    "The midpoint frame should already show the main artifact clearly."
)


def build_style_prompt_bank(
    *,
    base_prompts_path: Path,
    style_profiles_path: Path,
    output_path: Path,
    style_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    base_prompts = load_records(base_prompts_path)
    styles = _load_styles(style_profiles_path, style_ids)
    records = [
        _style_prompt(base_prompt, style)
        for base_prompt in base_prompts
        for style in styles
    ]
    write_jsonl(output_path, records)
    return records


def _load_styles(path: Path, style_ids: list[str] | None) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text())
    styles = payload.get("styles")
    if not isinstance(styles, list) or not styles:
        raise ValueError(f"{path} must contain a non-empty `styles` list.")
    selected = styles
    if style_ids:
        wanted = set(style_ids)
        selected = [style for style in styles if style.get("style_id") in wanted]
        missing = sorted(wanted - {style.get("style_id") for style in selected})
        if missing:
            raise ValueError(f"Unknown style ids in {path}: {missing}")
    return selected


def _style_prompt(base: dict[str, Any], style: dict[str, Any]) -> dict[str, Any]:
    prompt_id = f"{base['prompt_id']}__{style['style_id']}"
    prompt = "\n\n".join(
        [
            str(base["prompt"]).strip(),
            f"Style profile: {style['name']}.",
            str(style["prompt"]).strip(),
            GLOBAL_VISUAL_CONTRACT,
        ]
    )
    return {
        **base,
        "prompt_id": prompt_id,
        "prompt": prompt,
        "tags": _merge_unique(
            base.get("tags", []),
            style.get("tags", []),
            [f"style:{style['style_id']}"],
        ),
        "must_not_contain": _merge_unique(
            base.get("must_not_contain", []),
            ["Composition"],
        ),
        "style_id": style["style_id"],
        "style_name": style["name"],
        "style_family": style.get("family"),
        "audience": style.get("audience"),
        "visual_contract": GLOBAL_VISUAL_CONTRACT,
    }


def _merge_unique(*groups: list[Any]) -> list[Any]:
    values: list[Any] = []
    for group in groups:
        for item in group:
            if item not in values:
                values.append(item)
    return values
