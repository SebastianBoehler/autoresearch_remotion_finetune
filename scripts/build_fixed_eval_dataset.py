from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from remotion_pipeline.case_records import case_to_chat_record, prepare_cases
from remotion_pipeline.utils import ensure_dir, load_records, write_json, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="data/eval/remotion_fixed_eval_cases.jsonl")
    parser.add_argument("--output-dir", default="artifacts/datasets/remotion-fixed-eval")
    args = parser.parse_args()

    source_path = (PROJECT_ROOT / args.source).resolve()
    output_dir = ensure_dir((PROJECT_ROOT / args.output_dir).resolve())
    cases = prepare_cases(load_records(source_path), source_label=str(source_path))
    write_jsonl(output_dir / "test.jsonl", [case_to_chat_record(case) for case in cases])
    write_json(
        output_dir / "manifest.json",
        {
            "source_dataset": str(source_path),
            "output_dir": str(output_dir),
            "counts": {"test": len(cases)},
            "purpose": "fixed behavior eval, not training",
        },
    )
    print(f"Wrote fixed eval dataset with {len(cases)} cases to {output_dir}")


if __name__ == "__main__":
    main()
