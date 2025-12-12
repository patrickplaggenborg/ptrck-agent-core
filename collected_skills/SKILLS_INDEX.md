# Skills Index

Quick reference for all 13 foundational skills in ptrck-agent-core.

---

## By Category

### 🏆 Meta-Skills (How to Create Skills)
| Skill | Source | Key Concept | When to Use |
|-------|--------|-------------|-------------|
| [skill-creator](skills/skill-creator/) | Anthropic | Progressive disclosure, resource bundling | Creating any new skill |
| [mcp-builder](skills/mcp-builder/) | Anthropic | Agent-centric design, evaluation-driven | Building MCP servers |
| [writing-skills](skills/writing-skills/) | Superpowers | TDD on documentation | Creating bulletproof skills |

### ⭐ Core Methodology (Iron Laws)
| Skill | Iron Law | When to Apply |
|-------|----------|---------------|
| [test-driven-development](skills/test-driven-development/) | NO PRODUCTION CODE WITHOUT FAILING TEST FIRST | Every implementation |
| [verification-before-completion](skills/verification-before-completion/) | NO COMPLETION CLAIMS WITHOUT VERIFICATION | Every completion claim |
| [systematic-debugging](skills/systematic-debugging/) | NO FIXES WITHOUT ROOT CAUSE FIRST | Every bug/failure |
| [using-superpowers](skills/using-superpowers/) | CHECK FOR SKILLS BEFORE ANY ACTION | Every task (adapt to ptrck) |
| [claude-agent-sdk](skills/claude-agent-sdk/) | - | Building agents programmatically |

### 🔧 Agent Orchestration
| Skill | Purpose | Output |
|-------|---------|--------|
| [writing-plans](skills/writing-plans/) | Break work into 2-5 min tasks | Detailed implementation plan |
| [subagent-driven-development](skills/subagent-driven-development/) | Execute plan with fresh subagents | Same-session, reviewed tasks |
| [executing-plans](skills/executing-plans/) | Execute plan in batches | 3-task batches with checkpoints |
| [dispatching-parallel-agents](skills/dispatching-parallel-agents/) | Parallelize independent work | ~40% faster multi-domain |
| [requesting-code-review](skills/requesting-code-review/) | Quality gate after tasks | Critical/Important/Minor issues |

---

## By Use Case

### "I need to create a new skill"
1. Read [skill-creator](skills/skill-creator/SKILL.md) for structure
2. Read [writing-skills](skills/writing-skills/SKILL.md) for quality approach
3. Use both: skill-creator for organization, writing-skills for testing

### "I need to build an MCP server"
1. Read [mcp-builder](skills/mcp-builder/SKILL.md)
2. Follow 4-phase process: Research → Implement → Review → Evaluate
3. Use agent-centric design principles

### "I need to implement a feature"
1. [writing-plans](skills/writing-plans/) - Create implementation plan
2. [test-driven-development](skills/test-driven-development/) - Write tests first
3. [subagent-driven-development](skills/subagent-driven-development/) - Execute with subagents
4. [verification-before-completion](skills/verification-before-completion/) - Verify completion

### "I have a bug to fix"
1. [systematic-debugging](skills/systematic-debugging/) - Find root cause FIRST
2. [test-driven-development](skills/test-driven-development/) - Write failing test
3. [verification-before-completion](skills/verification-before-completion/) - Verify fix works

### "I'm starting any task"
1. [using-superpowers](skills/using-superpowers/) - Check for applicable skills FIRST
2. Apply relevant skills from above
3. Follow Iron Laws throughout

### "I have multiple independent issues"
1. [dispatching-parallel-agents](skills/dispatching-parallel-agents/) - One agent per domain
2. Each agent follows TDD + verification
3. Review results when all complete

---

## Workflow Patterns

### Pattern 1: Single Feature Implementation
```
using-ptrck-agent-core
  ↓
writing-plans (create plan)
  ↓
subagent-driven-development
  ↓ (for each task)
  test-driven-development (RED-GREEN-REFACTOR)
  requesting-code-review (after task)
  verification-before-completion (prove it works)
```

### Pattern 2: Large Multi-Session Feature
```
using-ptrck-agent-core
  ↓
writing-plans (create detailed plan)
  ↓
executing-plans (batch execution)
  ↓ (3-task batches)
  test-driven-development (each task)
  requesting-code-review (after batch)
  verification-before-completion (prove batch works)
  ↓
Report to user, get feedback, continue
```

### Pattern 3: Debugging Multiple Issues
```
using-ptrck-agent-core
  ↓
dispatching-parallel-agents (one per issue)
  ↓ (for each agent)
  systematic-debugging (root cause first)
  test-driven-development (write failing test)
  requesting-code-review (verify fix)
  verification-before-completion (prove it's fixed)
```

### Pattern 4: Creating a New Skill
```
using-ptrck-agent-core
  ↓
skill-creator (understand structure)
writing-skills (understand quality approach)
  ↓
writing-plans (plan skill creation)
  ↓
Implement skill using both patterns:
  - skill-creator: scripts/references/assets organization
  - writing-skills: baseline testing, rationalization prevention
  ↓
verification-before-completion (test skill with agents)
```

---

## Skill Combinations

### Must Always Use Together
- **test-driven-development** + **verification-before-completion**
  - TDD ensures tests exist, verification ensures they pass

- **writing-plans** + **subagent-driven-development**
  - Plans provide tasks, SDD executes them with quality gates

- **systematic-debugging** + **test-driven-development**
  - Find root cause, write test that reproduces, fix, verify

### Complementary Pairs
- **skill-creator** + **writing-skills**
  - Structure from Anthropic, quality from Superpowers

- **subagent-driven-development** + **dispatching-parallel-agents**
  - SDD for sequential tasks, parallel for independent domains

- **requesting-code-review** + **verification-before-completion**
  - Review catches issues, verification proves fixes work

---

## Quick Reference: Iron Laws

| Law | When | How to Verify |
|-----|------|---------------|
| **NO CODE WITHOUT TEST** | Before writing implementation | Watch test fail first |
| **NO CLAIM WITHOUT PROOF** | Before saying "done" | Fresh execution + read output |
| **NO FIX WITHOUT ROOT CAUSE** | Before proposing solution | 4-phase investigation complete |

Violations of Iron Laws are never acceptable. They exist because they prevent common failure modes.

---

## Rationalization Prevention

Each Iron Law skill includes a **rationalization table** listing common excuses and why they're wrong.

Example from test-driven-development:
- ❌ "The test is obvious, I'll write it after"
- ✅ Actually: If it's obvious, it takes 30 seconds. Write it first.

Example from verification-before-completion:
- ❌ "I just ran it, I know it works"
- ✅ Actually: Run it AGAIN and READ the output. Prove it.

**Read the rationalization tables** - they're there because we all try to skip steps.

---

## File Locations

All skills are in: `skills/<skill-name>/SKILL.md`

Meta-skills with bundled resources:
- `skills/skill-creator/` - Has scripts/, references/, assets/ examples
- `skills/mcp-builder/` - Has reference/ docs for Python/TypeScript

---

## Next Actions

1. **Read the 3 meta-skills** to understand patterns
2. **Internalize the 3 Iron Laws** (TDD, verification, debugging)
3. **Adapt using-superpowers** to using-ptrck-agent-core
4. **Try creating your first skill** using both skill-creator and writing-skills patterns
