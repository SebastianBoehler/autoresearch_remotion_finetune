from __future__ import annotations

import unittest

from remotion_pipeline.dynamic_stop import should_stop_remotion_generation


class DynamicStopTests(unittest.TestCase):
    def test_stops_when_exported_component_is_complete(self) -> None:
        code = """import {AbsoluteFill} from 'remotion';

export const Demo = () => {
  return (
    <AbsoluteFill>
      <div>Ready</div>
    </AbsoluteFill>
  );
};
"""
        self.assertTrue(should_stop_remotion_generation(code))

    def test_does_not_stop_with_unbalanced_component(self) -> None:
        code = """import {AbsoluteFill} from 'remotion';

export const Demo = () => {
  return (
    <AbsoluteFill>
      <div>Still streaming</div>
"""
        self.assertFalse(should_stop_remotion_generation(code))

    def test_does_not_stop_with_unclosed_string_literal(self) -> None:
        code = """import {AbsoluteFill} from 'remotion';

export const Demo = () => {
  return (
    <AbsoluteFill>
      <div style={{ boxShadow: "0 0 20px rgba(0,0,0,0.14)` }} />
    </AbsoluteFill>
  );
};
"""
        self.assertFalse(should_stop_remotion_generation(code))

    def test_does_not_stop_without_remotion_import_by_default(self) -> None:
        code = """export const Demo = () => {
  return <div>Plain React</div>;
};
"""
        self.assertFalse(should_stop_remotion_generation(code))
        self.assertTrue(
            should_stop_remotion_generation(code, require_remotion_import=False)
        )


if __name__ == "__main__":
    unittest.main()
