from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from remotion_pipeline.local_inference import generate_completion
from remotion_pipeline.mlx import evaluate_loss
from remotion_pipeline.render_check import normalize_generated_code, run_remotion_check
from remotion_pipeline.types import ExperimentConfig, MetricWeights
from remotion_pipeline.utils import load_records, write_json

CODE_BLOCK_PATTERN = re.compile(r"```(?:tsx|ts|jsx|js)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_code(text: str) -> str:
    match = CODE_BLOCK_PATTERN.search(text)
    return match.group(1).strip() if match else text.strip()


def score_case(
    *,
    case: dict[str, Any],
    code: str,
    repo_root: Path,
    render_enabled: bool,
    weights: MetricWeights,
    runtime,
    timeout_seconds: int,
) -> dict[str, Any]:
    normalized_code = normalize_generated_code(code)
    check = run_remotion_check(
        code=normalized_code,
        repo_root=repo_root,
        runtime=runtime,
        duration_in_frames=case.get("duration_in_frames", 90),
        fps=case.get("fps", 30),
        width=case.get("width", 1280),
        height=case.get("height", 720),
        default_props=case.get("default_props", {}),
        timeout_seconds=timeout_seconds,
        render_enabled=render_enabled,
    )

    required = case.get("must_contain", [])
    required_ratio = (
        sum(1 for snippet in required if snippet in normalized_code) / len(required)
        if required
        else 1.0
    )
    forbidden = case.get("must_not_contain", [])
    forbidden_ok = all(snippet not in normalized_code for snippet in forbidden)

    enabled_weights = {
        "compile": weights.compile,
        "component_export": weights.component_export,
        "required_snippets": weights.required_snippets,
        "forbidden_snippets": weights.forbidden_snippets,
    }
    if check.render_ok is not None:
        enabled_weights["render"] = weights.render
    total_weight = sum(enabled_weights.values()) or 1.0
    weighted_score = (
        enabled_weights["compile"] * float(check.compile_ok)
        + enabled_weights["component_export"] * float(check.export_info is not None)
        + enabled_weights["required_snippets"] * required_ratio
        + enabled_weights["forbidden_snippets"] * float(forbidden_ok)
        + enabled_weights.get("render", 0.0) * float(bool(check.render_ok))
    ) / total_weight

    return {
        "case_id": case["case_id"],
        "compile_ok": check.compile_ok,
        "component_name": (
            check.export_info.component_name if check.export_info is not None else None
        ),
        "uses_default_export": (
            check.export_info.uses_default_export
            if check.export_info is not None
            else None
        ),
        "required_snippet_ratio": required_ratio,
        "forbidden_ok": forbidden_ok,
        "render_ok": check.render_ok,
        "compile_log_tail": check.compile_log_tail,
        "render_log_tail": check.render_log_tail,
        "weighted_score": weighted_score,
        "final_code": normalized_code,
        "render_mode": check.render_mode,
    }


def evaluate_adapter(
    *,
    config: ExperimentConfig,
    repo_root: Path,
    dataset_dir: Path,
    adapter_path: Path | None,
    output_path: Path,
) -> dict[str, Any]:
    records = load_records(dataset_dir / "test.jsonl")
    max_cases = config.evaluation.max_cases or len(records)
    selected = records[:max_cases]
    per_case: list[dict[str, Any]] = []
    for record in selected:
        system_prompt = next(
            (message["content"] for message in record["messages"] if message["role"] == "system"),
            None,
        )
        user_prompt = next(
            message["content"] for message in record["messages"] if message["role"] == "user"
        )
        raw_response = generate_completion(
            base_model=config.base_model,
            adapter_path=adapter_path,
            prompt=user_prompt,
            system_prompt=system_prompt,
            generation=config.generation,
            transport=config.generation.local_transport,
        )
        code = extract_code(raw_response)
        case_result = score_case(
            case=record,
            code=code,
            repo_root=repo_root,
            render_enabled=config.evaluation.run_render,
            weights=config.evaluation.metric_weights,
            runtime=config.evaluation.runtime,
            timeout_seconds=config.evaluation.max_render_seconds,
        )
        case_result["raw_response"] = raw_response
        case_result["generated_code"] = code
        case_result["code"] = case_result["final_code"]
        case_result["prompt"] = user_prompt
        case_result["system_prompt"] = system_prompt
        per_case.append(case_result)

    compile_rate = sum(item["compile_ok"] for item in per_case) / len(per_case)
    render_attempts = [item for item in per_case if item["render_ok"] is not None]
    render_rate = (
        sum(item["render_ok"] for item in render_attempts) / len(render_attempts)
        if render_attempts
        else None
    )
    mean_case_score = sum(item["weighted_score"] for item in per_case) / len(per_case)

    payload = {
        "run_name": config.name,
        "base_model": config.base_model,
        "adapter_path": str(adapter_path) if adapter_path is not None else None,
        "dataset_dir": str(dataset_dir),
        "summary": {
            "num_cases": len(per_case),
            "compile_success_rate": compile_rate,
            "render_success_rate": render_rate,
            "mean_case_score": mean_case_score,
        },
        "cases": per_case,
    }
    if config.run_loss_eval:
        payload["summary"].update(
            evaluate_loss(
                config=config,
                dataset_dir=dataset_dir,
                adapter_path=adapter_path,
                log_path=output_path.with_suffix(".loss.log"),
            )
        )
    write_json(output_path, payload)
    return payload
