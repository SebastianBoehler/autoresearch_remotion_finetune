import importlib.util
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "generate_verified_remotion.py"
SPEC = importlib.util.spec_from_file_location("generate_verified_remotion", SCRIPT_PATH)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_verified_generation_requires_compile_and_non_failed_render() -> None:
    assert MODULE._is_verified_case({"compile_ok": True, "render_ok": True})
    assert MODULE._is_verified_case({"compile_ok": True, "render_ok": None})
    assert not MODULE._is_verified_case({"compile_ok": False, "render_ok": True})
    assert not MODULE._is_verified_case({"compile_ok": True, "render_ok": False})
