"""PreToolUse hook: force confirmation for Edit/Write/NotebookEdit outside the
current project directory. Silent (no output) when the target is inside the
project, or when the tool call isn't a file-path edit -- both cases fall
through to normal permission resolution.

Exception: any path inside a `.claude` folder (global ~/.claude, or any
project's .claude) is also silent, except the files that hold these rules
themselves (~/.claude/settings.json and ~/.claude/hooks/), which keep the
normal outside-the-project check.

Claude Code's own temp folder (%TEMP%\\claude, where each session's
scratchpad lives) is silent too.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile


HOME_CLAUDE = os.path.join(os.path.expanduser("~"), ".claude")
PROTECTED_FILES = [os.path.join(HOME_CLAUDE, "settings.json")]
PROTECTED_DIRS = [os.path.join(HOME_CLAUDE, "hooks")]
EXEMPT_DIRS = [os.path.join(tempfile.gettempdir(), "claude")]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not path:
        return

    target = _norm(path)

    if _in_claude_dir(target) and not _is_protected(target):
        return

    if any(_is_inside(target, _norm(d)) for d in EXEMPT_DIRS):
        return

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if not project_dir:
        _ask(f"无法确定当前项目目录（CLAUDE_PROJECT_DIR 未设置），出于安全默认需要确认后才能修改：{path}")
        return

    if not _is_inside(target, _norm(project_dir)):
        _ask(f"目标文件不在当前项目目录（{project_dir}）内，需要确认后才能修改：{path}")


def _norm(path: str) -> str:
    # realpath expands 8.3 short names (C:\Users\JOHNDO~1) so they can't
    # sidestep the protected-file check.
    return os.path.normcase(os.path.realpath(path))


def _is_inside(target: str, root: str) -> bool:
    try:
        return os.path.commonpath([target, root]) == root
    except ValueError:
        # Different drives on Windows -- definitely outside.
        return False


def _in_claude_dir(target: str) -> bool:
    return ".claude" in target.split(os.sep)[:-1]


def _is_protected(target: str) -> bool:
    if any(target == _norm(f) for f in PROTECTED_FILES):
        return True
    return any(_is_inside(target, _norm(d)) for d in PROTECTED_DIRS)


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
