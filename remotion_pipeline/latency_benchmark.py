from __future__ import annotations

import math
from dataclasses import replace
from pathlib import Path
from statistics import mean, median
from typing import Any

from remotion_pipeline.benchmark_prompting import compose_system_prompt, load_target_skill
from remotion_pipeline.local_inference import generate_completion_result
from remotion_pipeline.target_generation import generation_for_target
from remotion_pipeline.types import BenchmarkConfig, BenchmarkTargetConfig
from remotion_pipeline.utils import ensure_dir, load_records, slugify, write_json


def run_latency_benchmark(
    benchmark: BenchmarkConfig,
    repo_root: Path,
    *,
    max_cases: int | None = None,
    max_tokens: int | None = None,
    target_names: set[str] | None = None,
    warmup_cases: int = 1,
    repetitions: int = 1,
) -> dict[str, Any]:
    if max_tokens is not None:
        benchmark = replace(
            benchmark,
            generation=replace(benchmark.generation, max_tokens=max_tokens),
        )
    dataset_dir = (repo_root / benchmark.dataset_dir).resolve()
    output_dir = ensure_dir((repo_root / benchmark.output_dir).resolve())
    records = load_records(dataset_dir / "test.jsonl")
    selected_limit = max_cases or benchmark.evaluation.max_cases or len(records)
    selected = records[:selected_limit]
    targets = [
        target
        for target in benchmark.targets
        if target_names is None or target.name in target_names
    ]
    if not targets:
        raise ValueError("No latency benchmark targets matched the requested filter.")

    target_results: list[dict[str, Any]] = []
    for target in targets:
        output_path = output_dir / f"{slugify(target.name)}-latency.json"
        try:
            payload = _benchmark_target(
                benchmark=benchmark,
                target=target,
                records=selected,
                repo_root=repo_root,
                warmup_cases=warmup_cases,
                repetitions=repetitions,
            )
            write_json(output_path, payload)
            target_results.append(_target_summary(target, payload, output_path))
        except Exception as exc:
            error_payload = _error_payload(benchmark, target, exc)
            write_json(output_path, error_payload)
            target_results.append(
                {
                    "name": target.name,
                    "backend": target.backend,
                    "model": target.model,
                    "local_transport": error_payload["local_transport"],
                    "draft_model": error_payload["draft_model"],
                    "num_draft_tokens": error_payload["num_draft_tokens"],
                    "skill_path": target.skill_path,
                    "output_path": str(output_path),
                    "error": str(exc),
                }
            )

    leaderboard = sorted(
        [item for item in target_results if "summary" in item],
        key=lambda item: (
            item["summary"].get("mean_wall_seconds", math.inf),
            item["summary"].get("mean_ttft_seconds", math.inf),
            -1.0
            * (item["summary"].get("mean_end_to_end_generation_tokens_per_second") or 0.0),
        ),
    )
    payload = {
        "name": benchmark.name,
        "dataset_dir": str(dataset_dir),
        "num_cases": len(selected),
        "max_tokens": benchmark.generation.max_tokens,
        "warmup_cases": warmup_cases,
        "repetitions": repetitions,
        "targets": target_results,
        "leaderboard": leaderboard,
    }
    write_json(output_dir / "latency-leaderboard.json", payload)
    return payload


def _benchmark_target(
    benchmark: BenchmarkConfig,
    target: BenchmarkTargetConfig,
    records: list[dict[str, Any]],
    repo_root: Path,
    *,
    warmup_cases: int,
    repetitions: int,
) -> dict[str, Any]:
    if target.backend != "local":
        raise ValueError("Latency benchmark currently supports only local targets.")

    transport = target.local_transport or benchmark.generation.local_transport
    generation = generation_for_target(benchmark.generation, target)
    adapter_path = (repo_root / target.adapter_path).resolve() if target.adapter_path else None
    skill_text, resolved_skill_path = load_target_skill(target, repo_root)

    for record in records[: min(warmup_cases, len(records))]:
        system_prompt, user_prompt = _record_prompts(record, skill_text)
        generate_completion_result(
            base_model=target.model,
            adapter_path=adapter_path,
            prompt=user_prompt,
            system_prompt=system_prompt,
            generation=generation,
            transport=transport,
        )

    case_results: list[dict[str, Any]] = []
    for repeat_index in range(repetitions):
        for record in records:
            system_prompt, user_prompt = _record_prompts(record, skill_text)
            result = generate_completion_result(
                base_model=target.model,
                adapter_path=adapter_path,
                prompt=user_prompt,
                system_prompt=system_prompt,
                generation=generation,
                transport=transport,
            )
            case_results.append(
                {
                    "case_id": record["case_id"],
                    "repeat_index": repeat_index,
                    "prompt_chars": len(user_prompt),
                    "response_chars": len(result.text),
                    **result.metrics.to_dict(),
                }
            )

    return {
        "run_name": target.name,
        "backend": target.backend,
        "model": target.model,
        "adapter_path": target.adapter_path,
        "local_transport": transport,
        "draft_model": generation.draft_model,
        "num_draft_tokens": generation.num_draft_tokens if generation.draft_model else None,
        "skill_path": resolved_skill_path,
        "summary": _summarize_case_results(case_results),
        "cases": case_results,
    }


def _record_prompts(record: dict[str, Any], skill_text: str | None) -> tuple[str | None, str]:
    base_system_prompt = next(
        (message["content"] for message in record["messages"] if message["role"] == "system"),
        None,
    )
    system_prompt = compose_system_prompt(base_system_prompt, skill_text)
    user_prompt = next(message["content"] for message in record["messages"] if message["role"] == "user")
    return system_prompt, user_prompt


def _target_summary(
    target: BenchmarkTargetConfig,
    payload: dict[str, Any],
    output_path: Path,
) -> dict[str, Any]:
    return {
        "name": target.name,
        "backend": target.backend,
        "model": target.model,
        "local_transport": payload["local_transport"],
        "draft_model": payload["draft_model"],
        "num_draft_tokens": payload["num_draft_tokens"],
        "skill_path": payload["skill_path"],
        "output_path": str(output_path),
        "summary": payload["summary"],
    }


def _error_payload(
    benchmark: BenchmarkConfig,
    target: BenchmarkTargetConfig,
    exc: Exception,
) -> dict[str, Any]:
    generation = generation_for_target(benchmark.generation, target)
    return {
        "run_name": target.name,
        "backend": target.backend,
        "model": target.model,
        "local_transport": target.local_transport or benchmark.generation.local_transport,
        "draft_model": generation.draft_model,
        "num_draft_tokens": generation.num_draft_tokens if generation.draft_model else None,
        "skill_path": target.skill_path,
        "error": str(exc),
    }


def _summarize_case_results(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {
        "num_samples": len(case_results),
        "mean_wall_seconds": _mean(_values(case_results, "wall_seconds")),
        "median_wall_seconds": _median(_values(case_results, "wall_seconds")),
        "p95_wall_seconds": _percentile(_values(case_results, "wall_seconds"), 0.95),
        "mean_ttft_seconds": _mean(_values(case_results, "ttft_seconds")),
        "median_ttft_seconds": _median(_values(case_results, "ttft_seconds")),
        "mean_prompt_tokens": _mean(_values(case_results, "prompt_tokens")),
        "mean_generation_tokens": _mean(_values(case_results, "generation_tokens")),
        "mean_prompt_tokens_per_second": _mean(_values(case_results, "prompt_tokens_per_second")),
        "mean_generation_tokens_per_second": _mean(_values(case_results, "generation_tokens_per_second")),
        "mean_end_to_end_generation_tokens_per_second": _mean(
            _values(case_results, "end_to_end_generation_tokens_per_second")
        ),
        "mean_peak_memory_gb": _mean(_values(case_results, "peak_memory_gb")),
        "token_ceiling_rate": _true_rate(case_results, "hit_token_ceiling"),
        "mean_draft_accept_rate": _mean(_values(case_results, "draft_accept_rate")),
    }
    summary["total_generation_tokens"] = sum(_values(case_results, "generation_tokens"))
    return summary


def _values(rows: list[dict[str, Any]], key: str) -> list[float]:
    return [row[key] for row in rows if row.get(key) is not None]


def _true_rate(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [row[key] for row in rows if row.get(key) is not None]
    return None if not values else sum(bool(value) for value in values) / len(values)


def _mean(values: list[float]) -> float | None:
    return mean(values) if values else None


def _median(values: list[float]) -> float | None:
    return median(values) if values else None


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)
