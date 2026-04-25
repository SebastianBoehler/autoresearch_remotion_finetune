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
        if _is_manufacturing(prompt):
            return profiles["manufacturing"]
        if _is_long_trace(prompt):
            return profiles["manufacturing_long"]
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
        if _is_kpi(prompt):
            return [profiles["kpi"], profiles["general"], profiles["manufacturing_long"]]
        if _is_manufacturing(prompt):
            return [profiles["manufacturing"], profiles["general_long"], profiles["kpi_long"]]
        return [profiles["general"], profiles["kpi"], profiles["manufacturing_long"]]

    return select


def _profile_generations(generation: GenerationConfig) -> dict[str, GenerationConfig]:
    extended_tokens = max(generation.max_tokens, 1200)
    return {
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


def _prompt_text(record: dict[str, Any]) -> str:
    return " ".join(
        message["content"] for message in record["messages"] if message["role"] == "user"
    ).lower()


def _is_kpi(prompt: str) -> bool:
    return "kpi strip" in prompt


def _is_manufacturing(prompt: str) -> bool:
    return "manufacturing" in prompt or "oee" in prompt


def _is_long_trace(prompt: str) -> bool:
    return "tool call" in prompt or "latency chip" in prompt


def _is_general_repair_family(prompt: str) -> bool:
    return any(
        marker in prompt
        for marker in (
            "market line",
            "finance dashboard",
            "revenue line",
            "contract diff",
            "legal",
            "security",
            "attack path",
            "insurance",
            "risk matrix",
        )
    )
