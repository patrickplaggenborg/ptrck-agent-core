# ptrck-agent-core

**Foundation Skills for Building Agent Swarms**

This collection contains 13 carefully curated skills that form the foundation for building reliable, high-quality agent swarm systems. These skills combine Anthropic's official patterns with proven community methodologies.

---

## Contents

### 🏆 TIER 0: Meta-Skills (3 skills)
**Learn these patterns FIRST before building your own skills**

1. **[skill-creator](skills/skill-creator/)** (Anthropic Official)
   - Progressive disclosure principle
   - Resource bundling (scripts/references/assets)
   - Packaging & validation tools
   - 6-step creation process

2. **[mcp-builder](skills/mcp-builder/)** (Anthropic Official)
   - Agent-centric design principles
   - Evaluation-driven development
   - 4-phase MCP server implementation
   - Python & TypeScript guides

3. **[writing-skills](skills/writing-skills/)** (Superpowers)
   - TDD approach to skill creation
   - Baseline testing (watch agents fail without skill)
   - Rationalization prevention tables
   - CSO (Claude Search Optimization)

---

### ⭐ TIER 1: Core Methodology (5 skills)
**Iron Laws - Non-negotiable disciplines**

4. **[test-driven-development](skills/test-driven-development/)** (Superpowers)
   - Iron Law: "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"
   - RED-GREEN-REFACTOR cycle
   - Rationalization prevention

5. **[verification-before-completion](skills/verification-before-completion/)** (Superpowers)
   - Iron Law: "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"
   - IDENTIFY → RUN → READ → VERIFY → CLAIM gate

6. **[systematic-debugging](skills/systematic-debugging/)** (Superpowers)
   - Iron Law: "NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST"
   - 4-phase debugging process

7. **[using-superpowers](skills/using-superpowers/)** (Superpowers)
   - Mandatory entry protocol
   - Skill discovery before action
   - **TODO**: Adapt this to "using-ptrck-agent-core"

8. **[claude-agent-sdk](skills/claude-agent-sdk/)** (ClaudeSkillz)
   - Programmatic Claude interaction
   - MCP server integration
   - Subagent orchestration patterns

---

### 🔧 TIER 2: Agent Orchestration (5 skills)
**Core patterns for building agent swarms**

9. **[writing-plans](skills/writing-plans/)** (Superpowers)
   - Bite-sized tasks (2-5 minute increments)
   - Complete code examples with file paths
   - TDD/YAGNI/DRY principles

10. **[subagent-driven-development](skills/subagent-driven-development/)** (Superpowers)
    - Execute plans with fresh subagents
    - Code review after each task
    - Same-session execution

11. **[executing-plans](skills/executing-plans/)** (Superpowers)
    - Batch execution with checkpoints
    - 3-task default batches
    - Parallel session execution

12. **[dispatching-parallel-agents](skills/dispatching-parallel-agents/)** (Superpowers)
    - Parallelize independent investigations
    - ~40% faster for multi-domain issues

13. **[requesting-code-review](skills/requesting-code-review/)** (Superpowers)
    - Quality gate for completed work
    - Categorize issues: Critical/Important/Minor
    - Auto-integration with subagent-driven-development

---

## Skill Philosophy

This collection combines three complementary approaches:

### 1. Anthropic's Official Patterns (skill-creator, mcp-builder)
- **Focus**: Structure, progressive disclosure, agent-centric design
- **Teaches**: HOW Anthropic thinks about skill design
- **Use for**: Learning official patterns, building MCP servers

### 2. Superpowers Methodology (most skills)
- **Focus**: Discipline, "Iron Laws", rationalization prevention
- **Teaches**: Quality through verification and testing
- **Use for**: Agent orchestration, preventing quality erosion

### 3. Community SDK (claude-agent-sdk)
- **Focus**: Programmatic agent control
- **Teaches**: Building agents programmatically
- **Use for**: Agent swarm foundation

---

## Conceptual Hierarchy

```
LEARN FIRST (Meta-skills):
    skill-creator → mcp-builder → writing-skills
    ↓
    Apply these patterns to build
    ↓

CORE METHODOLOGY:
    using-ptrck-agent-core (entry protocol)
    ↓
    test-driven-development (every task)
    verification-before-completion (every claim)
    systematic-debugging (every bug)
    ↓
    claude-agent-sdk (agent foundation)
    ↓

AGENT ORCHESTRATION:
    writing-plans
    ├── subagent-driven-development
    │   ├── requesting-code-review (after each task)
    │   └── dispatching-parallel-agents (when parallel)
    └── executing-plans
        └── (same review/parallel patterns)
```

---

## Getting Started

### Step 1: Learn the Patterns
Read these three meta-skills to understand how to create skills:
1. [skill-creator](skills/skill-creator/SKILL.md) - Anthropic's official approach
2. [mcp-builder](skills/mcp-builder/SKILL.md) - Building MCP servers
3. [writing-skills](skills/writing-skills/SKILL.md) - TDD for skills

**Compare approaches**: Anthropic focuses on structure, Superpowers on quality through testing.

### Step 2: Adopt the Iron Laws
Read and internalize these non-negotiable disciplines:
- [test-driven-development](skills/test-driven-development/SKILL.md)
- [verification-before-completion](skills/verification-before-completion/SKILL.md)
- [systematic-debugging](skills/systematic-debugging/SKILL.md)

### Step 3: Understand Agent Orchestration
Learn how to coordinate multiple agents:
- [writing-plans](skills/writing-plans/SKILL.md)
- [subagent-driven-development](skills/subagent-driven-development/SKILL.md)

### Step 4: Customize for Your Use
- Adapt [using-superpowers](skills/using-superpowers/) to "using-ptrck-agent-core"
- Add your own domain-specific skills following the meta-skill patterns

---

## Next Steps

### Immediate TODOs
1. **Adapt using-superpowers** → Create `using-ptrck-agent-core` skill
2. **Read all meta-skills** to understand both Anthropic and Superpowers approaches
3. **Test first skill creation** using both skill-creator and writing-skills patterns

### Future Additions
As you need them, consider adding from the source collections:
- **From awesome-claude-skills-master**:
  - document-skills/ (docx, pdf, pptx, xlsx) - if you need document processing
  - webapp-testing - if you need Playwright integration

- **From ClaudeSkillz**:
  - claude-code-bash-patterns - if you use bash heavily
  - Domain-specific tools (Docker, cloud, etc) - as needed

- **From Superpowers**:
  - brainstorming - for design refinement
  - using-git-worktrees - for isolated development
  - finishing-a-development-branch - for merge/PR workflow

---

## Key Characteristics

✅ **Follows Anthropic's official best practices** (skill-creator, mcp-builder)
✅ **Enforces quality through "Iron Laws"** (TDD, verification, debugging)
✅ **Enables sophisticated agent orchestration** (subagent-driven, parallel dispatch)
✅ **Prevents rationalization and quality erosion** (explicit anti-patterns)
✅ **Provides both approaches to skill creation** (structure + testing)

---

## Sources

- **awesome-claude-skills-master**: https://github.com/anthropics/skills (Official Anthropic)
- **superpowers**: https://github.com/obra/superpowers (Jesse Vincent)
- **ClaudeSkillz**: https://github.com/jackspace/ClaudeSkillz (Community)

For detailed analysis of why these skills were chosen, see [../REPOSITORY_ANALYSIS.md](../REPOSITORY_ANALYSIS.md)

---

## Philosophy

> "Start with Anthropic's patterns, enforce with Superpowers' discipline, orchestrate with proven agent techniques."

This collection is designed to:
- Teach you the RIGHT way to create skills (meta-skills)
- Prevent common quality pitfalls (Iron Laws)
- Enable sophisticated multi-agent coordination (orchestration)
- Provide both official and battle-tested patterns (complementary approaches)

**Don't bloat this core.** Add skills only when you truly need them. Keep this foundation lean and focused.
