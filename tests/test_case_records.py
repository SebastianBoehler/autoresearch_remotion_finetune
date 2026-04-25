from __future__ import annotations

import unittest

from remotion_pipeline.case_records import (
    DEFAULT_SYSTEM_PROMPT,
    case_to_chat_record,
    normalize_case_record,
)


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

    def test_chat_training_record_uses_messages_without_completion_column(self) -> None:
        case = normalize_case_record(
            {
                "case_id": "sample",
                "system": "Return TSX only.",
                "prompt": "Build a chart card",
                "completion": "export const Demo = () => <div />;\n",
                "tags": ["demo"],
            }
        )

        record = case_to_chat_record(case)

        self.assertNotIn("completion", record)
        self.assertNotIn("prompt", record)
        self.assertEqual(record["messages"][0]["role"], "system")
        self.assertEqual(record["messages"][1]["role"], "user")
        self.assertEqual(record["messages"][2]["role"], "assistant")
        self.assertEqual(record["messages"][2]["content"], case["completion"])

    def test_default_system_prompt_blocks_common_remotion_hook_mistake(self) -> None:
        self.assertIn("spring(...)", DEFAULT_SYSTEM_PROMPT)
        self.assertIn("never import or call useSpring", DEFAULT_SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
