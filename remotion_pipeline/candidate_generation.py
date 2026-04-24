from __future__ import annotations

from pathlib import Path
from typing import Any

from remotion_pipeline.case_records import DEFAULT_SYSTEM_PROMPT, prepare_cases
from remotion_pipeline.eval import extract_code
from remotion_pipeline.openrouter import generate_openrouter_result
from remotion_pipeline.render_check import run_remotion_check
from remotion_pipeline.types import (
    BenchmarkTargetConfig,
    GenerationConfig,
    OpenRouterConfig,
    RemotionRuntimeConfig,
)
from remotion_pipeline.utils import ensure_dir, load_records, slugify, write_json, write_jsonl

CANDIDATE_SYSTEM_PROMPT = (
    f"{DEFAULT_SYSTEM_PROMPT} Make the animation visually polished, deterministic, "
    "and self-contained. Do not use CSS transitions, external network data, browser globals, "
    "arbitrary third-party packages, or Remotion Composition registrations. Export the visual "
    "component itself, not a Root or Composition wrapper."
)


def generate_openrouter_candidate_batch(
    *,
    prompt_path: Path,
    models: list[str],
    output_dir: Path,
    repo_root: Path,
    generation: GenerationConfig,
    openrouter: OpenRouterConfig,
    runtime: RemotionRuntimeConfig,
    timeout_seconds: int,
    samples_per_prompt: int = 1,
    row_license: str = "pending-human-review",
    source_name: str = "openrouter-synthetic-candidates",
    render_enabled: bool = True,
    max_prompts: int = 0,
) -> dict[str, Any]:
    prompts = _load_prompt_specs(prompt_path)
    if max_prompts > 0:
        prompts = prompts[:max_prompts]

    renders_dir = ensure_dir(output_dir / "renders")
    cases: list[dict[str, Any]] = []
    verification: list[dict[str, Any]] = []
    for prompt in prompts:
        for model in models:
            for sample_index in range(1, samples_per_prompt + 1):
                case, check = _generate_one(
                    prompt=prompt,
                    model=model,
                    sample_index=sample_index,
                    source_name=source_name,
                    row_license=row_license,
                    output_dir=output_dir,
                    renders_dir=renders_dir,
                    repo_root=repo_root,
                    generation=generation,
                    openrouter=openrouter,
                    runtime=runtime,
                    timeout_seconds=timeout_seconds,
                    render_enabled=render_enabled,
                )
                cases.append(case)
                verification.append(check)

    prepared_cases = prepare_cases(cases, source_label=str(prompt_path))
    write_jsonl(output_dir / "candidates.jsonl", prepared_cases)
    write_jsonl(output_dir / "rating_queue.jsonl", [_rating_record(row) for row in prepared_cases])
    write_json(output_dir / "verification.json", _verification_payload(prompt_path, verification))
    _write_review_markdown(output_dir / "review.md", prepared_cases)
    return _verification_payload(prompt_path, verification)


def _load_prompt_specs(path: Path) -> list[dict[str, Any]]:
    records = load_records(path)
    prompts: list[dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record.get("prompt"), str) or not record["prompt"].strip():
            raise ValueError(f"Prompt record {index} is missing a non-empty prompt.")
        prompt_id = str(record.get("prompt_id") or record.get("case_id") or f"prompt-{index}")
        prompts.append({**record, "prompt_id": prompt_id})
    return prompts


def _generate_one(
    *,
    prompt: dict[str, Any],
    model: str,
    sample_index: int,
    source_name: str,
    row_license: str,
    output_dir: Path,
    renders_dir: Path,
    repo_root: Path,
    generation: GenerationConfig,
    openrouter: OpenRouterConfig,
    runtime: RemotionRuntimeConfig,
    timeout_seconds: int,
    render_enabled: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    target = BenchmarkTargetConfig(name=model, backend="openrouter", model=model)
    result = generate_openrouter_result(
        target=target,
        prompt=str(prompt["prompt"]),
        system_prompt=str(prompt.get("system") or CANDIDATE_SYSTEM_PROMPT),
        generation=generation,
        config=openrouter,
    )
    code = extract_code(result.text)
    case_id = _candidate_case_id(prompt["prompt_id"], model, sample_index)
    preview_path = renders_dir / f"{case_id}.{runtime.output_extension}"
    case = _candidate_case(
        prompt=prompt,
        model=model,
        source_name=source_name,
        row_license=row_license,
        case_id=case_id,
        code=code,
        result=result,
        sample_index=sample_index,
        preview_path=preview_path.relative_to(output_dir),
    )
    check = run_remotion_check(
        code=code,
        repo_root=repo_root,
        runtime=runtime,
        duration_in_frames=case["duration_in_frames"],
        fps=case["fps"],
        width=case["width"],
        height=case["height"],
        default_props=case["default_props"],
        timeout_seconds=timeout_seconds,
        render_enabled=render_enabled,
        artifact_output_path=preview_path if render_enabled else None,
    )
    required_ratio = _required_snippet_ratio(case)
    forbidden_ok = _forbidden_snippets_ok(case)
    case["candidate_compile_ok"] = check.compile_ok
    case["candidate_render_ok"] = check.render_ok
    case["candidate_required_snippet_ratio"] = required_ratio
    case["candidate_forbidden_ok"] = forbidden_ok
    if not check.compile_ok or check.render_ok is False or required_ratio < 1 or not forbidden_ok:
        case["candidate_status"] = "failed-verification"
    return case, {
        "case_id": case_id,
        "model": model,
        "compile_ok": check.compile_ok,
        "render_ok": check.render_ok,
        "required_snippet_ratio": required_ratio,
        "forbidden_ok": forbidden_ok,
        "preview_path": str(preview_path.relative_to(output_dir)),
        "compile_log_tail": check.compile_log_tail,
        "render_log_tail": check.render_log_tail,
    }


def _candidate_case(
    *,
    prompt: dict[str, Any],
    model: str,
    source_name: str,
    row_license: str,
    case_id: str,
    code: str,
    result: Any,
    sample_index: int,
    preview_path: Path,
) -> dict[str, Any]:
    usage = result.usage
    tags = ["openrouter-candidate", f"model:{slugify(model)}", *prompt.get("tags", [])]
    return {
        "case_id": case_id,
        "system": prompt.get("system", CANDIDATE_SYSTEM_PROMPT),
        "prompt": prompt["prompt"],
        "completion": f"{code.strip()}\n",
        "tags": tags,
        "must_contain": prompt.get("must_contain", []),
        "must_not_contain": prompt.get("must_not_contain", []),
        "duration_in_frames": prompt.get("duration_in_frames", 120),
        "fps": prompt.get("fps", 30),
        "width": prompt.get("width", 1280),
        "height": prompt.get("height", 720),
        "default_props": prompt.get("default_props", {}),
        "license": row_license,
        "source_name": source_name,
        "source_model": model,
        "source_rating": "unrated",
        "source_repo_path": "openrouter-generated",
        "synthetic_generation_method": "openrouter-generated-from-first-party-prompt",
        "prompt_id": prompt["prompt_id"],
        "candidate_batch": source_name,
        "candidate_status": "needs-human-rating",
        "candidate_compile_ok": None,
        "candidate_render_ok": None,
        "candidate_required_snippet_ratio": None,
        "candidate_forbidden_ok": None,
        "candidate_preview_path": str(preview_path),
        "rating_decision": "unrated",
        "human_rating": None,
        "human_notes": "",
        "generation_latency_ms": round(result.duration_seconds * 1000),
        "generation_first_token_ms": None,
        "generation_prompt_tokens": usage.get("prompt_tokens"),
        "generation_completion_tokens": usage.get("completion_tokens"),
        "generation_total_tokens": usage.get("total_tokens"),
        "openrouter_generation_id": result.response_id,
        "openrouter_response_model": result.response_model,
        "sample_index": sample_index,
    }


def _rating_record(case: dict[str, Any]) -> dict[str, Any]:
    return {**case, "human_rating": None, "rating_decision": "unrated", "human_notes": ""}


def _required_snippet_ratio(case: dict[str, Any]) -> float:
    required = case.get("must_contain", [])
    if not required:
        return 1.0
    return sum(1 for snippet in required if snippet in case["completion"]) / len(required)


def _forbidden_snippets_ok(case: dict[str, Any]) -> bool:
    return all(snippet not in case["completion"] for snippet in case.get("must_not_contain", []))


def _verification_payload(prompt_path: Path, verification: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(verification)
    return {
        "prompt_path": str(prompt_path),
        "summary": {
            "candidates": total,
            "compile_success_rate": _rate(verification, "compile_ok"),
            "render_success_rate": _rate(verification, "render_ok"),
        },
        "cases": verification,
    }


def _rate(rows: list[dict[str, Any]], key: str) -> float | None:
    attempts = [row for row in rows if row.get(key) is not None]
    return None if not attempts else sum(bool(row[key]) for row in attempts) / len(attempts)


def _candidate_case_id(prompt_id: str, model: str, sample_index: int) -> str:
    return f"cand-{slugify(prompt_id)}-{slugify(model)}-{sample_index}"


def _write_review_markdown(path: Path, cases: list[dict[str, Any]]) -> None:
    lines = ["# Candidate Review", "", "Edit `rating_queue.jsonl` after reviewing renders.", ""]
    for case in cases:
        lines.extend(
            [
                f"## {case['case_id']}",
                "",
                f"- Model: `{case['source_model']}`",
                f"- Preview: `{case['candidate_preview_path']}`",
                f"- Prompt: {case['prompt']}",
                "",
            ]
        )
    path.write_text("\n".join(lines))
