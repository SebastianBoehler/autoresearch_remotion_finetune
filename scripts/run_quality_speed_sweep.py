from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from remotion_pipeline.eval import evaluate_adapter
from remotion_pipeline.latency_benchmark import run_latency_benchmark
from remotion_pipeline.types import BenchmarkConfig, ExperimentConfig
from remotion_pipeline.utils import ensure_dir, resolve_path, write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/qwen25coder_3b_remotion.json")
    parser.add_argument("--latency-config", default="configs/local_mlx_latency_benchmark.json")
    parser.add_argument("--output-dir", default="artifacts/sweeps/quality-speed")
    parser.add_argument("--cap", type=int, action="append")
    parser.add_argument("--latency-cases", type=int, default=5)
    parser.add_argument("--target", default="remotion-lora-qwen25coder-3b")
    args = parser.parse_args()

    output_dir = ensure_dir(resolve_path(PROJECT_ROOT, args.output_dir))
    experiment = ExperimentConfig.load(resolve_path(PROJECT_ROOT, args.config))
    latency = BenchmarkConfig.load(resolve_path(PROJECT_ROOT, args.latency_config))
    rows: list[dict[str, object]] = []
    caps = args.cap or [700, 900, 1200]
    for cap in caps:
        exp = replace(experiment, generation=replace(experiment.generation, max_tokens=cap))
        eval_path = output_dir / f"eval-cap-{cap}.json"
        eval_payload = evaluate_adapter(
            config=exp,
            repo_root=PROJECT_ROOT,
            dataset_dir=resolve_path(PROJECT_ROOT, exp.dataset_dir),
            adapter_path=resolve_path(PROJECT_ROOT, exp.adapter_path),
            output_path=eval_path,
        )
        latency_config = replace(
            latency,
            output_dir=str(output_dir / f"latency-cap-{cap}"),
            generation=replace(latency.generation, max_tokens=cap),
        )
        latency_payload = run_latency_benchmark(
            latency_config,
            PROJECT_ROOT,
            max_cases=args.latency_cases,
            max_tokens=cap,
            target_names={args.target},
            warmup_cases=1,
            repetitions=1,
        )
        rows.append(
            {
                "max_tokens": cap,
                "eval_output_path": str(eval_path),
                "quality": eval_payload["summary"],
                "latency": latency_payload["leaderboard"][0]["summary"],
            }
        )
        write_json(output_dir / "summary.json", _summary(rows, args.target))


def _summary(rows: list[dict[str, object]], target: str) -> dict[str, object]:
    return {
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "target": target,
        "rows": rows,
    }


if __name__ == "__main__":
    main()
