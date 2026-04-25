from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from remotion_pipeline.latency_benchmark import run_latency_benchmark
from remotion_pipeline.local_inference_types import LocalGenerationMetrics, LocalGenerationResult
from remotion_pipeline.types import BenchmarkConfig, BenchmarkTargetConfig, EvaluationConfig
from remotion_pipeline.utils import write_jsonl


class LatencyBenchmarkTests(unittest.TestCase):
    def test_writes_latency_leaderboard_for_local_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            dataset_dir = root / "dataset"
            dataset_dir.mkdir()
            write_jsonl(
                dataset_dir / "test.jsonl",
                [
                    {
                        "case_id": "case-a",
                        "messages": [
                            {"role": "system", "content": "Return TSX only."},
                            {"role": "user", "content": "Build a chart."},
                            {"role": "assistant", "content": "export const Demo = () => null;"},
                        ],
                    }
                ],
            )
            benchmark = BenchmarkConfig(
                name="latency",
                dataset_dir="dataset",
                output_dir="out",
                evaluation=EvaluationConfig(max_cases=1),
                targets=[
                    BenchmarkTargetConfig(
                        name="local",
                        backend="local",
                        model="demo/model",
                        draft_model="demo/draft",
                        num_draft_tokens=3,
                    )
                ],
            )
            result = LocalGenerationResult(
                text="export const Demo = () => null;",
                metrics=LocalGenerationMetrics(
                    transport="in_process",
                    wall_seconds=0.5,
                    ttft_seconds=0.1,
                    generation_tokens=50,
                    end_to_end_generation_tokens_per_second=100,
                    hit_token_ceiling=False,
                    draft_model="demo/draft",
                    num_draft_tokens=3,
                    draft_accept_rate=0.5,
                ),
            )

            with patch(
                "remotion_pipeline.latency_benchmark.generate_completion_result",
                return_value=result,
            ):
                payload = run_latency_benchmark(benchmark, root, warmup_cases=0)

        self.assertEqual(payload["leaderboard"][0]["name"], "local")
        summary = payload["leaderboard"][0]["summary"]
        self.assertEqual(summary["mean_wall_seconds"], 0.5)
        self.assertEqual(summary["token_ceiling_rate"], 0.0)
        self.assertEqual(summary["mean_draft_accept_rate"], 0.5)
        self.assertEqual(payload["leaderboard"][0]["draft_model"], "demo/draft")


if __name__ == "__main__":
    unittest.main()
