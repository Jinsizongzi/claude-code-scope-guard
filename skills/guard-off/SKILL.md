---
name: guard-off
description: Turn the delete-confirmation prompt OFF / 关闭删除确认弹窗（删除类命令直接执行）
disable-model-invocation: true
allowed-tools: Bash(python C:/Users/<you>/.claude/toggle-delete-guard.py *)
---

!`python C:/Users/<you>/.claude/toggle-delete-guard.py off`

Repeat the line above to the user verbatim, then stop. Do not run any other command.
把上面这一行输出原样告诉用户，然后停止。不要运行任何其他命令。
