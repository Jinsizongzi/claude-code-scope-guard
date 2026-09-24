---
name: guard-on
description: Turn the delete-confirmation prompt ON / 打开删除确认弹窗（删除类命令需要你点允许）
disable-model-invocation: true
allowed-tools: Bash(python C:/Users/<you>/.claude/toggle-delete-guard.py *)
---

!`python C:/Users/<you>/.claude/toggle-delete-guard.py on`

Repeat the line above to the user verbatim, then stop. Do not run any other command.
把上面这一行输出原样告诉用户，然后停止。不要运行任何其他命令。
