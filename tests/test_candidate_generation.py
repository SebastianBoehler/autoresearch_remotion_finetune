from __future__ import annotations

import unittest

from remotion_pipeline.candidate_generation import CANDIDATE_SYSTEM_PROMPT
from remotion_pipeline.candidate_quality import (
    MAX_CANDIDATE_SOURCE_LINES,
    passes_verification,
    preview_frame,
    source_line_count,
)
from remotion_pipeline.types import RemotionRuntimeConfig


class CandidateGenerationTests(unittest.TestCase):
    def test_prompt_and_gate_keep_generated_sources_compact(self) -> None:
        self.assertEqual(MAX_CANDIDATE_SOURCE_LINES, 300)
        self.assertIn("under 260 lines", CANDIDATE_SYSTEM_PROMPT)
        self.assertIn("ASCII-only", CANDIDATE_SYSTEM_PROMPT)
        self.assertIn("48px safe margin", CANDIDATE_SYSTEM_PROMPT)

    def test_source_line_count_ignores_outer_whitespace(self) -> None:
        self.assertEqual(source_line_count("\n\nconst a = 1;\nconst b = 2;\n\n"), 2)
        self.assertEqual(source_line_count(""), 0)

    def test_preview_frame_uses_late_still_for_review(self) -> None:
        self.assertEqual(preview_frame({"duration_in_frames": 120}, RemotionRuntimeConfig()), 90)

    def test_verification_pass_requires_line_count_gate(self) -> None:
        row = {
            "compile_ok": True,
            "render_ok": True,
            "required_snippet_ratio": 1.0,
            "forbidden_ok": True,
            "line_count_ok": False,
            "ascii_ok": True,
        }

        self.assertFalse(passes_verification(row))

    def test_verification_pass_requires_ascii_source(self) -> None:
        row = {
            "compile_ok": True,
            "render_ok": True,
            "required_snippet_ratio": 1.0,
            "forbidden_ok": True,
            "line_count_ok": True,
            "ascii_ok": False,
        }

        self.assertFalse(passes_verification(row))


if __name__ == "__main__":
    unittest.main()
