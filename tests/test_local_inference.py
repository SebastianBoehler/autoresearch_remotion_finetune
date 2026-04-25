from __future__ import annotations

import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from remotion_pipeline.local_inference import (
    _native_stop_reason,
    _should_stop_stream,
    clear_model_cache,
    generate_completion,
    generate_completion_result,
)
from remotion_pipeline.local_inference_cli import build_subprocess_command, parse_verbose_output
from remotion_pipeline.local_inference_types import LocalGenerationResult
from remotion_pipeline.types import GenerationConfig


class LocalInferenceTests(unittest.TestCase):
    def tearDown(self) -> None:
        clear_model_cache()

    def test_generate_completion_uses_in_process_transport_by_default(self) -> None:
        expected = LocalGenerationResult(text="export const Demo = () => null;", metrics=SimpleNamespace())
        with patch(
            "remotion_pipeline.local_inference._generate_in_process",
            return_value=expected,
        ) as mock_generate:
            text = generate_completion(
                base_model="demo/model",
                adapter_path=None,
                prompt="Build a chart.",
                system_prompt=None,
                generation=GenerationConfig(),
            )

        self.assertEqual(text, expected.text)
        mock_generate.assert_called_once()

    def test_generate_completion_result_routes_to_subprocess_transport(self) -> None:
        expected = LocalGenerationResult(text="export const Demo = () => null;", metrics=SimpleNamespace())
        with patch(
            "remotion_pipeline.local_inference._generate_subprocess",
            return_value=expected,
        ) as mock_generate:
            result = generate_completion_result(
                base_model="demo/model",
                adapter_path=Path("/tmp/adapter"),
                prompt="Build a chart.",
                system_prompt="Return TSX only.",
                generation=GenerationConfig(),
                transport="subprocess",
            )

        self.assertEqual(result.text, expected.text)
        mock_generate.assert_called_once()

    def test_parse_verbose_output_extracts_metrics(self) -> None:
        output = "\n".join(
            [
                "==========",
                "export const Demo = () => null;",
                "==========",
                "Prompt: 128 tokens, 512.500 tokens-per-sec",
                "Generation: 64 tokens, 128.250 tokens-per-sec",
                "Peak memory: 7.125 GB",
            ]
        )

        text, metrics = parse_verbose_output(output, wall_seconds=1.5)

        self.assertIn("export const Demo", text)
        self.assertEqual(metrics.transport, "subprocess")
        self.assertEqual(metrics.prompt_tokens, 128)
        self.assertEqual(metrics.generation_tokens, 64)
        self.assertAlmostEqual(metrics.end_to_end_generation_tokens_per_second, 64 / 1.5)

    def test_subprocess_command_includes_speculative_draft_args(self) -> None:
        command = build_subprocess_command(
            base_model="demo/model",
            adapter_path=Path("/tmp/adapter"),
            prompt="Build a chart.",
            system_prompt=None,
            generation=GenerationConfig(
                draft_model="demo/draft",
                num_draft_tokens=3,
            ),
        )

        self.assertIn("--draft-model", command)
        self.assertIn("demo/draft", command)
        self.assertIn("--num-draft-tokens", command)
        self.assertIn("3", command)

    def test_dynamic_stop_halts_complete_remotion_component(self) -> None:
        text = """import {AbsoluteFill} from 'remotion';

export const Demo = () => {
  return (
    <AbsoluteFill>
      <div>Ready</div>
    </AbsoluteFill>
  );
};
"""
        self.assertTrue(
            _should_stop_stream(
                [text],
                GenerationConfig(dynamic_remotion_stop=True, dynamic_stop_min_tokens=1),
                generation_tokens=128,
            )
        )

    def test_native_stop_reason_prefers_model_eos(self) -> None:
        self.assertEqual(
            _native_stop_reason("stop", 42, GenerationConfig(max_tokens=100)),
            "model_eos",
        )
        self.assertEqual(
            _native_stop_reason("length", 100, GenerationConfig(max_tokens=100)),
            "token_ceiling",
        )


if __name__ == "__main__":
    unittest.main()
