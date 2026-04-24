from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from remotion_pipeline.synthetic_dataset import build_synthetic_records


class SyntheticDatasetTest(unittest.TestCase):
    def test_builds_records_from_manifest_and_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            template = root / "template.tsx"
            template.write_text("export const Demo = () => <div />;\n")
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "inspiration_sources": ["remotion animation rules"],
                        "cases": [
                            {
                                "case_id": "demo",
                                "prompt": "Create a demo animation",
                                "template_path": "template.tsx",
                                "tags": ["demo"],
                                "must_contain": ["Demo"],
                            }
                        ],
                    }
                )
            )

            records = build_synthetic_records(manifest_path=manifest)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["license"], "MIT")
        self.assertEqual(records[0]["source_name"], "codex-synthetic-v1")
        self.assertIn("codex-synthetic", records[0]["tags"])
        self.assertIn("remotion animation rules", records[0]["inspiration_sources"])
        self.assertEqual(records[0]["entry_component"], "Demo")


if __name__ == "__main__":
    unittest.main()
