---
name: skill-retrospective
description: Analyze conversations to identify opportunities for creating new skills. This skill should be used when explicitly requested, or proactively when patterns emerge such as workarounds being discovered, the same code being rewritten, recurring gotchas or best practices being noted, or multi-step workflows being developed.
---

# Skill Retrospective

Analyze the current conversation to identify opportunities for creating new skills that could benefit future work.

## When to Activate

### Manual Trigger
- User explicitly asks to analyze the conversation for skill opportunities
- User asks "what skills could we create from this?"
- User requests a "skill retrospective" or "skill review"

### Automatic/Proactive Trigger
Activate when any of these patterns emerge during a conversation:
- A workaround or non-obvious solution was discovered
- The same code or commands were written multiple times
- A gotcha, pitfall, or best practice was identified
- A multi-step workflow was developed that could be reused
- Domain-specific knowledge was uncovered that isn't obvious

## Skill Opportunity Types

### Insight-Based Skills (Noun Names)
Knowledge, reminders, gotchas, and best practices. These contain information that helps avoid mistakes or provides guidance.

**Naming convention**: Use noun-based names describing the knowledge domain
- Examples: `web-fetch-cache-reminder`, `api-rate-limit-awareness`, `postgres-connection-pooling`

**Characteristics**:
- Short SKILL.md (usually <500 words)
- No scripts or complex resources needed
- Triggered proactively based on context
- Often discovered when something unexpected happens

### Action-Based Skills (Verb Names)
Workflows, automation, scripts, and multi-step procedures. These help execute tasks.

**Naming convention**: Use verb-based names describing the action
- Examples: `git-auto-commit`, `publish-skill`, `fetch-mcp-tools`, `sync-datasets`

**Characteristics**:
- May include scripts in `scripts/` directory
- May include reference documentation in `references/`
- Often triggered by explicit user request
- Usually discovered when the same steps are repeated

## Analysis Process

### Step 1: Identify Patterns
Scan the conversation for:
1. **Workarounds discovered** - "I found that you need to..." or "The trick is..."
2. **Repeated code/commands** - Same operations performed multiple times
3. **Gotchas and warnings** - "Watch out for..." or "Don't forget to..."
4. **Multi-step procedures** - Sequential operations that form a workflow
5. **Domain knowledge** - Specific information about APIs, tools, or systems

### Step 2: Classify Each Opportunity
For each potential skill identified, determine:
- Is it insight-based (knowledge) or action-based (workflow)?
- What would trigger this skill?
- How reusable is it across different contexts?

### Step 3: Check Against Existing Skills
Before suggesting a new skill, check existing skills in `~/.claude/skills/` and `.claude/skills/` for overlap.

If overlap exists:
- Note the existing skill
- Suggest whether to enhance the existing skill or create a new one
- Explain what would be different

### Step 4: Present Suggestions

For each skill opportunity, provide:

```
## Skill Opportunity: [proposed-skill-name]

**Type**: Insight-based / Action-based
**Trigger**: [When should this skill activate?]

**What it would do**:
[2-3 sentence description]

**Evidence from conversation**:
[Quote or reference the specific moment that suggests this skill]

**Overlap check**:
- No overlap with existing skills
- OR: Overlaps with [skill-name] - [recommendation]

**Confidence**: High / Medium / Low
```

## Output Format

Present findings as a structured report:

```
# Skill Retrospective

## Summary
[1-2 sentences about what was found]

## Opportunities Identified

### 1. [skill-name]
[Full opportunity template from above]

## Recommendations
[Priority-ordered list of which skills to create]

## Next Steps
To create any of these skills, use the `skill-creator` skill.
```

## Important Notes

- **Do NOT automatically create skills** - Only suggest opportunities
- **Quality over quantity** - Only suggest skills that would genuinely be reused
- **Low threshold for insight-based skills** - Even small gotchas can be valuable
- **Higher threshold for action-based skills** - Should save significant effort
- **Consider context** - Some patterns are project-specific, not universal
