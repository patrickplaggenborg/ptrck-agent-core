# Skill Activation Protocol

**CRITICAL**: Before responding to ANY user request, you MUST follow this three-step protocol:

## Step 1: Evaluate Skills (MANDATORY)

For EACH available skill, explicitly state:
- Skill name
- Does it match this request? (YES/NO)
- Brief reasoning (one sentence)

Example format:
```
Skill Evaluation:
- git-auto-commit: NO - No file modifications yet
- braintrust-core: YES - User wants to create a project
- braintrust-experimentation: NO - Not working with prompts/datasets
```

## Step 2: Activate Matching Skills (MANDATORY)

**The evaluation is WORTHLESS unless you ACTIVATE the skills.**

For EVERY skill marked YES, you MUST call `Skill(skill-name)` IMMEDIATELY.

Do NOT skip this step. Do NOT proceed to implementation without activation.

## Step 3: Implement

Only after activation, proceed with the actual work.

---

**IMPORTANT**: The `git-auto-commit` skill should be evaluated AGAIN at the END of your response if you made any file changes. If files were modified, activate it to commit changes.

---

This protocol is NON-NEGOTIABLE. Failure to follow these steps means skills will not work correctly.
