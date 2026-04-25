from __future__ import annotations

import argparse
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from remotion_pipeline.case_records import DEFAULT_SYSTEM_PROMPT
from remotion_pipeline.local_inference import clear_model_cache
from remotion_pipeline.retry_eval import (
    evaluate_with_verified_retries,
    fixed_eval_primary_selector,
    fixed_eval_retry_selector,
    retry_generation_from_config,
)
from remotion_pipeline.types import ExperimentConfig
from remotion_pipeline.utils import resolve_path, write_jsonl


def main() -> None:
    args = _parse_args()
    prompt = _prompt_text(args)
    config = ExperimentConfig.load(resolve_path(PROJECT_ROOT, args.config))
    if args.no_render:
        config = replace(config, evaluation=replace(config.evaluation, run_render=False))
    retry_generations = _retry_generations(config, args)
    retry_selector = (
        fixed_eval_retry_selector(config.generation)
        if args.adaptive_profile == "fixed-eval-v1"
        else None
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        dataset_dir = Path(tmpdir)
        write_jsonl(dataset_dir / "test.jsonl", [_case_record(args, prompt)])
        clear_model_cache()
        payload = evaluate_with_verified_retries(
            config=config,
            repo_root=PROJECT_ROOT,
            dataset_dir=dataset_dir,
            adapter_path=resolve_path(PROJECT_ROOT, config.adapter_path),
            output_path=resolve_path(PROJECT_ROOT, args.eval_output),
            retry_generations=retry_generations,
            retry_selector=retry_selector,
            primary_selector=_primary_selector(config, args),
        )
        clear_model_cache()

    case = payload["cases"][0]
    output_path = resolve_path(PROJECT_ROOT, args.output)
    verified = _is_verified_case(case)
    if verified or args.allow_unverified_output:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(case["code"])
    report = {
        "output": str(output_path) if verified or args.allow_unverified_output else None,
        "eval_output": str(resolve_path(PROJECT_ROOT, args.eval_output)),
        "compile_ok": case["compile_ok"],
        "render_ok": case["render_ok"],
        "score": case["weighted_score"],
        "attempt_count": case["attempt_count"],
        "selected_attempt_index": case["selected_attempt_index"],
        "verified": verified,
    }
    print(report)
    if not verified and not args.allow_unverified_output:
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/qwen25coder_3b_remotion.json")
    prompt = parser.add_mutually_exclusive_group(required=True)
    prompt.add_argument("--prompt")
    prompt.add_argument("--prompt-file")
    parser.add_argument("--output", default="artifacts/generated/verified-remotion.tsx")
    parser.add_argument("--eval-output", default="artifacts/evals/verified-generation.json")
    parser.add_argument("--case-id", default="verified_prompt")
    parser.add_argument("--system", default=DEFAULT_SYSTEM_PROMPT)
    parser.add_argument("--adaptive-profile", choices=["fixed-eval-v1"])
    parser.add_argument("--primary-profile", choices=["fixed-eval-v1"])
    parser.add_argument("--retry", action="append")
    parser.add_argument("--must-contain", action="append", default=[])
    parser.add_argument(
        "--must-not-contain",
        action="append",
        default=["fetch(", "axios", "Math.random", "useSpring", "Composition"],
    )
    parser.add_argument("--duration-in-frames", type=int, default=120)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--no-render", action="store_true")
    parser.add_argument("--allow-unverified-output", action="store_true")
    return parser.parse_args()


def _prompt_text(args: argparse.Namespace) -> str:
    if args.prompt is not None:
        return args.prompt
    return resolve_path(PROJECT_ROOT, args.prompt_file).read_text().strip()


def _case_record(args: argparse.Namespace, prompt: str) -> dict:
    return {
        "case_id": args.case_id,
        "tags": ["verified-generation"],
        "duration_in_frames": args.duration_in_frames,
        "fps": args.fps,
        "width": args.width,
        "height": args.height,
        "default_props": {},
        "must_contain": args.must_contain,
        "must_not_contain": args.must_not_contain,
        "messages": [
            {"role": "system", "content": args.system},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": ""},
        ],
    }


def _is_verified_case(case: dict) -> bool:
    return bool(case["compile_ok"] and case["render_ok"] is not False)


def _retry_generations(config: ExperimentConfig, args: argparse.Namespace):
    if args.adaptive_profile:
        return []
    retries = args.retry or ["0.6,0.75,42"]
    return [_parse_retry(config, retry) for retry in retries]


def _primary_selector(config: ExperimentConfig, args: argparse.Namespace):
    if args.primary_profile != "fixed-eval-v1":
        return None
    return fixed_eval_primary_selector(config.generation)


def _parse_retry(config: ExperimentConfig, value: str):
    parts = [part.strip() for part in value.split(",")]
    if len(parts) not in {2, 3, 4}:
        raise ValueError("--retry must be temperature,top_p[,seed[,max_tokens]]")
    seed = int(parts[2]) if len(parts) >= 3 and parts[2] else None
    max_tokens = int(parts[3]) if len(parts) == 4 and parts[3] else None
    return retry_generation_from_config(
        config.generation,
        temperature=float(parts[0]),
        top_p=float(parts[1]),
        seed=seed,
        max_tokens=max_tokens,
    )


if __name__ == "__main__":
    main()
