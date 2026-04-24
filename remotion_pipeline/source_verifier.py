from __future__ import annotations

from pathlib import Path
from typing import Any

from remotion_pipeline.case_records import prepare_cases
from remotion_pipeline.dataset_sources import load_source_records
from remotion_pipeline.render_check import run_remotion_check
from remotion_pipeline.types import DatasetSourceConfig, RemotionRuntimeConfig


def verify_source_cases(
    *,
    source: DatasetSourceConfig,
    repo_root: Path,
    runtime: RemotionRuntimeConfig,
    timeout_seconds: int,
    render_enabled: bool = True,
    max_cases: int = 0,
) -> dict[str, Any]:
    source_records, source_label = load_source_records(source)
    cases = prepare_cases(source_records, source_label=source_label)
    if max_cases > 0:
        cases = cases[:max_cases]

    results = [
        _verify_case(
            case=case,
            repo_root=repo_root,
            runtime=runtime,
            timeout_seconds=timeout_seconds,
            render_enabled=render_enabled,
        )
        for case in cases
    ]
    failures = [
        result
        for result in results
        if not result["compile_ok"] or result["render_ok"] is False
    ]
    total = len(results)
    compile_ok = sum(1 for result in results if result["compile_ok"])
    render_ok = sum(1 for result in results if result["render_ok"] is True)
    return {
        "source_dataset": source_label,
        "summary": {
            "cases": total,
            "compile_success_rate": compile_ok / total if total else 0,
            "render_success_rate": render_ok / total if render_enabled and total else None,
            "failure_count": len(failures),
        },
        "cases": results,
    }


def _verify_case(
    *,
    case: dict[str, Any],
    repo_root: Path,
    runtime: RemotionRuntimeConfig,
    timeout_seconds: int,
    render_enabled: bool,
) -> dict[str, Any]:
    result = run_remotion_check(
        code=case["completion"],
        repo_root=repo_root,
        runtime=runtime,
        duration_in_frames=case["duration_in_frames"],
        fps=case["fps"],
        width=case["width"],
        height=case["height"],
        default_props=case["default_props"],
        timeout_seconds=timeout_seconds,
        render_enabled=render_enabled,
    )
    return {
        "case_id": case["case_id"],
        "compile_ok": result.compile_ok,
        "render_ok": result.render_ok,
        "render_mode": result.render_mode,
        "component": result.export_info.component_name if result.export_info else None,
        "compile_log_tail": result.compile_log_tail,
        "render_log_tail": result.render_log_tail,
    }
