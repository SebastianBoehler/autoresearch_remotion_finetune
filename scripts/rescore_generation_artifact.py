from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from remotion_pipeline.eval import extract_code, score_case
from remotion_pipeline.types import ExperimentConfig
from remotion_pipeline.utils import load_records, resolve_path, write_json


def main() -> None:
    args = _parse_args()
    config = ExperimentConfig.load(resolve_path(PROJECT_ROOT, args.config))
    input_path = resolve_path(PROJECT_ROOT, args.input)
    artifact = json.loads(input_path.read_text())
    dataset_dir = _dataset_dir(args, artifact)
    records = _records_by_case_id(dataset_dir)
    cases = [
        _rescore_case(
            artifact_case=case,
            record=records[case["case_id"]],
            config=config,
        )
        for case in artifact["cases"]
        if case["case_id"] in records
    ]
    payload = {
        **{key: artifact.get(key) for key in ("run_name", "base_model", "adapter_path")},
        "dataset_dir": str(dataset_dir),
        "rescored_from": str(input_path),
        "summary": _summarize(cases),
        "cases": cases,
    }
    write_json(resolve_path(PROJECT_ROOT, args.output), payload)
    print(payload["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/qwen25coder_3b_remotion.json")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dataset-dir")
    return parser.parse_args()


def _dataset_dir(args: argparse.Namespace, artifact: dict[str, Any]) -> Path:
    raw = args.dataset_dir or artifact.get("dataset_dir")
    if not raw:
        raise ValueError("Missing dataset dir. Pass --dataset-dir or use an artifact with dataset_dir.")
    return resolve_path(PROJECT_ROOT, raw)


def _records_by_case_id(dataset_dir: Path) -> dict[str, dict[str, Any]]:
    return {record["case_id"]: record for record in load_records(dataset_dir / "test.jsonl")}


def _rescore_case(
    *,
    artifact_case: dict[str, Any],
    record: dict[str, Any],
    config: ExperimentConfig,
) -> dict[str, Any]:
    source_code = _source_code(artifact_case)
    scored = score_case(
        case=record,
        code=source_code,
        repo_root=PROJECT_ROOT,
        render_enabled=config.evaluation.run_render,
        weights=config.evaluation.metric_weights,
        runtime=config.evaluation.runtime,
        timeout_seconds=config.evaluation.max_render_seconds,
    )
    scored["raw_response"] = artifact_case.get("raw_response")
    scored["generated_code"] = source_code
    scored["code"] = scored["final_code"]
    scored["prompt"] = artifact_case.get("prompt")
    scored["system_prompt"] = artifact_case.get("system_prompt")
    scored["generation_metrics"] = artifact_case.get("generation_metrics", {})
    return scored


def _source_code(case: dict[str, Any]) -> str:
    if case.get("generated_code"):
        return case["generated_code"]
    if case.get("raw_response"):
        return extract_code(case["raw_response"])
    return case.get("code") or case.get("final_code") or ""


def _summarize(cases: list[dict[str, Any]]) -> dict[str, Any]:
    render_attempts = [case for case in cases if case["render_ok"] is not None]
    return {
        "num_cases": len(cases),
        "compile_success_rate": _rate(cases, "compile_ok"),
        "render_success_rate": _rate(render_attempts, "render_ok"),
        "mean_case_score": _mean([case["weighted_score"] for case in cases]),
        "quality_signal_counts": _quality_signal_counts(cases),
    }


def _rate(cases: list[dict[str, Any]], key: str) -> float | None:
    return None if not cases else sum(bool(case[key]) for case in cases) / len(cases)


def _mean(values: list[Any]) -> float | None:
    return None if not values else sum(float(value) for value in values) / len(values)


def _quality_signal_counts(cases: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for case in cases:
        signals = case.get("quality_signals", {})
        for key, value in signals.items():
            if key in {"ascii_only", "has_supported_export"}:
                continue
            if isinstance(value, bool) and value:
                counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


if __name__ == "__main__":
    main()
