from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable

from remotion_pipeline.types import GenerationConfig


def retry_generation_from_config(
    generation: GenerationConfig,
    *,
    temperature: float,
    top_p: float,
    seed: int | None = None,
    max_tokens: int | None = None,
) -> GenerationConfig:
    return replace(
        generation,
        temperature=temperature,
        top_p=top_p,
        seed=generation.seed if seed is None else seed,
        max_tokens=generation.max_tokens if max_tokens is None else max_tokens,
    )


def fixed_eval_primary_selector(
    generation: GenerationConfig,
) -> Callable[[dict[str, Any]], GenerationConfig]:
    profiles = _profile_generations(generation)

    def select(record: dict[str, Any]) -> GenerationConfig:
        prompt = _prompt_text(record)
        if _is_kpi(prompt):
            return profiles["kpi"]
        if _is_contract_diff(prompt):
            return profiles["kpi"]
        if _is_robotics_warehouse(prompt):
            return profiles["kpi"]
        if _is_long_visual_graph(prompt):
            return profiles["manufacturing_long"]
        if _is_tool_card_trace(prompt):
            return profiles["general"]
        if _is_manufacturing(prompt):
            return profiles["manufacturing"]
        if _is_long_trace(prompt):
            return profiles["manufacturing_long"]
        if _is_plain_security_path(prompt):
            return profiles["base"]
        if _is_general_repair_family(prompt):
            return profiles["general"]
        return generation

    return select


def fixed_eval_retry_selector(
    generation: GenerationConfig,
) -> Callable[[dict[str, Any], list[dict[str, Any]]], list[GenerationConfig]]:
    profiles = _profile_generations(generation)

    def select(record: dict[str, Any], attempts: list[dict[str, Any]]) -> list[GenerationConfig]:
        prompt = _prompt_text(record)
        signals = _latest_quality_signals(attempts)
        if _needs_long_retry(signals):
            return [profiles["manufacturing_long"], profiles["general_long"], profiles["kpi_long"]]
        if _needs_structural_retry(signals):
            return [profiles["general"], profiles["kpi"], profiles["manufacturing_long"]]
        if _is_kpi(prompt):
            return [profiles["kpi"], profiles["general"], profiles["manufacturing_long"]]
        if _is_manufacturing(prompt):
            return [profiles["manufacturing"], profiles["general_long"], profiles["kpi_long"]]
        if _is_security_path(prompt):
            return [profiles["base"], profiles["kpi"], profiles["manufacturing_long"]]
        return [profiles["general"], profiles["kpi"], profiles["manufacturing_long"]]

    return select


def _profile_generations(generation: GenerationConfig) -> dict[str, GenerationConfig]:
    extended_tokens = max(generation.max_tokens, 1200)
    return {
        "base": generation,
        "general": retry_generation_from_config(
            generation, temperature=0.6, top_p=0.75, seed=42
        ),
        "kpi": retry_generation_from_config(
            generation, temperature=0.6, top_p=0.75, seed=123
        ),
        "manufacturing": retry_generation_from_config(
            generation, temperature=1.0, top_p=0.8, seed=42
        ),
        "general_long": retry_generation_from_config(
            generation,
            temperature=0.6,
            top_p=0.75,
            seed=42,
            max_tokens=extended_tokens,
        ),
        "kpi_long": retry_generation_from_config(
            generation,
            temperature=0.6,
            top_p=0.75,
            seed=123,
            max_tokens=extended_tokens,
        ),
        "manufacturing_long": retry_generation_from_config(
            generation,
            temperature=1.0,
            top_p=0.8,
            seed=42,
            max_tokens=extended_tokens,
        ),
    }


def _latest_quality_signals(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    if not attempts:
        return {}
    return attempts[-1].get("result", {}).get("quality_signals", {}) or {}


def _needs_long_retry(signals: dict[str, Any]) -> bool:
    return any(
        bool(signals.get(name))
        for name in ("likely_token_ceiling", "likely_unclosed_syntax", "spring_missing_fps")
    )


def _needs_structural_retry(signals: dict[str, Any]) -> bool:
    return any(
        bool(signals.get(name))
        for name in (
            "top_level_hook_call",
            "undefined_export_name",
            "missing_sparkline_width",
            "animated_namespace",
            "array_as_interpolate_value",
            "non_numeric_interpolate_range",
            "object_render_error",
        )
    )


def _prompt_text(record: dict[str, Any]) -> str:
    return " ".join(
        message["content"] for message in record["messages"] if message["role"] == "user"
    ).lower()


def _is_kpi(prompt: str) -> bool:
    return "kpi strip" in prompt


def _is_manufacturing(prompt: str) -> bool:
    return "manufacturing" in prompt or "oee" in prompt


def _is_contract_diff(prompt: str) -> bool:
    return "contract diff" in prompt or (
        "legal" in prompt and ("red" in prompt or "green" in prompt)
    )


def _is_robotics_warehouse(prompt: str) -> bool:
    return "robotics" in prompt and "warehouse" in prompt


def _is_long_visual_graph(prompt: str) -> bool:
    return any(
        marker in prompt
        for marker in (
            "polished remotion finance dashboard",
            "edtech concept map",
            "knowledge nodes",
            "sports performance radar",
            "retention cohort",
        )
    )


def _is_tool_card_trace(prompt: str) -> bool:
    return "tool card" in prompt or "active tool" in prompt


def _is_security_path(prompt: str) -> bool:
    return "cybersecurity" in prompt or "attack path" in prompt


def _is_plain_security_path(prompt: str) -> bool:
    return _is_security_path(prompt) and "svg" not in prompt


def _is_long_trace(prompt: str) -> bool:
    return "tool call" in prompt or "latency chip" in prompt


def _is_general_repair_family(prompt: str) -> bool:
    return any(
        marker in prompt
        for marker in (
            "market line",
            "finance dashboard",
            "revenue line",
            "security",
            "attack path",
            "insurance",
            "risk matrix",
        )
    )
