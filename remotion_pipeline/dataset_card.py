from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from remotion_pipeline.case_records import PASSTHROUGH_FIELDS


def build_dataset_card(metadata: dict[str, Any], output_dir: Path) -> str:
    title = metadata.get("pretty_name") or metadata.get("repo_id") or output_dir.name
    counts = metadata["counts"]
    repo_id = metadata.get("repo_id")
    column_names = [
        "case_id",
        "system",
        "prompt",
        "completion",
        "messages",
        "tags",
        "entry_component",
        "duration_in_frames",
        "fps",
        "width",
        "height",
        "default_props",
        "must_contain",
        "must_not_contain",
        *PASSTHROUGH_FIELDS,
    ]
    lines = [
        _build_frontmatter(metadata),
        f"# {title}",
        "",
        "Curated Remotion code-generation examples exported from the `autoresearch_remotion_finetune` pipeline.",
        "",
        "## Summary",
        "",
        "- Focus: supervised fine-tuning and evaluation examples for prompt-to-Remotion code generation.",
        "- Primary modality: text-to-code pairs with duration, frame-rate, and render metadata.",
        "- Export configs: one canonical source config and one train-ready chat config.",
        "",
        "## Counts",
        "",
        f"- Canonical cases: {counts['cases']}",
        f"- Chat train: {counts['chat']['train']}",
        f"- Chat validation: {counts['chat']['validation']}",
        f"- Chat test: {counts['chat']['test']}",
        "",
        "## Columns",
        "",
    ]
    lines.extend(f"- `{column}`" for column in column_names)
    lines.extend(
        [
            "",
            "## Provenance And Licensing",
            "",
            f"- Repository-level license metadata is `{metadata['license']}`.",
            "- Each exported row should keep its row-level `license` and source metadata.",
            "",
            "## Notes",
            "",
            f"- Source dataset: `{metadata['source_dataset']}`",
            f"- Split seed: `{metadata['split_seed']}`",
        ]
    )
    if metadata["dataset_filter"]["include_tags"]:
        lines.append(
            "- Included tags: `"
            + "`, `".join(metadata["dataset_filter"]["include_tags"])
            + "`"
        )
    if metadata["dataset_filter"]["exclude_tags"]:
        lines.append(
            "- Excluded tags: `"
            + "`, `".join(metadata["dataset_filter"]["exclude_tags"])
            + "`"
        )
    if repo_id:
        lines.extend(
            [
                "",
                "## Loading",
                "",
                "```python",
                "from datasets import load_dataset",
                "",
                f"cases = load_dataset({json.dumps(repo_id)}, 'cases', split='train')",
                f"chat = load_dataset({json.dumps(repo_id)}, 'chat')",
                "```",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def _build_frontmatter(metadata: dict[str, Any]) -> str:
    lines = [
        "---",
        "configs:",
        "- config_name: cases",
        "  data_files:",
        "  - split: train",
        "    path: cases.jsonl",
        "- config_name: chat",
        "  data_files:",
        "  - split: train",
        "    path: chat/train.jsonl",
        "  - split: validation",
        "    path: chat/validation.jsonl",
        "  - split: test",
        "    path: chat/test.jsonl",
    ]
    if metadata.get("pretty_name"):
        lines.append(f"pretty_name: {json.dumps(metadata['pretty_name'])}")
    lines.append(f"license: {json.dumps(metadata['license'])}")
    if metadata.get("tags"):
        lines.append("tags:")
        lines.extend(f"- {tag}" for tag in metadata["tags"])
    lines.append("---")
    return "\n".join(lines)
