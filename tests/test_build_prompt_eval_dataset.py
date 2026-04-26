import importlib.util
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_prompt_eval_dataset.py"
SPEC = importlib.util.spec_from_file_location("build_prompt_eval_dataset", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_prompt_eval_dataset_preserves_prompt_constraints(tmp_path: Path) -> None:
    source = tmp_path / "prompts.jsonl"
    source.write_text(
        '{"prompt_id":"demo","prompt":"Create a Remotion demo.",'
        '"tags":["frontier"],"must_contain":["svg"],'
        '"must_not_contain":["fetch("],"duration_in_frames":90,'
        '"fps":30,"width":1280,"height":720}\n'
    )

    cases = MODULE.prompt_records_to_eval_cases([source])

    assert cases[0]["case_id"] == "eval_demo"
    assert cases[0]["tags"] == ["frontier-eval", "frontier"]
    assert cases[0]["must_contain"] == ["svg"]
    assert cases[0]["must_not_contain"] == ["fetch("]
    assert cases[0]["duration_in_frames"] == 90
