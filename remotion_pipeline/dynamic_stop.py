from __future__ import annotations

import re

_CODE_BLOCK = re.compile(r"```(?:tsx|ts|jsx|js)?\s*(.*?)(?:```|$)", re.DOTALL | re.IGNORECASE)
_COMPONENT_EXPORT = re.compile(
    r"\bexport\s+(?:default\s+)?(?:const|function)\s+[A-Z][A-Za-z0-9_]*"
)
_REMOTION_IMPORT = re.compile(r"\bfrom\s+['\"]remotion['\"]")


def should_stop_remotion_generation(
    text: str,
    *,
    require_remotion_import: bool = True,
) -> bool:
    code = extract_streamed_code(text)
    if not _COMPONENT_EXPORT.search(code):
        return False
    if require_remotion_import and not _REMOTION_IMPORT.search(code):
        return False
    return _has_jsx_return(code) and _delimiters_are_balanced(code) and _last_line_can_end(code)


def extract_streamed_code(text: str) -> str:
    match = _CODE_BLOCK.search(text)
    return match.group(1).strip() if match else text.strip()


def _has_jsx_return(code: str) -> bool:
    return "return (" in code or "return <" in code or "=> (" in code or "=> <" in code


def _last_line_can_end(code: str) -> bool:
    lines = [line.strip() for line in code.splitlines() if line.strip()]
    if not lines:
        return False
    line = lines[-1]
    if line.endswith((",", "(", "[", "{", "=>", ":", "?", ".", "&&", "||")):
        return False
    return line.endswith((";", "}", ");", "};"))


def _delimiters_are_balanced(code: str) -> bool:
    masked, literals_closed = _mask_literals_and_comments(code)
    if not literals_closed:
        return False
    stack: list[str] = []
    opening = {"(", "[", "{"}
    closing = {")": "(", "]": "[", "}": "{"}
    for char in masked:
        if char in opening:
            stack.append(char)
            continue
        if char in closing:
            if not stack or stack.pop() != closing[char]:
                return False
    return not stack


def _mask_literals_and_comments(code: str) -> tuple[str, bool]:
    chars = list(code)
    index = 0
    state: str | None = None
    while index < len(chars):
        char = chars[index]
        nxt = chars[index + 1] if index + 1 < len(chars) else ""
        if state is None:
            if char == "/" and nxt == "/":
                state = "line-comment"
                chars[index] = chars[index + 1] = " "
                index += 2
                continue
            if char == "/" and nxt == "*":
                state = "block-comment"
                chars[index] = chars[index + 1] = " "
                index += 2
                continue
            if char in {"'", '"', "`"}:
                state = char
                chars[index] = " "
        elif state == "line-comment":
            if char == "\n":
                state = None
            else:
                chars[index] = " "
        elif state == "block-comment":
            chars[index] = " "
            if char == "*" and nxt == "/":
                chars[index + 1] = " "
                state = None
                index += 1
        elif state in {"'", '"', "`"}:
            escaped = index > 0 and code[index - 1] == "\\"
            chars[index] = " "
            if char == state and not escaped:
                state = None
        index += 1
    return "".join(chars), state is None
