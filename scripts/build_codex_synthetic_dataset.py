from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from remotion_pipeline.case_records import prepare_cases
from remotion_pipeline.synthetic_dataset import build_synthetic_records
from remotion_pipeline.utils import write_records

DEFAULT_MANIFESTS = [
    "data/synthetic/codex_manifest.json",
    "data/synthetic/codex_frontier_manifest.json",
    "data/synthetic/codex_gpt55_manifest.json",
    "data/synthetic/codex_gpt55_targeted_manifest.json",
    "data/synthetic/codex_gpt55_repair_manifest.json",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        action="append",
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

    manifests = args.manifest or DEFAULT_MANIFESTS
    records = prepare_cases(
        [
            record
            for manifest in manifests
            for record in build_synthetic_records(
                manifest_path=Path(manifest).resolve(),
                row_license=args.row_license,
                source_name=args.source_name,
                source_model=args.source_model,
            )
        ],
        source_label=", ".join(manifests),
    )
    write_records(Path(args.output).resolve(), records)
    print(f"Wrote {len(records)} synthetic cases to {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
