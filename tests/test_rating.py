from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from remotion_pipeline.rating import promote_rated_cases


class RatingTest(unittest.TestCase):
    def test_promotes_high_rated_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_path = root / "rating_queue.jsonl"
            output_path = root / "approved.jsonl"
            rows = [
                _row("great", 5, "unrated"),
                _row("manual", None, "accept"),
                _row("weak", 2, "unrated"),
                _row("rejected", 5, "reject"),
                {**_row("failed", 5, "accept"), "candidate_render_ok": False},
            ]
            input_path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")

            promoted = promote_rated_cases(
                input_path=input_path,
                output_path=output_path,
                min_rating=4,
                accepted_license="MIT",
            )
            self.assertTrue(output_path.exists())

        self.assertEqual([row["case_id"] for row in promoted], ["great", "manual"])
        self.assertEqual(promoted[0]["license"], "MIT")
        self.assertIn("human-approved", promoted[0]["tags"])


def _row(case_id: str, rating: int | None, decision: str) -> dict:
    return {
        "case_id": case_id,
        "prompt": f"Prompt {case_id}",
        "completion": "export const Demo = () => <div />;",
        "tags": ["candidate"],
        "license": "pending-human-review",
        "human_rating": rating,
        "rating_decision": decision,
    }


if __name__ == "__main__":
    unittest.main()
