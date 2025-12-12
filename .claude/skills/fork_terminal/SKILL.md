---
name: Fork Terminal Skill
description: Fork a terminal session to a new terminal window. Use this when the user requests 'fork terminal' or 'create a new terminal' or 'new terminal: <command>'.
---

# Purpose

Fork a terminal session to a new terminal window. Using one agentic coding tools or raw cli commands.
Follow the `Instructions`, execute the `Workflow`, based on the `Cookbook`.

## Variables

ENABLE_RAW_CLI_COMMANDS: true
ENABLE_GEMINI_CLI: true
ENABLE_CODEX_CLI: true
ENABLE_CLAUDE_CODE: true

## Instructions

- Based on the user's request, follow the `Cookbook` to determine which tool to use.

## Workflow

1. Understand the users request 
2. READ `.claude/skills/fork_terminal/tools/fork_terminal.py` to understand our tooling.
3. Follow the `Cookbook` to determine which tool to use.
4. Execute the `.claude/skills/fork_terminal/tools/fork_terminal.py: fork_terminal(command: str)` tool.

## Cookbook

### Raw CLI Commands

- IF the user requests a non-agentic coding tool.
- THEN: Read and execute: `.claude/skills/fork_terminal/cookbook/cli-command.md`
- EXAMPLES:
- "Create a new terminal to <xyz> with ffmpeg"
- "Create a new terminal to <xyz> with curl"
- "Create a new terminal to <xyz> with python"
