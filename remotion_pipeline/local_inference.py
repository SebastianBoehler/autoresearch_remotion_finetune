from __future__ import annotations

import subprocess
import time
from pathlib import Path
from threading import Lock
from typing import Any

from remotion_pipeline.local_inference_cli import build_subprocess_command, parse_verbose_output
from remotion_pipeline.local_inference_types import LocalGenerationMetrics, LocalGenerationResult
from remotion_pipeline.types import GenerationConfig

_MODEL_CACHE: dict[tuple[str, str | None], tuple[Any, Any]] = {}
_MODEL_CACHE_LOCK = Lock()


def clear_model_cache() -> None:
    with _MODEL_CACHE_LOCK:
        _MODEL_CACHE.clear()


def generate_completion(
    base_model: str,
    adapter_path: Path | None,
    prompt: str,
    system_prompt: str | None,
    generation: GenerationConfig,
    transport: str = "in_process",
) -> str:
    return generate_completion_result(
        base_model=base_model,
        adapter_path=adapter_path,
        prompt=prompt,
        system_prompt=system_prompt,
        generation=generation,
        transport=transport,
    ).text


def generate_completion_result(
    base_model: str,
    adapter_path: Path | None,
    prompt: str,
    system_prompt: str | None,
    generation: GenerationConfig,
    transport: str = "in_process",
) -> LocalGenerationResult:
    if transport == "in_process":
        return _generate_in_process(
            base_model=base_model,
            adapter_path=adapter_path,
            prompt=prompt,
            system_prompt=system_prompt,
            generation=generation,
        )
    if transport == "subprocess":
        return _generate_subprocess(
            base_model=base_model,
            adapter_path=adapter_path,
            prompt=prompt,
            system_prompt=system_prompt,
            generation=generation,
        )
    raise ValueError(f"Unsupported local transport: {transport}")


def _generate_subprocess(
    base_model: str,
    adapter_path: Path | None,
    prompt: str,
    system_prompt: str | None,
    generation: GenerationConfig,
) -> LocalGenerationResult:
    command = build_subprocess_command(
        base_model=base_model,
        adapter_path=adapter_path,
        prompt=prompt,
        system_prompt=system_prompt,
        generation=generation,
    )
    start = time.perf_counter()
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    wall_seconds = time.perf_counter() - start
    output = result.stdout.strip()
    if result.returncode != 0:
        error = output or result.stderr.strip() or "mlx_lm generate failed"
        raise RuntimeError(error)
    text, metrics = parse_verbose_output(output, wall_seconds)
    return LocalGenerationResult(text=text, metrics=metrics)


def _generate_in_process(
    base_model: str,
    adapter_path: Path | None,
    prompt: str,
    system_prompt: str | None,
    generation: GenerationConfig,
) -> LocalGenerationResult:
    model, tokenizer = _get_loaded_model(base_model, adapter_path)
    prompt_input, prompt_tokens = _prepare_prompt_input(tokenizer, prompt, system_prompt)
    sampler, mx, stream_generate = _build_runtime_handles(tokenizer, generation)
    mx.random.seed(generation.seed)

    start = time.perf_counter()
    first_token_seconds: float | None = None
    text_chunks: list[str] = []
    last_response = None
    for response in stream_generate(
        model,
        tokenizer,
        prompt_input,
        max_tokens=generation.max_tokens,
        sampler=sampler,
    ):
        if first_token_seconds is None:
            first_token_seconds = time.perf_counter() - start
        text_chunks.append(response.text)
        last_response = response

    wall_seconds = time.perf_counter() - start
    generation_tokens = 0
    prompt_tokens_per_second = None
    generation_tokens_per_second = None
    peak_memory_gb = None
    if last_response is not None:
        prompt_tokens = last_response.prompt_tokens
        generation_tokens = last_response.generation_tokens
        prompt_tokens_per_second = last_response.prompt_tps
        generation_tokens_per_second = last_response.generation_tps
        peak_memory_gb = last_response.peak_memory

    metrics = LocalGenerationMetrics(
        transport="in_process",
        wall_seconds=wall_seconds,
        ttft_seconds=first_token_seconds,
        prompt_tokens=prompt_tokens,
        prompt_tokens_per_second=prompt_tokens_per_second,
        generation_tokens=generation_tokens,
        generation_tokens_per_second=generation_tokens_per_second,
        end_to_end_generation_tokens_per_second=(
            generation_tokens / wall_seconds if wall_seconds > 0 else None
        ),
        peak_memory_gb=peak_memory_gb,
    )
    return LocalGenerationResult(text="".join(text_chunks), metrics=metrics)


def _get_loaded_model(
    base_model: str,
    adapter_path: Path | None,
) -> tuple[Any, Any]:
    cache_key = (base_model, str(adapter_path) if adapter_path is not None else None)
    with _MODEL_CACHE_LOCK:
        cached = _MODEL_CACHE.get(cache_key)
        if cached is not None:
            return cached

    load, _, _ = _import_mlx_runtime()
    loaded = load(
        base_model,
        adapter_path=str(adapter_path) if adapter_path is not None else None,
    )
    with _MODEL_CACHE_LOCK:
        _MODEL_CACHE[cache_key] = loaded
    return loaded


def _prepare_prompt_input(
    tokenizer: Any,
    prompt: str,
    system_prompt: str | None,
) -> tuple[str | list[int], int]:
    if getattr(tokenizer, "has_chat_template", False):
        messages: list[dict[str, str]] = []
        if system_prompt is not None:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        rendered_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            continue_final_message=False,
            add_generation_prompt=True,
        )
        prompt_tokens = tokenizer.encode(rendered_prompt, add_special_tokens=False)
        return prompt_tokens, len(prompt_tokens)

    prompt_tokens = _encode_text(tokenizer, prompt)
    return prompt, len(prompt_tokens)


def _build_runtime_handles(
    tokenizer: Any,
    generation: GenerationConfig,
) -> tuple[Any, Any, Any]:
    _, stream_generate, make_sampler = _import_mlx_runtime()
    import mlx.core as mx

    sampler = make_sampler(
        generation.temperature,
        generation.top_p,
        0.0,
        1,
        top_k=generation.top_k,
        xtc_probability=0.0,
        xtc_threshold=0.0,
        xtc_special_tokens=_encode_text(tokenizer, "\n") + list(tokenizer.eos_token_ids),
    )
    return sampler, mx, stream_generate


def _encode_text(tokenizer: Any, text: str) -> list[int]:
    add_special_tokens = getattr(tokenizer, "bos_token", None) is None or not text.startswith(
        getattr(tokenizer, "bos_token", "") or ""
    )
    try:
        return list(tokenizer.encode(text, add_special_tokens=add_special_tokens))
    except TypeError:
        return list(tokenizer.encode(text))


def _import_mlx_runtime() -> tuple[Any, Any, Any]:
    try:
        from mlx_lm import load, stream_generate
        from mlx_lm.sample_utils import make_sampler
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Local MLX inference requires `mlx_lm`. Install the repo environment with `uv sync`."
        ) from exc
    return load, stream_generate, make_sampler
