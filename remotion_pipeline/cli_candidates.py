from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from remotion_pipeline.candidate_generation import generate_openrouter_candidate_batch
from remotion_pipeline.rating import promote_rated_cases
from remotion_pipeline.types import ExperimentConfig, OpenRouterConfig


def register_candidate_commands(subparsers, commands: dict) -> None:
    generate = subparsers.add_parser("generate-candidates")
    generate.add_argument("--config", required=True)
    generate.add_argument("--prompts", required=True)
    generate.add_argument("--output-dir", required=True)
    generate.add_argument("--model", action="append", required=True)
    generate.add_argument("--samples-per-prompt", type=int, default=1)
    generate.add_argument("--max-prompts", type=int, default=0)
    generate.add_argument("--row-license", default="pending-human-review")
    generate.add_argument("--source-name", default="openrouter-synthetic-candidates")
    generate.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    generate.add_argument("--route")
    generate.add_argument("--max-tokens", type=int)
    generate.add_argument("--reasoning-effort")
    generate.add_argument("--exclude-reasoning", action="store_true")
    generate.add_argument("--no-render", action="store_true")
    commands["generate-candidates"] = cmd_generate_candidates

    promote = subparsers.add_parser("promote-rated-cases")
    promote.add_argument("--input", required=True)
    promote.add_argument("--output", required=True)
    promote.add_argument("--min-rating", type=int, default=4)
    promote.add_argument("--accepted-license", default="MIT")
    commands["promote-rated-cases"] = cmd_promote_rated_cases


def cmd_generate_candidates(args: argparse.Namespace) -> None:
    config_path = Path(args.config).resolve()
    config = ExperimentConfig.load(config_path)
    repo_root = config_path.parent.parent
    generation = config.generation
    if args.max_tokens is not None:
        generation = replace(generation, max_tokens=args.max_tokens)
    payload = generate_openrouter_candidate_batch(
        prompt_path=Path(args.prompts).resolve(),
        models=args.model,
        output_dir=Path(args.output_dir).resolve(),
        repo_root=repo_root,
        generation=generation,
        openrouter=OpenRouterConfig(
            api_key_env=args.api_key_env,
            route=args.route,
            reasoning_effort=args.reasoning_effort,
            reasoning_exclude=True if args.exclude_reasoning else None,
        ),
        runtime=config.evaluation.runtime,
        timeout_seconds=config.evaluation.max_render_seconds,
        samples_per_prompt=args.samples_per_prompt,
        row_license=args.row_license,
        source_name=args.source_name,
        render_enabled=not args.no_render,
        max_prompts=args.max_prompts,
    )
    print(f"Wrote candidates to {Path(args.output_dir).resolve()}")
    print(payload["summary"])


def cmd_promote_rated_cases(args: argparse.Namespace) -> None:
    promoted = promote_rated_cases(
        input_path=Path(args.input).resolve(),
        output_path=Path(args.output).resolve(),
        min_rating=args.min_rating,
        accepted_license=args.accepted_license,
    )
    print(f"Promoted {len(promoted)} rated cases to {Path(args.output).resolve()}")
