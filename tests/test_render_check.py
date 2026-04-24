from __future__ import annotations

import unittest

from remotion_pipeline.render_check import detect_export_info


class RenderCheckTest(unittest.TestCase):
    def test_detects_named_export(self) -> None:
        export_info = detect_export_info(
            "export const FancyChart = () => { return null; };"
        )
        self.assertIsNotNone(export_info)
        self.assertEqual(export_info.component_name, "FancyChart")
        self.assertFalse(export_info.uses_default_export)

    def test_detects_default_export(self) -> None:
        export_info = detect_export_info(
            "export default function PromoCard() { return null; }"
        )
        self.assertIsNotNone(export_info)
        self.assertEqual(export_info.component_name, "GeneratedComposition")
        self.assertTrue(export_info.uses_default_export)


if __name__ == "__main__":
    unittest.main()
