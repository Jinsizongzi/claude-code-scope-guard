"""PreToolUse hook: force confirmation for Edit/Write/NotebookEdit outside the
current project directory. Silent (no output) when the target is inside the
project, or when the tool call isn't a file-path edit -- both cases fall
through to normal permission resolution.
"""
from __future__ import annotations

import json
import os
import sys


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not path:
        return

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if not project_dir:
        _ask(f"无法确定当前项目目录（CLAUDE_PROJECT_DIR 未设置），出于安全默认需要确认后才能修改：{path}")
        return

    target = os.path.normcase(os.path.abspath(path))
    root = os.path.normcase(os.path.abspath(project_dir))

    try:
        inside = os.path.commonpath([target, root]) == root
    except ValueError:
        # Different drives on Windows -- definitely outside the project.
        inside = False

    if not inside:
        _ask(f"目标文件不在当前项目目录（{project_dir}）内，需要确认后才能修改：{path}")


def _ask(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


if __name__ == "__main__":
    main()
