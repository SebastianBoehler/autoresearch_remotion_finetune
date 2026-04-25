from __future__ import annotations

import argparse
import json
import shutil
import statistics
from pathlib import Path
from typing import Any

from remotion_pipeline.candidate_quality import rating_record
from remotion_pipeline.utils import write_json, write_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-bank", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--source", action="append", required=True)
    parser.add_argument("--clean", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prompt_bank = Path(args.prompt_bank).resolve()
    output_dir = Path(args.output_dir).resolve()
    source_dirs = [Path(source).resolve() for source in args.source]
    merged = merge_verified_candidates(
        prompt_bank=prompt_bank,
        source_dirs=source_dirs,
        output_dir=output_dir,
        clean=args.clean,
    )
    print(json.dumps(merged["summary"], indent=2))
    print(f"Wrote merged review queue to {output_dir}")


def merge_verified_candidates(
    *,
    prompt_bank: Path,
    source_dirs: list[Path],
    output_dir: Path,
    clean: bool = False,
) -> dict[str, Any]:
    if clean and output_dir.exists():
        shutil.rmtree(output_dir)
    renders_dir = output_dir / "renders"
    renders_dir.mkdir(parents=True, exist_ok=True)

    prompt_order = _prompt_order(prompt_bank)
    by_prompt = _select_verified_by_prompt(source_dirs, output_dir, renders_dir)
    missing = [prompt_id for prompt_id in prompt_order if prompt_id not in by_prompt]
    if missing:
        raise RuntimeError(f"Missing verified candidates for prompts: {missing}")

    rows = [by_prompt[prompt_id] for prompt_id in prompt_order]
    write_jsonl(output_dir / "candidates.jsonl", rows)
    write_jsonl(output_dir / "rating_queue.jsonl", [rating_record(row) for row in rows])
    payload = _verification_payload(rows)
    write_json(output_dir / "verification.json", payload)
    _write_review(output_dir / "review.md", rows)
    return payload


def _prompt_order(path: Path) -> list[str]:
    prompt_ids: list[str] = []
    for index, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        prompt_id = row.get("prompt_id") or row.get("case_id")
        if not prompt_id:
            raise ValueError(f"Prompt row {index} is missing prompt_id.")
        prompt_ids.append(str(prompt_id))
    return prompt_ids


def _select_verified_by_prompt(
    source_dirs: list[Path],
    output_dir: Path,
    renders_dir: Path,
) -> dict[str, dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for source_dir in source_dirs:
        for row in _load_candidates(source_dir):
            row["candidate_ascii_ok"] = row["completion"].isascii()
            if not _candidate_passes(row) or row["prompt_id"] in selected:
                continue
            _copy_preview(row, source_dir, output_dir, renders_dir)
            row["candidate_status"] = "needs-human-rating"
            row["candidate_batch"] = output_dir.name
            selected[row["prompt_id"]] = row
    return selected


def _load_candidates(source_dir: Path) -> list[dict[str, Any]]:
    path = source_dir / "candidates.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"Candidate file does not exist: {path}")
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _candidate_passes(row: dict[str, Any]) -> bool:
    return (
        row.get("candidate_compile_ok") is True
        and row.get("candidate_render_ok") is True
        and row.get("candidate_required_snippet_ratio") == 1
        and row.get("candidate_forbidden_ok") is True
        and row.get("candidate_line_count_ok") is True
        and row.get("candidate_ascii_ok") is True
    )


def _copy_preview(
    row: dict[str, Any],
    source_dir: Path,
    output_dir: Path,
    renders_dir: Path,
) -> None:
    preview = source_dir / row["candidate_preview_path"]
    if not preview.exists():
        return
    destination = renders_dir / preview.name
    shutil.copy2(preview, destination)
    row["candidate_preview_path"] = str(destination.relative_to(output_dir))


def _verification_payload(rows: list[dict[str, Any]]) -> dict[str, Any]:
    cases = [_verification_case(row) for row in rows]
    return {
        "summary": {
            "candidates": len(rows),
            "compile_success_rate": 1.0,
            "render_success_rate": 1.0,
            "line_count_success_rate": 1.0,
            "ascii_success_rate": 1.0,
            "verification_pass_rate": 1.0,
            "mean_line_count": round(statistics.mean(row["candidate_line_count"] for row in rows), 1),
            "mean_generation_latency_ms": round(
                statistics.mean(row["generation_latency_ms"] for row in rows)
            ),
            "max_generation_latency_ms": max(row["generation_latency_ms"] for row in rows),
        },
        "cases": cases,
    }


def _verification_case(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": row["case_id"],
        "prompt_id": row["prompt_id"],
        "model": row["source_model"],
        "compile_ok": row["candidate_compile_ok"],
        "render_ok": row["candidate_render_ok"],
        "required_snippet_ratio": row["candidate_required_snippet_ratio"],
        "forbidden_ok": row["candidate_forbidden_ok"],
        "line_count": row["candidate_line_count"],
        "line_count_ok": row["candidate_line_count_ok"],
        "ascii_ok": row["candidate_ascii_ok"],
        "preview_path": row["candidate_preview_path"],
        "generation_latency_ms": row["generation_latency_ms"],
        "generation_completion_tokens": row.get("generation_completion_tokens"),
    }


def _write_review(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Candidate Review",
        "",
        "Merged verified OpenRouter candidates. Edit `rating_queue.jsonl` after reviewing renders.",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"## {row['case_id']}",
                "",
                f"- Model: `{row['source_model']}`",
                f"- Prompt ID: `{row['prompt_id']}`",
                f"- Lines: {row['candidate_line_count']}",
                f"- Latency: {row['generation_latency_ms']} ms",
                f"- Preview: `{row['candidate_preview_path']}`",
                f"- Prompt: {row['prompt']}",
                "",
            ]
        )
    path.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
