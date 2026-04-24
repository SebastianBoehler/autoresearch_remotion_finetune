from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from remotion_pipeline.types import RemotionRuntimeConfig

NAMED_EXPORT_PATTERN = re.compile(
    r"export\s+(?:const|function)\s+(?P<name>[A-Z][A-Za-z0-9_]*)"
)
DEFAULT_EXPORT_PATTERN = re.compile(r"export\s+default\b")


@dataclass
class ExportInfo:
    component_name: str
    uses_default_export: bool


@dataclass
class RemotionCheckResult:
    compile_ok: bool
    render_ok: bool | None
    export_info: ExportInfo | None
    compile_log_tail: str
    render_log_tail: str
    render_mode: str


def normalize_generated_code(code: str) -> str:
    stripped = code.replace("\r\n", "\n").strip()
    return f"{stripped}\n" if stripped else ""


def detect_export_info(code: str) -> ExportInfo | None:
    named_export = NAMED_EXPORT_PATTERN.search(code)
    if named_export:
        return ExportInfo(
            component_name=named_export.group("name"),
            uses_default_export=False,
        )
    if DEFAULT_EXPORT_PATTERN.search(code):
        return ExportInfo(
            component_name="GeneratedComposition",
            uses_default_export=True,
        )
    return None


def build_root_source(
    export_info: ExportInfo,
    runtime: RemotionRuntimeConfig,
    duration_in_frames: int,
    fps: int,
    width: int,
    height: int,
    default_props: dict[str, Any],
) -> str:
    import_statement = (
        'import GeneratedComposition from "./GeneratedComposition";'
        if export_info.uses_default_export
        else f'import {{ {export_info.component_name} as GeneratedComposition }} from "./GeneratedComposition";'
    )
    props_payload = json.dumps(default_props, indent=2)
    return (
        'import { Composition } from "remotion";\n'
        f"{import_statement}\n\n"
        "export const RemotionRoot: React.FC = () => {\n"
        "  return (\n"
        "    <>\n"
        "      <Composition\n"
        f'        id="{runtime.composition_id}"\n'
        "        component={GeneratedComposition}\n"
        "        durationInFrames={"
        + str(duration_in_frames)
        + "}\n"
        "        fps={"
        + str(fps)
        + "}\n"
        "        width={"
        + str(width)
        + "}\n"
        "        height={"
        + str(height)
        + "}\n"
        "        defaultProps={"
        + props_payload
        + "}\n"
        "      />\n"
        "    </>\n"
        "  );\n"
        "};\n"
    )


def _copy_runner_template(template_dir: Path, workspace_dir: Path) -> None:
    shutil.copytree(
        template_dir,
        workspace_dir,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(
            "node_modules",
            ".DS_Store",
            "dist",
            "out",
            "renders",
        ),
    )
    node_modules = template_dir / "node_modules"
    if node_modules.exists():
        os.symlink(node_modules, workspace_dir / "node_modules")


def _extract_log_tail(output: str) -> str:
    return output.strip()[-2000:]


def run_remotion_check(
    *,
    code: str,
    repo_root: Path,
    runtime: RemotionRuntimeConfig,
    duration_in_frames: int,
    fps: int,
    width: int,
    height: int,
    default_props: dict[str, Any] | None,
    timeout_seconds: int,
    render_enabled: bool,
) -> RemotionCheckResult:
    normalized_code = normalize_generated_code(code)
    export_info = detect_export_info(normalized_code)
    if export_info is None:
        return RemotionCheckResult(
            compile_ok=False,
            render_ok=None if not render_enabled else False,
            export_info=None,
            compile_log_tail="No supported component export found in generated code.",
            render_log_tail="",
            render_mode="bundle",
        )

    template_dir = (repo_root / runtime.runner_dir).resolve()
    node_modules = template_dir / "node_modules"
    if not node_modules.exists():
        message = (
            f"Runner dependencies are missing in {template_dir}. "
            "Install them with `npm install` inside the runner directory."
        )
        return RemotionCheckResult(
            compile_ok=False,
            render_ok=None if not render_enabled else False,
            export_info=export_info,
            compile_log_tail=message,
            render_log_tail="",
            render_mode="bundle",
        )

    default_props_payload = default_props or {}
    effective_render_mode = runtime.render_mode if render_enabled else "bundle"
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_dir = Path(tmpdir) / "runner"
        _copy_runner_template(template_dir, workspace_dir)
        (workspace_dir / "src" / "GeneratedComposition.tsx").write_text(normalized_code)
        (workspace_dir / "src" / "Root.tsx").write_text(
            build_root_source(
                export_info=export_info,
                runtime=runtime,
                duration_in_frames=duration_in_frames,
                fps=fps,
                width=width,
                height=height,
                default_props=default_props_payload,
            )
        )
        output_path = workspace_dir / f"render-output.{runtime.output_extension}"
        command = [
            "node",
            "scripts/render-check.mjs",
            "--entry",
            "src/index.ts",
            "--composition",
            runtime.composition_id,
            "--output",
            str(output_path),
            "--mode",
            effective_render_mode,
            "--frame",
            str(runtime.render_frame),
        ]
        result = subprocess.run(
            command,
            cwd=workspace_dir,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        combined_output = (result.stdout + "\n" + result.stderr).strip()
        if result.returncode != 0:
            return RemotionCheckResult(
                compile_ok=False,
                render_ok=False if render_enabled else None,
                export_info=export_info,
                compile_log_tail=_extract_log_tail(combined_output),
                render_log_tail=_extract_log_tail(combined_output),
                render_mode=effective_render_mode,
            )
        return RemotionCheckResult(
            compile_ok=True,
            render_ok=True if render_enabled else None,
            export_info=export_info,
            compile_log_tail=_extract_log_tail(combined_output),
            render_log_tail=_extract_log_tail(combined_output),
            render_mode=effective_render_mode,
        )
