from __future__ import annotations

from pathlib import Path
from typing import Any

from remotion_pipeline.types import RemotionRuntimeConfig

MAX_CANDIDATE_SOURCE_LINES = 300


def rating_record(case: dict[str, Any]) -> dict[str, Any]:
    return {**case, "human_rating": None, "rating_decision": "unrated", "human_notes": ""}


def required_snippet_ratio(case: dict[str, Any]) -> float:
    required = case.get("must_contain", [])
    if not required:
        return 1.0
    return sum(1 for snippet in required if snippet in case["completion"]) / len(required)


def forbidden_snippets_ok(case: dict[str, Any]) -> bool:
    return all(snippet not in case["completion"] for snippet in case.get("must_not_contain", []))


def source_line_count(code: str) -> int:
    stripped = code.strip()
    if not stripped:
        return 0
    return len(stripped.splitlines())


def preview_frame(case: dict[str, Any], runtime: RemotionRuntimeConfig) -> int:
    if runtime.render_mode != "still":
        return runtime.render_frame
    duration = int(case.get("duration_in_frames") or 90)
    return max(1, min(duration - 1, int(duration * 0.75)))


def runtime_with_preview_frame(
    runtime: RemotionRuntimeConfig,
    frame: int,
) -> RemotionRuntimeConfig:
    return RemotionRuntimeConfig(
        runner_dir=runtime.runner_dir,
        composition_id=runtime.composition_id,
        render_mode=runtime.render_mode,
        render_frame=frame,
        output_extension=runtime.output_extension,
    )


def verification_payload(prompt_path: Path, verification: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "prompt_path": str(prompt_path),
        "summary": {
            "candidates": len(verification),
            "compile_success_rate": _rate(verification, "compile_ok"),
            "render_success_rate": _rate(verification, "render_ok"),
            "line_count_success_rate": _rate(verification, "line_count_ok"),
            "ascii_success_rate": _rate(verification, "ascii_ok"),
            "verification_pass_rate": verification_pass_rate(verification),
        },
        "cases": verification,
    }


def verification_pass_rate(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    return sum(passes_verification(row) for row in rows) / len(rows)


def passes_verification(row: dict[str, Any]) -> bool:
    return (
        bool(row.get("compile_ok"))
        and row.get("render_ok") is not False
        and row.get("required_snippet_ratio") == 1
        and bool(row.get("forbidden_ok"))
        and bool(row.get("line_count_ok"))
        and bool(row.get("ascii_ok"))
    )


def write_review_markdown(path: Path, cases: list[dict[str, Any]]) -> None:
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


def _rate(rows: list[dict[str, Any]], key: str) -> float | None:
    attempts = [row for row in rows if row.get(key) is not None]
    return None if not attempts else sum(bool(row[key]) for row in attempts) / len(attempts)
