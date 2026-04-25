from remotion_pipeline.retry_eval import (
    _summarize,
    fixed_eval_primary_selector,
    fixed_eval_retry_selector,
    retry_generation_from_config,
)
from remotion_pipeline.types import GenerationConfig


def test_retry_summary_counts_total_attempt_costs() -> None:
    cases = [
        {
            "compile_ok": True,
            "render_ok": True,
            "weighted_score": 1.0,
            "selected_attempt_index": 0,
            "attempt_count": 1,
            "total_generation_tokens": 100,
            "total_generation_wall_seconds": 2.0,
            "generation_metrics": {
                "generation_tokens": 100,
                "hit_token_ceiling": False,
            },
        },
        {
            "compile_ok": True,
            "render_ok": True,
            "weighted_score": 0.9,
            "selected_attempt_index": 1,
            "attempt_count": 2,
            "total_generation_tokens": 240,
            "total_generation_wall_seconds": 5.0,
            "generation_metrics": {
                "generation_tokens": 90,
                "hit_token_ceiling": False,
            },
        },
    ]

    summary = _summarize(cases)

    assert summary["render_success_rate"] == 1.0
    assert summary["retry_rate"] == 0.5
    assert summary["mean_attempt_count"] == 1.5
    assert summary["mean_total_generation_tokens"] == 170
    assert summary["mean_total_generation_wall_seconds"] == 3.5


def test_retry_generation_overrides_sampling_only() -> None:
    generation = GenerationConfig(temperature=0.5, top_p=0.8, seed=42, max_tokens=900)

    retry = retry_generation_from_config(generation, temperature=0.6, top_p=0.75)

    assert retry.temperature == 0.6
    assert retry.top_p == 0.75
    assert retry.seed == 42
    assert retry.max_tokens == 900


def test_fixed_eval_adaptive_retry_routes_prompt_families() -> None:
    selector = fixed_eval_retry_selector(GenerationConfig(seed=42, max_tokens=900))

    kpi_retry = selector(_record("Create a Remotion KPI strip"), [])
    manufacturing_retry = selector(_record("Create a manufacturing OEE dashboard"), [])
    general_retry = selector(_record("Create a legal contract diff"), [])

    assert kpi_retry[0].seed == 123
    assert kpi_retry[0].temperature == 0.6
    assert len(kpi_retry) == 3
    assert kpi_retry[-1].max_tokens == 1200
    assert manufacturing_retry[0].temperature == 1.0
    assert manufacturing_retry[0].top_p == 0.8
    assert len(manufacturing_retry) == 3
    assert manufacturing_retry[-1].max_tokens == 1200
    assert general_retry[0].temperature == 0.6
    assert general_retry[0].seed == 42
    assert len(general_retry) == 3
    assert general_retry[-1].max_tokens == 1200


def test_fixed_eval_retry_uses_failure_quality_signals() -> None:
    selector = fixed_eval_retry_selector(GenerationConfig(seed=42, max_tokens=900))

    retry = selector(
        _record("Create a Remotion KPI strip"),
        [_attempt({"spring_missing_fps": True})],
    )

    assert retry[0].temperature == 1.0
    assert retry[0].max_tokens == 1200


def test_fixed_eval_primary_selector_routes_known_failure_families() -> None:
    generation = GenerationConfig(seed=42, max_tokens=900)
    selector = fixed_eval_primary_selector(generation)

    assert selector(_record("Create a Remotion KPI strip")).seed == 123
    assert selector(_record("Create a manufacturing OEE dashboard")).temperature == 1.0
    assert selector(_record("Create an AI trace with tool call nodes")).max_tokens == 1200
    assert selector(_record("Create a legal contract diff")).temperature == 0.6
    assert selector(_record("Create a finance dashboard with a revenue line")).temperature == 0.6
    assert selector(_record("Create an AI agent execution trace with plan cards")) == generation
    assert selector(_record("Create a simple radial progress badge")) == generation


def _record(prompt: str) -> dict:
    return {"messages": [{"role": "user", "content": prompt}]}


def _attempt(signals: dict) -> dict:
    return {"result": {"quality_signals": signals}}
