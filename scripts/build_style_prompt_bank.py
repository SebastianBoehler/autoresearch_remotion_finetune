from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from remotion_pipeline.style_prompts import build_style_prompt_bank


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-prompts",
        default="data/generation_prompts/remotion_learning_app_base_prompts.jsonl",
    )
    parser.add_argument(
        "--styles",
        default="data/style_profiles/remotion_learning_styles.json",
    )
    parser.add_argument(
        "--output",
        default="data/generation_prompts/remotion_learning_app_style_prompts.jsonl",
    )
    parser.add_argument("--style-id", action="append")
    args = parser.parse_args()

    records = build_style_prompt_bank(
        base_prompts_path=Path(args.base_prompts).resolve(),
        style_profiles_path=Path(args.styles).resolve(),
        output_path=Path(args.output).resolve(),
        style_ids=args.style_id,
    )
    print(f"Wrote {len(records)} styled prompts to {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
