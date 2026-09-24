# claude-code-scope-guard

[English](#english) | [中文](#中文)

Two small guards for [Claude Code](https://code.claude.com) on Windows:

1. **Scope guard**: a `PreToolUse` hook that asks for confirmation before `Edit` / `Write` / `NotebookEdit` touches a file outside the current project.
2. **Delete guard**: a list of `permissions.ask` rules that ask for confirmation before any delete-type command, plus `/guard-on`, `/guard-off` and `/guard-status` slash commands to switch it on and off.

两个给 [Claude Code](https://code.claude.com)（Windows）用的保护：

1. **项目范围保护**：一个 `PreToolUse` hook。`Edit` / `Write` / `NotebookEdit` 要改当前项目以外的文件时，先弹窗确认。
2. **删除保护**：一组 `permissions.ask` 规则。任何删除类命令执行前都先弹窗确认。另有 `/guard-on`、`/guard-off`、`/guard-status` 三个斜杠指令，用来开关它。

```
hooks/enforce-project-scope.py      # scope guard hook / 项目范围保护 hook
delete-guard/delete-guard.json      # delete guard rules / 删除保护规则
delete-guard/toggle-delete-guard.py # on/off/status script / 开关脚本
skills/guard-on/SKILL.md            # /guard-on
skills/guard-off/SKILL.md           # /guard-off
skills/guard-status/SKILL.md        # /guard-status
```

---

## English

### 1. Scope guard

Forces an explicit confirmation prompt whenever `Edit`, `Write`, or `NotebookEdit` targets a file **outside the current project directory**, even when your permission mode is `"auto"` and would otherwise silently approve it.

Useful if you run Claude Code with broad `additionalDirectories` (e.g. whole drives) for read/search convenience, but still want a hard stop before it *writes* to something outside the project it was actually invoked on.

#### Behavior

- Path inside `$CLAUDE_PROJECT_DIR` (or a subdirectory) → silent; normal permission handling applies.
- Path inside any `.claude` folder (the global `~/.claude`, or a `.claude` folder in any project) → silent, even outside the current project. Config, memory, skills and `CLAUDE.md` files can be edited without a prompt.
  - Exception: `~/.claude/settings.json` and anything under `~/.claude/hooks/` don't get this exemption, so Claude can't quietly rewrite the permission rules or this hook. They follow the normal inside/outside check.
- Path inside Claude Code's own temp folder (`%TEMP%\claude`, where each session's scratchpad lives) → silent.
- Path outside `$CLAUDE_PROJECT_DIR`, or `CLAUDE_PROJECT_DIR` not set → the hook returns `"ask"`, which forces a prompt regardless of `permissions.defaultMode`.
- Other tools (`Bash`, `PowerShell`, `Read`, `Glob`, ...) are not checked. A shell command that writes outside the project is **not** caught by this hook.

#### Install

1. Copy `hooks/enforce-project-scope.py` to e.g. `%USERPROFILE%\.claude\hooks\enforce-project-scope.py`.
2. Add this to `~/.claude/settings.json` (or a project's `.claude/settings.json`):

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

3. Needs Python 3 on `PATH`. Standard library only.

#### Notes

- Path comparison uses `os.path.normcase`, so it is case-insensitive and drive-letter aware.
- Paths are resolved with `os.path.realpath` first, so 8.3 short names (e.g. `C:\Users\JOHNDO~1\.claude\settings.json`) can't sidestep the protected-file check.
- The hook only ever asks for *more* confirmation. It can't approve anything. If it fails to read the payload, it returns silently and normal permission handling applies.

### 2. Delete guard

`delete-guard/delete-guard.json` holds 65 `permissions.ask` rules for both the `Bash` and `PowerShell` tools. They cover:

- file deletion: `rm`, `rmdir`, `unlink`, `shred`, `find -delete`, `del` / `erase` / `rd`, `Remove-Item` / `ri`
- destructive git: `git clean`, `git reset --hard`, `git checkout --`, `git restore`, `git rm -f` / `--force` / `-rf`, deleting branches, tags and stashes, `git push --delete`
- GitHub CLI: `gh ... delete`, `gh api ... DELETE`

Plain `git rm` (without `-f`) is intentionally **not** in the list. Git refuses to remove a file with uncommitted changes unless you pass `-f`, and committed files can be restored from history. The `*-f*` pattern also matches file names that contain `-f` (e.g. `my-file.py`). That only causes an extra prompt, never a missed one.

`ask` rules still prompt in `bypassPermissions` mode, so this list is also a safety net when you bypass permissions.

#### Switching it on and off

| Command | Effect |
| --- | --- |
| `/guard-on` | Writes the 65 rules into `permissions.ask` |
| `/guard-off` | Removes them from `permissions.ask` |
| `/guard-status` | Prints `ON`, `OFF` or `PARTIAL` with a rule count |

- **Scope:** global. The script edits the user-level `~/.claude/settings.json`, which every project and session reads. New sessions always pick up the change. Whether an already running session reloads it immediately has not been verified.
- Other `ask` rules you add yourself are kept on both `on` and `off`.
- Before each write, the script copies `settings.json` to `settings.json.bak`, then replaces the file atomically.
- The skills use `disable-model-invocation: true`, so Claude can't call them by itself. Only you can type them. In testing, auto mode's classifier also refused to let Claude run `toggle-delete-guard.py off` directly (reason: self-modification).
- The skills use `!` pre-execution, so the script runs when you type the command. Claude only repeats the one-line result.

#### Install

1. Copy `delete-guard/delete-guard.json` and `delete-guard/toggle-delete-guard.py` to `%USERPROFILE%\.claude\`.
2. Copy the three folders under `skills/` to `%USERPROFILE%\.claude\skills\`.
3. In each `SKILL.md`, replace `<you>` with your Windows user name (the path appears twice: in `allowed-tools` and in the `!` line).
4. Type `/guard-on`. If the commands don't show up in the `/` menu, start a new session.
5. Type `/guard-status` to check. Expected: `delete guard: ON (65/65 rules active)`.

---

## 中文

### 1. 项目范围保护

`Edit`、`Write`、`NotebookEdit` 要改**当前项目文件夹以外**的文件时，强制弹窗确认。即使权限模式是 `"auto"`，也会弹窗。

适合这种情况：为了方便读取和搜索，给 Claude Code 开了很大的 `additionalDirectories`（比如整个硬盘），但仍然希望它在写项目以外的文件之前先停下来问你。

#### 行为

- 路径在 `$CLAUDE_PROJECT_DIR` 里（包括子文件夹）→ 不处理，按正常权限规则走。
- 路径在任何 `.claude` 文件夹里（全局 `~/.claude`，或任何项目的 `.claude`）→ 不弹窗，即使在当前项目以外。配置、记忆、skill、`CLAUDE.md` 可以直接改。
  - 例外：`~/.claude/settings.json` 和 `~/.claude/hooks/` 下的文件没有这个豁免，防止 Claude 悄悄改掉权限规则或这个 hook 本身。它们按正常的“项目内/项目外”判断。
- 路径在 Claude Code 自己的临时文件夹里（`%TEMP%\claude`，每个会话的 scratchpad 在这里）→ 不弹窗。
- 路径在 `$CLAUDE_PROJECT_DIR` 以外，或没有设置 `CLAUDE_PROJECT_DIR` → hook 返回 `"ask"`，不管 `permissions.defaultMode` 是什么都会弹窗。
- 其他工具（`Bash`、`PowerShell`、`Read`、`Glob` 等）不检查。通过命令行写项目外的文件，这个 hook **拦不到**。

#### 安装

1. 把 `hooks/enforce-project-scope.py` 复制到 `%USERPROFILE%\.claude\hooks\enforce-project-scope.py`。
2. 在 `~/.claude/settings.json`（或项目的 `.claude/settings.json`）里加上面英文部分的 `hooks` 配置，把 `<you>` 换成你的 Windows 用户名。
3. 需要 `PATH` 里有 Python 3。只用标准库。

#### 说明

- 路径比较用 `os.path.normcase`，不区分大小写，能识别不同盘符。
- 路径先经过 `os.path.realpath` 解析，所以 8.3 短文件名（比如 `C:\Users\JOHNDO~1\.claude\settings.json`）绕不过受保护文件的检查。
- 这个 hook 只会增加确认，不会自动批准任何操作。读取输入失败时直接退出，按正常权限规则走。

### 2. 删除保护

`delete-guard/delete-guard.json` 里有 65 条 `permissions.ask` 规则，`Bash` 和 `PowerShell` 两个工具都覆盖。范围：

- 删文件：`rm`、`rmdir`、`unlink`、`shred`、`find -delete`、`del` / `erase` / `rd`、`Remove-Item` / `ri`
- 危险的 git 操作：`git clean`、`git reset --hard`、`git checkout --`、`git restore`、`git rm -f` / `--force` / `-rf`、删分支、删 tag、删 stash、`git push --delete`
- GitHub CLI：`gh ... delete`、`gh api ... DELETE`

普通的 `git rm`（不带 `-f`）**故意不拦**。文件有未提交的改动时，不带 `-f` 的 `git rm` 会拒绝执行；已提交的文件可以从 git 历史找回。`*-f*` 这条规则也会匹配文件名里带 `-f` 的情况（比如 `my-file.py`），这只会多弹一次窗，不会漏拦。

`ask` 规则在 `bypassPermissions`（跳过权限）模式下也会弹窗，所以开了跳过权限，这组规则仍然有效。

#### 开关

| 指令 | 作用 |
| --- | --- |
| `/guard-on` | 把 65 条规则写进 `permissions.ask` |
| `/guard-off` | 从 `permissions.ask` 里删掉这 65 条规则 |
| `/guard-status` | 显示 `ON`、`OFF` 或 `PARTIAL`，以及生效的规则数 |

- **生效范围：全局。** 脚本改的是用户级 `~/.claude/settings.json`，所有项目和会话都读这个文件。新开的会话一定按新设置执行；已经开着的会话会不会马上重新读取，还没验证。
- 你自己另外加的 `ask` 规则，开和关都会保留。
- 每次写入前，脚本先把 `settings.json` 备份成 `settings.json.bak`，然后整体替换文件。
- 三个 skill 都设置了 `disable-model-invocation: true`，Claude 不能自己调用，只有你能输入。测试时，auto 模式的安全检查也拒绝让 Claude 直接运行 `toggle-delete-guard.py off`（原因：自我修改）。
- skill 用的是 `!` 预执行：你输入指令时脚本就运行了，Claude 只负责把一行结果转述给你。

#### 安装

1. 把 `delete-guard/delete-guard.json` 和 `delete-guard/toggle-delete-guard.py` 复制到 `%USERPROFILE%\.claude\`。
2. 把 `skills/` 下的三个文件夹复制到 `%USERPROFILE%\.claude\skills\`。
3. 在每个 `SKILL.md` 里，把 `<you>` 换成你的 Windows 用户名（每个文件有两处：`allowed-tools` 和 `!` 那一行）。
4. 输入 `/guard-on`。如果在 `/` 菜单里看不到这三个指令，就新开一个会话。
5. 输入 `/guard-status` 检查。正常结果：`delete guard: ON (65/65 rules active)`。

---

## License

MIT — do whatever you want with it. / 随便用。
