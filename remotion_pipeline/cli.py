from __future__ import annotations

import argparse
from pathlib import Path

from remotion_pipeline.benchmark import run_benchmark
from remotion_pipeline.cli_candidates import register_candidate_commands
from remotion_pipeline.cli_latency import register_latency_commands
from remotion_pipeline.compare import compare_runs
from remotion_pipeline.dataset import build_dataset
from remotion_pipeline.dataset_sources import resolve_dataset_source
from remotion_pipeline.eval import evaluate_adapter
from remotion_pipeline.hf_dataset import export_hf_dataset
from remotion_pipeline.mlx import train_adapter
from remotion_pipeline.source_verifier import verify_source_cases
from remotion_pipeline.types import BenchmarkConfig, ExperimentConfig
from remotion_pipeline.utils import append_tsv, resolve_path, write_json

RESULT_FIELDS = [
    "run_name",
    "base_model",
    "test_loss",
    "test_perplexity",
    "compile_success_rate",
    "render_success_rate",
    "mean_case_score",
    "adapter_path",
    "eval_output_path",
]


def _load_config(config_path: Path) -> tuple[ExperimentConfig, Path]:
    resolved = config_path.resolve()
    return ExperimentConfig.load(resolved), resolved.parent.parent


def _require_path(path: Path, description: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{description} does not exist: {path}")


def _resolve_source_from_args(
    repo_root: Path,
    source_config,
    args: argparse.Namespace,
):
    return resolve_dataset_source(
        base_dir=repo_root,
        source=source_config,
        override=getattr(args, "source", None),
        override_kind=getattr(args, "source_kind", None),
        override_config_name=getattr(args, "source_config_name", None),
        override_split=getattr(args, "source_split", None),
        override_revision=getattr(args, "source_revision", None),
    )


def _append_results(config: ExperimentConfig, repo_root: Path, payload: dict) -> None:
    summary = payload["summary"]
    append_tsv(
        resolve_path(repo_root, config.results_tsv),
        {
            "run_name": config.name,
            "base_model": config.base_model,
            "test_loss": summary.get("test_loss"),
            "test_perplexity": summary.get("test_perplexity"),
            "compile_success_rate": summary.get("compile_success_rate"),
            "render_success_rate": summary.get("render_success_rate"),
            "mean_case_score": summary.get("mean_case_score"),
            "adapter_path": payload["adapter_path"],
            "eval_output_path": str(resolve_path(repo_root, config.eval_output_path)),
        },
        RESULT_FIELDS,
    )


def cmd_build_dataset(args: argparse.Namespace) -> None:
    config, repo_root = _load_config(Path(args.config))
    source = _resolve_source_from_args(repo_root, config.source_dataset, args)
    dataset_dir = resolve_path(repo_root, config.dataset_dir)
    manifest = build_dataset(source, dataset_dir, config.splits, config.dataset_filter)
    print(f"Built dataset at {dataset_dir}")
    print(manifest)


def cmd_train(args: argparse.Namespace) -> None:
    config, repo_root = _load_config(Path(args.config))
    dataset_dir = resolve_path(repo_root, config.dataset_dir)
    _require_path(dataset_dir / "train.jsonl", "Training split")
    _require_path(dataset_dir / "valid.jsonl", "Validation split")
    adapter_path = resolve_path(repo_root, config.adapter_path)
    log_path = adapter_path.parent / f"{adapter_path.name}.train.log"
    train_adapter(config, dataset_dir, adapter_path, log_path)
    print(f"Training complete. Adapter saved to {adapter_path}")
    print(f"Training log: {log_path}")


def cmd_eval(args: argparse.Namespace) -> None:
    config, repo_root = _load_config(Path(args.config))
    if args.base_only:
        config.run_loss_eval = False
    dataset_dir = resolve_path(repo_root, config.dataset_dir)
    _require_path(dataset_dir / "test.jsonl", "Test split")
    adapter_path = None
    if not args.base_only:
        adapter_path = resolve_path(repo_root, config.adapter_path)
        _require_path(adapter_path, "Adapter path")
    output_path = resolve_path(repo_root, args.output or config.eval_output_path)
    payload = evaluate_adapter(
        config=config,
        repo_root=repo_root,
        dataset_dir=dataset_dir,
        adapter_path=adapter_path,
        output_path=output_path,
    )
    if not args.base_only:
        _append_results(config, repo_root, payload)
    print(f"Evaluation written to {output_path}")
    print(payload["summary"])


def cmd_run(args: argparse.Namespace) -> None:
    config, repo_root = _load_config(Path(args.config))
    source = _resolve_source_from_args(repo_root, config.source_dataset, args)
    dataset_dir = resolve_path(repo_root, config.dataset_dir)
    adapter_path = resolve_path(repo_root, config.adapter_path)
    output_path = resolve_path(repo_root, config.eval_output_path)
    build_dataset(source, dataset_dir, config.splits, config.dataset_filter)
    train_adapter(
        config,
        dataset_dir,
        adapter_path,
        adapter_path.parent / f"{adapter_path.name}.train.log",
    )
    payload = evaluate_adapter(
        config=config,
        repo_root=repo_root,
        dataset_dir=dataset_dir,
        adapter_path=adapter_path,
        output_path=output_path,
    )
    _append_results(config, repo_root, payload)
    print(f"Full run complete for {config.name}")
    print(payload["summary"])


def cmd_compare(args: argparse.Namespace) -> None:
    config, repo_root = _load_config(Path(args.config))
    result = compare_runs(
        baseline_path=resolve_path(repo_root, args.baseline),
        candidate_path=resolve_path(repo_root, args.candidate),
        min_loss_delta=config.evaluation.min_loss_delta,
        tie_loss_delta=config.evaluation.tie_loss_delta,
        allowed_render_regression=config.evaluation.allowed_render_regression,
    )
    output_path = resolve_path(repo_root, args.output)
    write_json(output_path, result)
    print(f"Comparison written to {output_path}")
    print(result)


def cmd_benchmark(args: argparse.Namespace) -> None:
    config_path = Path(args.config).resolve()
    benchmark = BenchmarkConfig.load(config_path)
    repo_root = config_path.parent.parent
    payload = run_benchmark(benchmark, repo_root)
    print(f"Benchmark written to {resolve_path(repo_root, benchmark.output_dir) / 'leaderboard.json'}")
    for index, entry in enumerate(payload["leaderboard"], start=1):
        summary = entry["summary"]
        print(
            f"{index}. {entry['name']} "
            f"(score={summary.get('mean_case_score'):.3f}, "
            f"render={summary.get('render_success_rate')}, "
            f"compile={summary.get('compile_success_rate'):.3f})"
        )


def cmd_export_hf_dataset(args: argparse.Namespace) -> None:
    config, repo_root = _load_config(Path(args.config))
    source = _resolve_source_from_args(repo_root, config.source_dataset, args)
    output_dir = Path(args.output_dir).resolve()
    payload = export_hf_dataset(
        source=source,
        output_dir=output_dir,
        split_config=config.splits,
        dataset_filter=config.dataset_filter,
        repo_id=args.repo_id,
        pretty_name=args.pretty_name,
        license_name=args.license,
        languages=args.language or [],
        task_categories=args.task_category or [],
        size_categories=args.size_category or [],
        tags=args.tag or [],
    )
    print(f"Exported HF dataset staging folder to {output_dir}")
    print(payload)


def cmd_verify_source(args: argparse.Namespace) -> None:
    config, repo_root = _load_config(Path(args.config))
    source = _resolve_source_from_args(repo_root, config.source_dataset, args)
    payload = verify_source_cases(
        source=source,
        repo_root=repo_root,
        runtime=config.evaluation.runtime,
        timeout_seconds=config.evaluation.max_render_seconds,
        render_enabled=not args.no_render,
        max_cases=args.max_cases,
    )
    if args.output:
        output_path = resolve_path(repo_root, args.output)
        write_json(output_path, payload)
        print(f"Source verification written to {output_path}")
    print(payload["summary"])
    if payload["summary"]["failure_count"]:
        raise SystemExit(1)


def _add_source_override_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source")
    parser.add_argument("--source-kind", choices=["local", "hf"])
    parser.add_argument("--source-config-name")
    parser.add_argument("--source-split")
    parser.add_argument("--source-revision")


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m remotion_pipeline.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in (
        "build-dataset",
        "train",
        "eval",
        "run",
        "benchmark",
        "export-hf-dataset",
        "verify-source",
    ):
        subparser = subparsers.add_parser(name)
        subparser.add_argument("--config", required=True)
        if name in {"build-dataset", "run", "export-hf-dataset", "verify-source"}:
            _add_source_override_args(subparser)
        if name == "eval":
            subparser.add_argument("--base-only", action="store_true")
            subparser.add_argument("--output")
        if name == "export-hf-dataset":
            subparser.add_argument("--output-dir", required=True)
            subparser.add_argument("--repo-id")
            subparser.add_argument("--pretty-name")
            subparser.add_argument("--license")
            subparser.add_argument("--language", action="append")
            subparser.add_argument("--task-category", action="append")
            subparser.add_argument("--size-category", action="append")
            subparser.add_argument("--tag", action="append")
        if name == "verify-source":
            subparser.add_argument("--output")
            subparser.add_argument("--max-cases", type=int, default=0)
            subparser.add_argument("--no-render", action="store_true")
    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--config", required=True)
    compare_parser.add_argument("--baseline", required=True)
    compare_parser.add_argument("--candidate", required=True)
    compare_parser.add_argument("--output", required=True)
    commands = {
        "build-dataset": cmd_build_dataset,
        "train": cmd_train,
        "eval": cmd_eval,
        "run": cmd_run,
        "compare": cmd_compare,
        "benchmark": cmd_benchmark,
        "export-hf-dataset": cmd_export_hf_dataset,
        "verify-source": cmd_verify_source,
    }
    register_candidate_commands(subparsers, commands)
    register_latency_commands(subparsers, commands)

    args = parser.parse_args()
    commands[args.command](args)


if __name__ == "__main__":
    main()
