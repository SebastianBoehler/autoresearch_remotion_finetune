from __future__ import annotations

import argparse
from pathlib import Path

from remotion_pipeline.latency_benchmark import run_latency_benchmark
from remotion_pipeline.types import BenchmarkConfig
from remotion_pipeline.utils import resolve_path


def cmd_latency_benchmark(args: argparse.Namespace) -> None:
    config_path = Path(args.config).resolve()
    benchmark = BenchmarkConfig.load(config_path)
    repo_root = config_path.parent.parent
    target_names = set(args.target or []) or None
    payload = run_latency_benchmark(
        benchmark,
        repo_root,
        max_cases=args.max_cases,
        max_tokens=args.max_tokens,
        target_names=target_names,
        warmup_cases=args.warmup_cases,
        repetitions=args.repetitions,
    )
    output_path = resolve_path(repo_root, benchmark.output_dir) / "latency-leaderboard.json"
    print(f"Latency benchmark written to {output_path}")
    for index, entry in enumerate(payload["leaderboard"], start=1):
        summary = entry["summary"]
        print(
            f"{index}. {entry['name']} "
            f"(wall={_fmt(summary.get('mean_wall_seconds'))}s, "
            f"ttft={_fmt(summary.get('mean_ttft_seconds'))}, "
            f"e2e_tps={_fmt(summary.get('mean_end_to_end_generation_tokens_per_second'))})"
        )


def register_latency_commands(
    subparsers: argparse._SubParsersAction,
    commands: dict[str, object],
) -> None:
    parser = subparsers.add_parser("latency-benchmark")
    parser.add_argument("--config", required=True)
    parser.add_argument("--max-cases", type=int)
    parser.add_argument("--max-tokens", type=int)
    parser.add_argument("--target", action="append")
    parser.add_argument("--warmup-cases", type=int, default=1)
    parser.add_argument("--repetitions", type=int, default=1)
    commands["latency-benchmark"] = cmd_latency_benchmark


def _fmt(value: object) -> str:
    return "n/a" if value is None else f"{float(value):.3f}"
