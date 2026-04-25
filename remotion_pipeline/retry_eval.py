from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from remotion_pipeline.eval import extract_code, score_case
from remotion_pipeline.local_inference import generate_completion_result
from remotion_pipeline.retry_profiles import (
    fixed_eval_primary_selector,
    fixed_eval_retry_selector,
    retry_generation_from_config,
)
from remotion_pipeline.types import ExperimentConfig, GenerationConfig
from remotion_pipeline.utils import load_records, write_json


def evaluate_with_verified_retries(
    *,
    config: ExperimentConfig,
    repo_root: Path,
    dataset_dir: Path,
    adapter_path: Path | None,
    output_path: Path,
    retry_generations: list[GenerationConfig],
    retry_selector: Callable[[dict[str, Any], list[dict[str, Any]]], list[GenerationConfig]] | None = None,
    primary_selector: Callable[[dict[str, Any]], GenerationConfig] | None = None,
) -> dict[str, Any]:
    records = load_records(dataset_dir / "test.jsonl")
    selected_records = records[: config.evaluation.max_cases or len(records)]
    cases = [
        _evaluate_case(
            record=record,
            config=config,
            repo_root=repo_root,
            adapter_path=adapter_path,
            retry_generations=retry_generations,
            retry_selector=retry_selector,
            primary_selector=primary_selector,
        )
        for record in selected_records
    ]
    payload = {
        "run_name": config.name,
        "base_model": config.base_model,
        "adapter_path": str(adapter_path) if adapter_path is not None else None,
        "dataset_dir": str(dataset_dir),
        "summary": _summarize(cases),
        "cases": cases,
    }
    write_json(output_path, payload)
    return payload


def _evaluate_case(
    *,
    record: dict[str, Any],
    config: ExperimentConfig,
    repo_root: Path,
    adapter_path: Path | None,
    retry_generations: list[GenerationConfig],
    retry_selector: Callable[[dict[str, Any], list[dict[str, Any]]], list[GenerationConfig]] | None,
    primary_selector: Callable[[dict[str, Any]], GenerationConfig] | None,
) -> dict[str, Any]:
    system_prompt = next(
        (message["content"] for message in record["messages"] if message["role"] == "system"),
        None,
    )
    user_prompt = next(message["content"] for message in record["messages"] if message["role"] == "user")
    attempts: list[dict[str, Any]] = []
    best_attempt: dict[str, Any] | None = None
    index = 0
    primary_generation = primary_selector(record) if primary_selector else config.generation
    attempted_generations = {_generation_signature(primary_generation)}
    attempt = _run_attempt(
        record=record,
        generation=primary_generation,
        attempt_index=0,
        config=config,
        repo_root=repo_root,
        adapter_path=adapter_path,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
    attempts.append(attempt)
    if _passes_verification(attempt):
        best_attempt = attempt
    if (
        best_attempt is None
        or attempt["result"]["weighted_score"] > best_attempt["result"]["weighted_score"]
    ):
        best_attempt = attempt
    selected_retries = retry_selector(record, attempts) if retry_selector else retry_generations
    for generation in selected_retries:
        if best_attempt is not None and _passes_verification(best_attempt):
            break
        signature = _generation_signature(generation)
        if signature in attempted_generations:
            continue
        attempted_generations.add(signature)
        index += 1
        attempt = _run_attempt(
            record=record,
            generation=generation,
            attempt_index=index,
            config=config,
            repo_root=repo_root,
            adapter_path=adapter_path,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        attempts.append(attempt)
        if (
            best_attempt is None
            or attempt["result"]["weighted_score"] > best_attempt["result"]["weighted_score"]
        ):
            best_attempt = attempt
        if _passes_verification(attempt):
            break
    if best_attempt is None:
        raise ValueError(f"No retry attempts were run for case {record['case_id']}")
    selected = best_attempt
    return {
        **selected["result"],
        "prompt": user_prompt,
        "system_prompt": system_prompt,
        "selected_attempt_index": selected["attempt_index"],
        "attempt_count": len(attempts),
        "total_generation_wall_seconds": sum(
            attempt["result"]["generation_metrics"].get("wall_seconds") or 0
            for attempt in attempts
        ),
        "total_generation_tokens": sum(
            attempt["result"]["generation_metrics"].get("generation_tokens") or 0
            for attempt in attempts
        ),
        "attempts": attempts,
    }


def _run_attempt(
    *,
    record: dict[str, Any],
    generation: GenerationConfig,
    attempt_index: int,
    config: ExperimentConfig,
    repo_root: Path,
    adapter_path: Path | None,
    system_prompt: str | None,
    user_prompt: str,
) -> dict[str, Any]:
    generation_result = generate_completion_result(
        base_model=config.base_model,
        adapter_path=adapter_path,
        prompt=user_prompt,
        system_prompt=system_prompt,
        generation=generation,
        transport=generation.local_transport,
    )
    raw_response = generation_result.text
    code = extract_code(raw_response)
    result = score_case(
        case=record,
        code=code,
        repo_root=repo_root,
        render_enabled=config.evaluation.run_render,
        weights=config.evaluation.metric_weights,
        runtime=config.evaluation.runtime,
        timeout_seconds=config.evaluation.max_render_seconds,
    )
    result["raw_response"] = raw_response
    result["generated_code"] = code
    result["code"] = result["final_code"]
    result["generation_metrics"] = generation_result.metrics.to_dict()
    return {
        "attempt_index": attempt_index,
        "generation": generation.to_dict() if hasattr(generation, "to_dict") else vars(generation),
        "result": result,
    }


def _passes_verification(attempt: dict[str, Any]) -> bool:
    result = attempt["result"]
    return bool(result["compile_ok"] and result["render_ok"] is not False)


def _generation_signature(generation: GenerationConfig) -> tuple[Any, ...]:
    return (
        generation.max_tokens,
        generation.temperature,
        generation.top_p,
        generation.top_k,
        generation.seed,
        generation.draft_model,
        generation.num_draft_tokens,
    )


def _summarize(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "num_cases": len(cases),
        "compile_success_rate": _rate(cases, "compile_ok"),
        "render_success_rate": _rate(
            [case for case in cases if case["render_ok"] is not None],
            "render_ok",
        ),
        "mean_case_score": _mean([case["weighted_score"] for case in cases]),
        "retry_rate": _mean([case["selected_attempt_index"] > 0 for case in cases]),
        "mean_attempt_count": _mean([case["attempt_count"] for case in cases]),
        "mean_selected_generation_tokens": _metric_mean(cases, "generation_tokens"),
        "mean_total_generation_tokens": _mean([case["total_generation_tokens"] for case in cases]),
        "mean_total_generation_wall_seconds": _mean(
            [case["total_generation_wall_seconds"] for case in cases]
        ),
        "token_ceiling_rate": _metric_true_rate(cases, "hit_token_ceiling"),
    }


def _metric_values(cases: list[dict[str, Any]], key: str) -> list[Any]:
    return [
        case["generation_metrics"][key]
        for case in cases
        if case.get("generation_metrics", {}).get(key) is not None
    ]


def _metric_mean(cases: list[dict[str, Any]], key: str) -> float | None:
    return _mean(_metric_values(cases, key))


def _metric_true_rate(cases: list[dict[str, Any]], key: str) -> float | None:
    values = _metric_values(cases, key)
    return None if not values else sum(bool(value) for value in values) / len(values)


def _rate(cases: list[dict[str, Any]], key: str) -> float | None:
    return None if not cases else sum(bool(case[key]) for case in cases) / len(cases)


def _mean(values: list[Any]) -> float | None:
    return None if not values else sum(float(value) for value in values) / len(values)
