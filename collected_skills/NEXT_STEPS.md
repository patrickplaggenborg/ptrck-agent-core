# Next Steps for ptrck-agent-core

Action items for getting started with your agent swarm foundation.

---

## Phase 1: Learn the Patterns (Do This First)

### Read These 3 Meta-Skills in Order:

- [ ] **Read [skill-creator/SKILL.md](skills/skill-creator/SKILL.md)**
  - Focus on: Progressive disclosure, resource bundling (scripts/references/assets)
  - Note: This is Anthropic's official approach
  - Time: ~15 minutes

- [ ] **Read [mcp-builder/SKILL.md](skills/mcp-builder/SKILL.md)**
  - Focus on: Agent-centric design principles, evaluation-driven development
  - Note: Critical for building tool integrations
  - Time: ~20 minutes

- [ ] **Read [writing-skills/SKILL.md](skills/writing-skills/SKILL.md)**
  - Focus on: TDD for skills, baseline testing, rationalization prevention
  - Note: Compare with skill-creator approach
  - Time: ~10 minutes

**Key Question**: How do skill-creator (structure) and writing-skills (quality) complement each other?

---

## Phase 2: Internalize the Iron Laws

### Read These 3 Discipline Skills:

- [ ] **Read [test-driven-development/SKILL.md](skills/test-driven-development/SKILL.md)**
  - Iron Law: "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"
  - Read the rationalization table
  - Time: ~10 minutes

- [ ] **Read [verification-before-completion/SKILL.md](skills/verification-before-completion/SKILL.md)**
  - Iron Law: "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"
  - Understand IDENTIFY → RUN → READ → VERIFY → CLAIM
  - Time: ~10 minutes

- [ ] **Read [systematic-debugging/SKILL.md](skills/systematic-debugging/SKILL.md)**
  - Iron Law: "NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST"
  - Understand the 4-phase process
  - Time: ~10 minutes

**Key Question**: Why do these laws exist? What failures do they prevent?

---

## Phase 3: Understand Agent Orchestration

### Read These Core Orchestration Skills:

- [ ] **Read [writing-plans/SKILL.md](skills/writing-plans/SKILL.md)**
  - Focus on: 2-5 minute task breakdown, complete code examples
  - Time: ~10 minutes

- [ ] **Read [subagent-driven-development/SKILL.md](skills/subagent-driven-development/SKILL.md)**
  - Focus on: Fresh subagents per task, code review checkpoints
  - Time: ~10 minutes

- [ ] **Read [executing-plans/SKILL.md](skills/executing-plans/SKILL.md)**
  - Focus on: Batch execution, human checkpoints
  - Compare with subagent-driven-development
  - Time: ~10 minutes

- [ ] **Read [dispatching-parallel-agents/SKILL.md](skills/dispatching-parallel-agents/SKILL.md)**
  - Focus on: When to parallelize, independent domains
  - Time: ~5 minutes

**Key Question**: When would you use subagent-driven vs executing-plans vs parallel dispatch?

---

## Phase 4: Customize for Your Use

### Immediate Customizations:

- [ ] **Adapt using-superpowers → using-ptrck-agent-core**
  - Copy `skills/using-superpowers/SKILL.md`
  - Rename to `skills/using-ptrck-agent-core/SKILL.md`
  - Update references from "superpowers" to "ptrck-agent-core"
  - Update skill list to reference your 13 skills
  - Time: ~15 minutes

- [ ] **Review claude-agent-sdk**
  - Read [claude-agent-sdk/SKILL.md](skills/claude-agent-sdk/SKILL.md)
  - Understand `query()` API, MCP integration
  - Compare with mcp-builder for MCP-specific patterns
  - Time: ~15 minutes

- [ ] **Optional: Copy to your ptrck-agent-core repo**
  - Decide if you want to move this to `/Users/patrick/git/ptrck/ptrck-agent-core/.claude/skills/`
  - Or keep it here as reference
  - Time: ~5 minutes

---

## Phase 5: Test Your Understanding

### Create Your First Skill Using Both Approaches:

- [ ] **Choose a simple skill to create**
  - Something you actually need
  - Example: "error-logging" (how to log errors in your codebase)
  - Example: "api-response-formatting" (standard format for API responses)

- [ ] **Apply skill-creator approach**
  - Use `skills/skill-creator/scripts/init_skill.py` if available
  - Create SKILL.md with progressive disclosure
  - Organize into scripts/references/assets if needed

- [ ] **Apply writing-skills approach**
  - Create baseline test (agent without skill)
  - Create rationalization table
  - Test with subagent under pressure

- [ ] **Package and validate**
  - Use skill-creator packaging tools
  - Verify skill works as expected

**Key Question**: Which approach was more helpful? How can you use both together?

---

## Phase 6: Reference Other Skills

### When Needed, Read These:

- [ ] **[requesting-code-review/SKILL.md](skills/requesting-code-review/SKILL.md)**
  - When: After completing tasks that need review
  - Time: ~5 minutes

- [ ] **[using-superpowers/SKILL.md](skills/using-superpowers/SKILL.md)**
  - When: To understand entry protocol pattern
  - Time: ~5 minutes

---

## Common Pitfalls to Avoid

### Don't:
- ❌ Skip reading the meta-skills and jump straight to coding
- ❌ Violate the Iron Laws ("just this once")
- ❌ Copy all 261 skills from ClaudeSkillz into this core
- ❌ Create skills without testing them with agents first
- ❌ Ignore rationalization tables (they exist for a reason)

### Do:
- ✅ Read meta-skills FIRST to understand both approaches
- ✅ Internalize the Iron Laws and their rationalization tables
- ✅ Test every new skill with actual agents
- ✅ Keep this core lean - only add skills you truly need
- ✅ Use both skill-creator (structure) and writing-skills (quality)

---

## Decision Points

### "Should I add more skills from the source collections?"

**Before adding any skill, ask:**
1. Do I need this skill NOW, or might I need it someday?
2. Can I accomplish this without a dedicated skill?
3. Will this skill be used repeatedly, or just once?

**If "now + repeatedly"**: Copy it
**If "maybe someday"**: Leave it in source collection, copy when needed
**If "just once"**: Don't create a skill, just do it

**Keep this core lean.** The power is in the discipline, not the quantity.

---

## Validation Checklist

After Phase 4, verify you can answer:

- [ ] What's the difference between skill-creator and writing-skills approaches?
- [ ] What are the 3 Iron Laws and when do they apply?
- [ ] When would I use subagent-driven-development vs executing-plans?
- [ ] How does progressive disclosure work in skills?
- [ ] What's in scripts/ vs references/ vs assets/?
- [ ] How do I prevent rationalizing away the Iron Laws?
- [ ] When should I dispatch parallel agents?

If you can't answer these, re-read the relevant skills.

---

## Timeline

**Realistic timeline for phases 1-4:**
- Phase 1 (Learn patterns): 45 minutes
- Phase 2 (Iron Laws): 30 minutes
- Phase 3 (Orchestration): 35 minutes
- Phase 4 (Customize): 30 minutes
- **Total: ~2.5 hours**

**Don't rush.** Understanding these patterns will save you days of mistakes.

---

## Success Criteria

You're ready to build agent swarms when you:

1. ✅ Understand both Anthropic's and Superpowers' approaches to skills
2. ✅ Can recite the 3 Iron Laws without looking
3. ✅ Know when to use each orchestration pattern
4. ✅ Have created at least one skill using both approaches
5. ✅ Have adapted using-superpowers to using-ptrck-agent-core
6. ✅ Can explain why the Iron Laws exist (what failures they prevent)

---

## Resources

- **Full Analysis**: [../REPOSITORY_ANALYSIS.md](../REPOSITORY_ANALYSIS.md)
- **Quick Reference**: [SKILLS_INDEX.md](SKILLS_INDEX.md)
- **This Collection**: [README.md](README.md)

---

## Questions to Consider

As you go through these phases, think about:

1. **What patterns from Anthropic do I want to adopt?**
   - Progressive disclosure?
   - Resource bundling?
   - Evaluation-driven development?

2. **Which Iron Laws resonate most with problems I've faced?**
   - Shipping code without tests?
   - Claiming completion without verification?
   - Fixing symptoms instead of root causes?

3. **What agent orchestration patterns fit my use case?**
   - Single-session subagent-driven?
   - Multi-session batch execution?
   - Parallel independent agents?

4. **What's my first real skill I need to create?**
   - What problem does it solve?
   - Will it be used repeatedly?
   - How will I test it?

---

## Final Note

**This is a foundation, not a complete system.**

You'll build your own domain-specific skills on top of this. These 13 skills teach you:
- How to create skills (meta-skills)
- How to maintain quality (Iron Laws)
- How to coordinate agents (orchestration)

Everything else is domain-specific. Build it when you need it, following these patterns.

**Start with Phase 1. Read the meta-skills. Everything else builds from there.**
