from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from remotion_pipeline.render_check import detect_export_info


@dataclass
class GenerationQualitySignals:
    line_count: int
    ascii_only: bool
    has_supported_export: bool
    likely_token_ceiling: bool
    likely_unclosed_syntax: bool
    top_level_hook_call: bool
    undefined_export_name: bool
    missing_sparkline_width: bool
    animated_namespace: bool
    array_as_interpolate_value: bool
    non_numeric_interpolate_range: bool
    spring_missing_fps: bool
    object_render_error: bool

    def to_dict(self) -> dict:
        return asdict(self)


def analyze_generation_quality(
    *,
    code: str,
    compile_log_tail: str = "",
    render_log_tail: str = "",
) -> GenerationQualitySignals:
    log = f"{compile_log_tail}\n{render_log_tail}"
    return GenerationQualitySignals(
        line_count=len(code.splitlines()),
        ascii_only=code.isascii(),
        has_supported_export=detect_export_info(code) is not None,
        likely_token_ceiling=_looks_truncated(code, log),
        likely_unclosed_syntax=_has_unclosed_syntax_log(log),
        top_level_hook_call=_has_top_level_hook_call(code),
        undefined_export_name=_has_undefined_default_export(code, log),
        missing_sparkline_width="SPARKLINE_WIDTH" in code
        and not re.search(r"const\s+SPARKLINE_WIDTH\b", code),
        animated_namespace="<animated." in code or "</animated." in code,
        array_as_interpolate_value=bool(re.search(r"interpolate\(\[[A-Za-z_]\w*\]", code)),
        non_numeric_interpolate_range=_has_non_numeric_interpolate_signal(code, log),
        spring_missing_fps='"fps" must be a number' in log,
        object_render_error="React error #31" in log or "args[]=object%20with%20keys" in log,
    )


def _looks_truncated(code: str, log: str) -> bool:
    stripped = code.rstrip()
    return (
        "end of file" in log
        or "Expected \"}\"" in log
        or stripped.endswith("[0,")
        or stripped.endswith("(")
        or stripped.count("{") > stripped.count("}") + 2
    )


def _has_unclosed_syntax_log(log: str) -> bool:
    return any(
        marker in log
        for marker in (
            "Expected \"}\"",
            "Expected identifier",
            "Unexpected \"export\"",
            "found end of file",
        )
    )


def _has_top_level_hook_call(code: str) -> bool:
    export_index = _first_component_export_index(code)
    hook_index = code.find("useCurrentFrame()")
    return hook_index >= 0 and (export_index < 0 or hook_index < export_index)


def _has_undefined_default_export(code: str, log: str) -> bool:
    match = re.search(r"export\s+default\s+([A-Za-z_]\w*)\s*;?\s*$", code)
    if match is None:
        return False
    exported = match.group(1)
    if re.search(rf"(?:const|function|class)\s+{re.escape(exported)}\b", code):
        return False
    return f"{exported} is not defined" in log or bool(_component_names(code))


def _has_non_numeric_interpolate_signal(code: str, log: str) -> bool:
    return (
        "inputRange must contain only numbers" in log
        or "outputRange must contain only numbers" in log
    )


def _first_component_export_index(code: str) -> int:
    matches = [
        index
        for index in (
            code.find("export const "),
            code.find("export function "),
            code.find("export default "),
        )
        if index >= 0
    ]
    return min(matches) if matches else -1


def _component_names(code: str) -> list[str]:
    return re.findall(r"(?:export\s+)?(?:const|function)\s+([A-Z][A-Za-z0-9_]*)\b", code)
