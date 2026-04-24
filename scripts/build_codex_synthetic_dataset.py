from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from remotion_pipeline.synthetic_dataset import write_synthetic_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        default="data/synthetic/codex_manifest.json",
        help="Synthetic dataset manifest with prompts and template paths.",
    )
    parser.add_argument(
        "--output",
        default="data/remotion_codex_synthetic_cases.jsonl",
        help="Canonical JSONL dataset path to write.",
    )
    parser.add_argument("--row-license", default="MIT")
    parser.add_argument("--source-name", default="codex-synthetic-v1")
    parser.add_argument("--source-model", default="codex-gpt-5")
    args = parser.parse_args()

    records = write_synthetic_dataset(
        manifest_path=Path(args.manifest).resolve(),
        output_path=Path(args.output).resolve(),
        row_license=args.row_license,
        source_name=args.source_name,
        source_model=args.source_model,
    )
    print(f"Wrote {len(records)} synthetic cases to {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
