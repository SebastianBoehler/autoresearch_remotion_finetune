from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from remotion_pipeline.local_inference import clear_model_cache
from remotion_pipeline.retry_eval import (
    evaluate_with_verified_retries,
    fixed_eval_primary_selector,
    fixed_eval_retry_selector,
    retry_generation_from_config,
)
from remotion_pipeline.types import ExperimentConfig
from remotion_pipeline.utils import resolve_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/qwen25coder_3b_remotion.json")
    parser.add_argument("--dataset-dir", default="artifacts/datasets/remotion-fixed-eval")
    parser.add_argument(
        "--output",
        default="artifacts/evals/qwen25coder-3b-remotion-fixed-eval-verified-retry.json",
    )
    parser.add_argument("--retry-temperature", type=float, default=0.6)
    parser.add_argument("--retry-top-p", type=float, default=0.75)
    parser.add_argument("--retry-seed", type=int)
    parser.add_argument(
        "--retry",
        action="append",
        help="Fallback decoder as temperature,top_p[,seed[,max_tokens]]. Can be repeated.",
    )
    parser.add_argument(
        "--adaptive-profile",
        choices=["fixed-eval-v1"],
        help="Route retries by prompt family to avoid wasted fallback attempts.",
    )
    parser.add_argument(
        "--primary-profile",
        choices=["fixed-eval-v1"],
        help="Route the first generation by prompt family before verified retries.",
    )
    parser.add_argument("--max-cases", type=int, default=0)
    args = parser.parse_args()

    config = ExperimentConfig.load(resolve_path(PROJECT_ROOT, args.config))
    config = replace(
        config,
        dataset_dir=args.dataset_dir,
        run_loss_eval=False,
        evaluation=replace(config.evaluation, max_cases=args.max_cases),
    )
    retry_generations = _retry_generations(config, args)
    clear_model_cache()
    payload = evaluate_with_verified_retries(
        config=config,
        repo_root=PROJECT_ROOT,
        dataset_dir=resolve_path(PROJECT_ROOT, config.dataset_dir),
        adapter_path=resolve_path(PROJECT_ROOT, config.adapter_path),
        output_path=resolve_path(PROJECT_ROOT, args.output),
        retry_generations=retry_generations,
        retry_selector=_retry_selector(config, args),
        primary_selector=_primary_selector(config, args),
    )
    clear_model_cache()
    print(payload["summary"])


def _retry_generations(config: ExperimentConfig, args: argparse.Namespace):
    if args.adaptive_profile:
        return []
    if not args.retry:
        return [
            retry_generation_from_config(
                config.generation,
                temperature=args.retry_temperature,
                top_p=args.retry_top_p,
                seed=args.retry_seed,
            )
        ]
    return [_parse_retry(config, value) for value in args.retry]


def _retry_selector(config: ExperimentConfig, args: argparse.Namespace):
    if args.adaptive_profile != "fixed-eval-v1":
        return None
    return fixed_eval_retry_selector(config.generation)


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
    return _make_retry(config, float(parts[0]), float(parts[1]), seed, max_tokens)


def _make_retry(
    config: ExperimentConfig,
    temperature: float,
    top_p: float,
    seed: int | None,
    max_tokens: int | None,
):
    return retry_generation_from_config(
        config.generation,
        temperature=temperature,
        top_p=top_p,
        seed=seed,
        max_tokens=max_tokens,
    )


if __name__ == "__main__":
    main()
