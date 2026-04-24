from __future__ import annotations

import unittest

from remotion_pipeline.case_records import normalize_case_record


class CaseRecordsTest(unittest.TestCase):
    def test_defaults_are_applied(self) -> None:
        case = normalize_case_record(
            {
                "case_id": "sample",
                "prompt": "Build a chart card",
                "completion": "export default function Sample() { return null; }",
            }
        )
        self.assertEqual(case["entry_component"], "GeneratedComposition")
        self.assertEqual(case["duration_in_frames"], 90)
        self.assertEqual(case["fps"], 30)
        self.assertEqual(case["width"], 1280)
        self.assertEqual(case["height"], 720)
        self.assertEqual(case["default_props"], {})


if __name__ == "__main__":
    unittest.main()
