# claude-code-scope-guard

A `PreToolUse` hook for [Claude Code](https://code.claude.com) that forces an explicit confirmation prompt whenever `Edit`, `Write`, or `NotebookEdit` targets a file **outside the current project directory** — even when your permission mode is `"auto"` and would otherwise silently approve it.

Useful if you run Claude Code with broad `additionalDirectories` (e.g. whole drives) for read/search convenience, but still want a hard stop before it *writes* to something outside the project it was actually invoked on.

## Behavior

- If the edited/written path is inside `$CLAUDE_PROJECT_DIR` (or a subdirectory of it) → silent, falls through to normal permission handling.
- If the path is inside any `.claude` folder — the global `~/.claude`, or a `.claude` folder in any project — → silent, even when it's outside the current project. Claude Code config, memory, skills and `CLAUDE.md` files can be edited without a prompt.
  - Exception: `~/.claude/settings.json` and anything under `~/.claude/hooks/` don't get this exemption, so Claude can't quietly rewrite the permission rules or this hook itself. They follow the normal inside/outside-the-project check.
- If the path is inside Claude Code's own temp folder (`%TEMP%\claude`, where each session's scratchpad lives) → silent. Claude is told to put its temp files there, so prompting for them is just noise.
- If the path is outside `$CLAUDE_PROJECT_DIR`, or `CLAUDE_PROJECT_DIR` isn't set at all → returns a hook decision of `"ask"`, which forces a confirmation prompt regardless of `permissions.defaultMode`.
- Tool calls that aren't `Edit`/`Write`/`NotebookEdit` (e.g. `Bash`, `Read`, `Glob`) are not touched by this hook at all — it only looks at `tool_input.file_path` / `tool_input.notebook_path`.

## Install

1. Copy `hooks/enforce-project-scope.py` somewhere permanent, e.g. `%USERPROFILE%\.claude\hooks\enforce-project-scope.py`.
2. Add this to your Claude Code `settings.json` (global `~/.claude/settings.json` or project `.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"C:\\Users\\<you>\\.claude\\hooks\\enforce-project-scope.py\""
          }
        ]
      }
    ]
  }
}
```

3. Requires Python 3 on `PATH` (or point `command` at a full interpreter path). No third-party dependencies — stdlib only.

## Notes

- On Windows, path comparison uses `os.path.normcase`, so it's case-insensitive and drive-letter aware; a path on a different drive than the project directory is correctly treated as "outside".
- Paths are resolved with `os.path.realpath` first, so 8.3 short names (e.g. `C:\Users\JOHNDO~1\.claude\settings.json`) can't sidestep the protected-file check.
- This hook only ever asks for *more* confirmation than your base permission settings would otherwise require — it can't auto-approve anything by itself. Worst case if something goes wrong reading the payload, it just returns silently and normal permission resolution applies.
- Verified working live against Claude Code (Sonnet 5) on Windows: a `Write` call targeting a path outside the session's project directory correctly triggered a confirmation prompt.

## License

MIT — do whatever you want with it.
