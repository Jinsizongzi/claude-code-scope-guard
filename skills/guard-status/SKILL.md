---
name: guard-status
description: Show whether the delete-confirmation prompt is ON or OFF / 查看删除确认弹窗当前是开还是关
disable-model-invocation: true
allowed-tools: Bash(python C:/Users/<you>/.claude/toggle-delete-guard.py *)
---

!`python C:/Users/<you>/.claude/toggle-delete-guard.py status`

Repeat the line above to the user verbatim, then stop. Do not run any other command.
把上面这一行输出原样告诉用户，然后停止。不要运行任何其他命令。
