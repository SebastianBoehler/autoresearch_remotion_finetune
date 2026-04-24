from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from remotion_pipeline.style_prompts import build_style_prompt_bank


class StylePromptsTest(unittest.TestCase):
    def test_builds_cross_product_with_style_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            base = root / "base.jsonl"
            styles = root / "styles.json"
            output = root / "out.jsonl"
            base.write_text(
                json.dumps(
                    {
                        "prompt_id": "quiz",
                        "prompt": "Make a quiz card.",
                        "tags": ["quiz"],
                        "must_not_contain": ["fetch("],
                    }
                )
                + "\n"
            )
            styles.write_text(
                json.dumps(
                    {
                        "styles": [
                            {
                                "style_id": "clean_light",
                                "name": "Clean Light",
                                "family": "light",
                                "audience": "students",
                                "tags": ["light"],
                                "prompt": "Use black text on white cards.",
                            }
                        ]
                    }
                )
            )

            records = build_style_prompt_bank(
                base_prompts_path=base,
                style_profiles_path=styles,
                output_path=output,
            )
            self.assertTrue(output.exists())

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["prompt_id"], "quiz__clean_light")
        self.assertEqual(records[0]["style_id"], "clean_light")
        self.assertIn("style:clean_light", records[0]["tags"])
        self.assertIn("Composition", records[0]["must_not_contain"])


if __name__ == "__main__":
    unittest.main()
