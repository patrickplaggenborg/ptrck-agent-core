# Multi-Agent OS Architecture Plan

**Status**: Draft
**Created**: 2026-01-15
**Author**: Claude (Opus 4.5)

---

## Executive Summary

You want to transform `ptrck-agent-core` into a **personal and business operating system** that orchestrates multiple Claude agents to handle complex tasks autonomously. The ChatGPT conversation provided valuable conceptual scaffolding—task state machines, skill contracts, multi-agent loops—but proposed Docker-centric infrastructure that doesn't leverage what you already have.

**The key insight**: Your repository already contains 80% of the foundation. The existing skill system, the claude-agent-sdk knowledge, and the hook-based automation are exactly the primitives needed. We don't need Docker containers or a FastAPI orchestrator—we need to **compose what exists into an orchestration layer**.

---

## Understanding Your Intention

Based on the ChatGPT conversation and your repository, you want:

1. **Autonomous task execution** - Give a goal, get results
2. **Multi-agent coordination** - Specialized agents (Planner, Implementer, Reviewer) working together
3. **Structured workflows** - Plans that can be inspected, approved, and tracked
4. **Skill-based capabilities** - Your existing skills as the "syscalls" of the OS
5. **Human-in-the-loop controls** - Approval gates for destructive operations

---

## What ChatGPT Got Right

| Concept | Value | Keep? |
|---------|-------|-------|
| Task state machine | Essential for tracking execution | ✅ Yes |
| Skill manifests | Clear contracts for capabilities | ✅ Already have (SKILL.md) |
| Plan.json schema | Contract between agents | ✅ Yes, adapted |
| Role prompts | Constrained agent behavior | ✅ Yes |
| Approval gates | Human control | ✅ Yes |
| Message protocol | Structured communication | ✅ Simplified |

## What ChatGPT Got Wrong

| Proposal | Problem | Better Alternative |
|----------|---------|-------------------|
| Docker per task | Overkill, complex infrastructure | Claude Code native sandboxing |
| FastAPI orchestrator | Extra service to maintain | Skills + claude-agent-sdk |
| Git worktrees per task | Complexity without benefit | Normal branches |
| skill.yaml manifests | Duplicates SKILL.md | Extend existing format |
| Custom CLI protocol | Fragile parsing | Agent SDK streaming |

---

## Proposed Architecture

### Core Principle: Skills Are Syscalls

Your skills are already atomic, composable operations. The OS layer doesn't replace them—it orchestrates them.

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│          (Claude Code CLI / future web UI)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR SKILL                       │
│     (new skill: handles goals, creates plans, runs agents)  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌───────────────────┐ ┌───────────────┐ ┌───────────────────┐
│  PLANNER AGENT    │ │ IMPLEMENTER   │ │  REVIEWER AGENT   │
│  (via Task tool)  │ │ AGENT         │ │  (via Task tool)  │
└───────────────────┘ └───────────────┘ └───────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     EXISTING SKILLS                         │
│  braintrust-* │ atlassian-* │ figma │ mcp-* │ etc.         │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. Task State Machine (as data, not service)

Store task state in `.agent/tasks/` within the working directory:

```
.agent/
├── tasks/
│   └── {task-id}/
│       ├── task.json       # State, payload, history
│       ├── plan.json       # Planner output
│       ├── events.log      # Append-only execution log
│       └── outputs/        # Results from each step
└── config.json             # Global agent settings
```

**Task states** (same as ChatGPT proposed):
- `QUEUED` → `PREPARING` → `RUNNING` → `SUCCEEDED` | `FAILED`
- `RUNNING` ↔ `AWAITING_INPUT` (for approvals)
- Any → `CANCELED`

#### 2. Orchestrator Skill

A new skill `agent-orchestrator` that:
- Accepts goals from users
- Spawns Planner agent to create plan.json
- Executes plan steps via Implementer agent
- Validates results via Reviewer agent
- Handles approvals and state transitions

#### 3. Plan Schema (adapted from ChatGPT)

```json
{
  "version": 1,
  "task_id": "string",
  "goal": "string",
  "context": {
    "workdir": "string",
    "branch": "string",
    "skills_available": ["skill-id", ...]
  },
  "steps": [
    {
      "id": "S1",
      "title": "string",
      "type": "skill | shell | ask_user | agent",
      "skill_id": "optional - which skill to invoke",
      "prompt": "optional - for agent type steps",
      "shell": "optional - for shell type",
      "approval": "none | before_run | before_write",
      "depends_on": ["optional step ids"],
      "notes": "optional reasoning"
    }
  ],
  "success_criteria": ["string"]
}
```

#### 4. Agent Definitions

Using claude-agent-sdk patterns, define agents with constrained capabilities:

**Planner Agent**:
- Tools: `Read`, `Glob`, `Grep` (read-only exploration)
- Output: plan.json
- Cannot execute or modify

**Implementer Agent**:
- Tools: All tools, filtered by skill allowlist
- Follows plan step-by-step
- Pauses for approvals

**Reviewer Agent**:
- Tools: `Read`, `Glob`, `Grep`, `Bash` (for tests)
- Validates success criteria
- Cannot modify files (read-only)

---

## Implementation Plan

### Phase 1: Foundation

**Goal**: Create the orchestration infrastructure

1. **Create `.agent/` directory structure**
   - Task storage schema
   - Config file format

2. **Build `agent-orchestrator` skill**
   - Goal parsing and validation
   - Task creation and state management
   - Agent spawning logic

3. **Define agent role prompts**
   - Planner prompt (produces plan.json)
   - Implementer prompt (executes steps)
   - Reviewer prompt (validates results)

### Phase 2: Core Workflow

**Goal**: End-to-end task execution

4. **Implement plan execution engine**
   - Step sequencing
   - Skill invocation
   - Result capture

5. **Add approval gates**
   - Hook into user-prompt-submit
   - AWAITING_INPUT state handling
   - Approval/rejection flow

6. **Create task management commands**
   - `/task create <goal>` - Start new task
   - `/task status` - View current task
   - `/task approve` - Approve pending step
   - `/task cancel` - Cancel task

### Phase 3: Integration

**Goal**: Connect to existing skills

7. **Skill discovery mechanism**
   - Parse SKILL.md frontmatter
   - Build available skills list for Planner

8. **Skill invocation bridge**
   - Map plan step to Skill tool call
   - Capture outputs
   - Handle errors

### Phase 4: Polish

**Goal**: Production readiness

9. **Event logging and observability**
   - Structured event log format
   - Task history viewer

10. **Error recovery**
    - Retry logic
    - Rollback capabilities
    - Resume from checkpoint

---

## Detailed Component Designs

### The Orchestrator Skill (`agent-orchestrator/SKILL.md`)

```yaml
---
name: agent-orchestrator
description: |
  Multi-agent task orchestration system. Use this skill when the user provides
  a complex goal that requires planning, implementation, and review. Converts
  goals into executable plans and coordinates specialized agents to complete them.

  Keywords: orchestrate, multi-agent, plan, execute, autonomous, complex task
---
```

This skill will contain:
- `SKILL.md` - Orchestration logic and prompts
- `scripts/task_manager.py` - Task state management
- `references/plan_schema.json` - Plan validation schema
- `references/agent_prompts.md` - Role prompt templates

### Agent Prompt Templates

**Planner** (constrained to produce structured output):
```markdown
You are the PLANNER agent. Your job is to convert a goal into an executable plan.

## Constraints
- You can ONLY explore the codebase (Read, Glob, Grep)
- You CANNOT execute commands or modify files
- You MUST output valid plan.json

## Available Skills
{skills_list_with_descriptions}

## Goal
{user_goal}

## Output
Produce a plan.json with:
1. Clear step-by-step actions
2. Each step uses an available skill or asks the user
3. Success criteria that can be verified

Output ONLY the JSON, no markdown fences.
```

**Implementer** (executes with guardrails):
```markdown
You are the IMPLEMENTER agent. You execute the plan step by step.

## Plan
{plan_json}

## Current Step
{current_step}

## Rules
- Follow the plan exactly
- For steps with approval != "none", wait for approval
- Use only the skills specified in the plan
- Report errors clearly

Execute the current step.
```

**Reviewer** (validates without modifying):
```markdown
You are the REVIEWER agent. You verify the work was done correctly.

## Plan
{plan_json}

## Success Criteria
{success_criteria}

## Rules
- You CANNOT modify files
- Run verification commands (tests, lint, etc.)
- Check each success criterion
- Produce a clear pass/fail report
```

### Task State Schema (`task.json`)

```json
{
  "id": "task_1736956800000",
  "state": "RUNNING",
  "goal": "Add dark mode toggle to settings page",
  "created_at": "2026-01-15T12:00:00Z",
  "updated_at": "2026-01-15T12:05:00Z",
  "current_agent": "implementer",
  "current_step": "S3",
  "inputs": [
    {"ts": "...", "type": "approval", "message": "Yes, proceed"}
  ],
  "error": null,
  "outputs": {
    "S1": {"status": "completed", "result_path": "..."},
    "S2": {"status": "completed", "result_path": "..."}
  }
}
```

---

## Why This Approach

### Builds on What You Have

| Existing | How We Use It |
|----------|---------------|
| SKILL.md format | Skills become plan steps |
| claude-agent-sdk skill | Informs agent spawning patterns |
| Skill activation hook | Triggers orchestrator for complex goals |
| git-auto-commit | Called by Implementer for commits |

### Avoids Unnecessary Complexity

| ChatGPT Proposed | We Skip | Why |
|-----------------|---------|-----|
| Docker containers | ✗ | Claude Code already sandboxes |
| FastAPI service | ✗ | Skills run in Claude's process |
| Git worktrees | ✗ | Branches are simpler |
| Custom protocol | ✗ | Agent SDK handles messaging |

### Enables Future Growth

- **Web UI**: Task state is just JSON files—easy to build a viewer
- **Remote execution**: Could add remote agent runners later
- **Team features**: Task files can be shared/synced

---

## Comparison: ChatGPT vs This Plan

| Aspect | ChatGPT Approach | This Plan |
|--------|-----------------|-----------|
| Infrastructure | Docker + FastAPI | Claude Code native |
| Skill format | skill.yaml (new) | SKILL.md (existing) |
| Agent execution | Container subprocess | Task tool spawning |
| State storage | SQLite/Postgres | JSON files |
| Message passing | Custom JSON protocol | Agent SDK streaming |
| Deployment | Server deployment | rsync to ~/.claude |
| Complexity | High (4 services) | Low (1 skill) |
| Time to value | Weeks | Days |

---

## Next Steps

1. **Validate this plan** - Does this match your vision?
2. **Prioritize phases** - Start with Phase 1 or skip to core workflow?
3. **Scope decisions**:
   - Simple text-based UI vs future web UI?
   - Local-only vs remote agent execution later?
   - Which existing skills to integrate first?

---

## Open Questions

1. **Approval UX**: How do you want to approve/reject steps?
   - In-line during conversation?
   - Separate `/task approve` command?
   - Both?

2. **Skill allowlisting**: Should the orchestrator:
   - Use all available skills?
   - Have a configurable allowlist?
   - Ask user each time?

3. **Persistence**: Where should `.agent/` live?
   - In each project (isolated)?
   - In `~/.claude/agent/` (global)?
   - Configurable?

4. **Error handling**: When a step fails:
   - Auto-retry?
   - Ask user?
   - Fail entire task?

---

## Summary

Your repository is already 80% of a multi-agent OS. The missing piece is an **orchestration layer** that coordinates agents around goals. We build this as a **single skill** (`agent-orchestrator`) that:

1. Accepts goals
2. Spawns a Planner to create structured plans
3. Executes plans via Implementer with approval gates
4. Validates via Reviewer
5. Stores state in simple JSON files

This approach:
- Leverages your existing skill investment
- Uses Claude Code's native capabilities
- Avoids infrastructure overhead
- Can be built incrementally
- Enables future enhancements

The ChatGPT conversation gave us the conceptual model. Now we implement it the Claude Code way.
