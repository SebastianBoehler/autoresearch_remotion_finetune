from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from remotion_pipeline.case_records import case_to_chat_record, prepare_cases
from remotion_pipeline.utils import ensure_dir, load_records, write_json, write_jsonl

DEFAULT_SOURCES = [
    "data/generation_prompts/remotion_frontier_niche_prompts.jsonl",
    "data/generation_prompts/remotion_frontier_niche_prompts_round2.jsonl",
    "data/generation_prompts/remotion_frontier_niche_prompts_round3.jsonl",
]
PLACEHOLDER_COMPLETION = (
    'import { AbsoluteFill } from "remotion";\n'
    "export const EvalPlaceholder = () => <AbsoluteFill />;\n"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", help="Prompt-bank JSONL file.")
    parser.add_argument("--output-dir", default="artifacts/datasets/remotion-frontier-eval")
    args = parser.parse_args()

    source_paths = [PROJECT_ROOT / source for source in (args.source or DEFAULT_SOURCES)]
    cases = prompt_records_to_eval_cases(source_paths)
    output_dir = ensure_dir((PROJECT_ROOT / args.output_dir).resolve())
    write_jsonl(output_dir / "test.jsonl", [case_to_chat_record(case) for case in cases])
    write_json(
        output_dir / "manifest.json",
        {
            "source_dataset": [str(path.resolve()) for path in source_paths],
            "output_dir": str(output_dir),
            "counts": {"test": len(cases)},
            "purpose": "arbitrary frontier prompt eval, not training",
        },
    )
    print(f"Wrote prompt eval dataset with {len(cases)} cases to {output_dir}")


def prompt_records_to_eval_cases(source_paths: list[Path]) -> list[dict[str, Any]]:
    records = [
        _prompt_record_to_eval_case(row)
        for source_path in source_paths
        for row in load_records(source_path.resolve())
    ]
    return prepare_cases(records, source_label=", ".join(str(path) for path in source_paths))


def _prompt_record_to_eval_case(row: dict[str, Any]) -> dict[str, Any]:
    prompt_id = str(row["prompt_id"])
    return {
        "case_id": f"eval_{prompt_id}",
        "prompt": row["prompt"],
        "completion": PLACEHOLDER_COMPLETION,
        "tags": ["frontier-eval", *row.get("tags", [])],
        "must_contain": row.get("must_contain", []),
        "must_not_contain": row.get("must_not_contain", []),
        "duration_in_frames": row.get("duration_in_frames", 120),
        "fps": row.get("fps", 30),
        "width": row.get("width", 1280),
        "height": row.get("height", 720),
        "prompt_id": prompt_id,
    }


if __name__ == "__main__":
    main()
