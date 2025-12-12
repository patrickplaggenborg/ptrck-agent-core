# Braintrust Skills - Refactored Structure

Successfully refactored the monolithic Braintrust skill into 4 focused, workflow-based skills for improved token efficiency and better skill triggering.

## Skills Overview

### 1. braintrust-core (3.5KB)
**Purpose**: Project management and workspace setup
**When to use**: Creating projects, listing projects, initial setup
**Tools**: `braintrust_projects.py`

**Key operations**:
- List all projects
- Create new projects
- Get project details
- Update project metadata
- Delete projects

**Typical usage**: Used during initial setup or administrative tasks. Rarely needed after project creation.

---

### 2. braintrust-experimentation (11KB)
**Purpose**: Core AI experimentation workflow (prompts, datasets, experiments)
**When to use**: Day-to-day experimentation, prompt engineering, model testing
**Tools**: `braintrust_prompts.py`, `braintrust_datasets.py`, `braintrust_experiments.py`

**Key operations**:
- Create and iterate on prompts
- Build and manage test datasets
- Run experiments and analyze results
- Compare experiment performance

**Typical usage**: This is the main skill for AI development workflows. Most frequently used.

---

### 3. braintrust-evaluation (4.8KB)
**Purpose**: Run evaluations locally and push code to Braintrust
**When to use**: Running evals, CI/CD integration, serverless deployment
**Tools**: `braintrust_eval.py`

**Key operations**:
- Run evaluation scripts locally
- Watch mode for rapid iteration
- Filter specific test cases
- Push functions to Braintrust platform
- Development mode debugging

**Typical usage**: Used when running automated evaluations or deploying code.

---

### 4. braintrust-logs (5.2KB)
**Purpose**: Production monitoring and observability
**When to use**: Monitoring production systems, analyzing user interactions, debugging
**Tools**: `braintrust_logs.py`

**Key operations**:
- Insert production logs
- Fetch and filter logs
- Add user feedback
- Analyze production patterns

**Typical usage**: Used for production monitoring, separate from experimentation.

---

## Token Efficiency Comparison

### Before (Single Unified Skill):
- **Metadata**: ~50 words (always loaded)
- **SKILL.md**: ~2,500 words (loaded when skill triggers)
- **Total when triggered**: ~2,550 words

**Problem**: Even when only working with prompts, all documentation for projects, logs, and eval is loaded.

### After (Split Skills):
- **Metadata**: ~50 words × 4 = 200 words (always loaded)
- **SKILL.md per skill**:
  - braintrust-core: ~600 words
  - braintrust-experimentation: ~1,800 words
  - braintrust-evaluation: ~1,200 words
  - braintrust-logs: ~1,500 words

**Example Scenario**: Working with prompts, datasets, and experiments only
- **Before**: 2,550 words loaded (includes unused logs, eval, projects docs)
- **After**: ~1,800 words loaded (only experimentation skill)
- **Savings**: ~30% reduction in token usage

## Installation

Each skill is packaged as a separate zip file:

```bash
# Install all skills
unzip braintrust-core.zip -d ~/.claude/skills/
unzip braintrust-experimentation.zip -d ~/.claude/skills/
unzip braintrust-evaluation.zip -d ~/.claude/skills/
unzip braintrust-logs.zip -d ~/.claude/skills/
```

Or install selectively based on your needs:

```bash
# Minimal setup (just experimentation)
unzip braintrust-experimentation.zip -d ~/.claude/skills/

# Add project management when needed
unzip braintrust-core.zip -d ~/.claude/skills/
```

## Prerequisites

All skills require:
1. Braintrust SDK: `pip install braintrust`
2. API key: `export BRAINTRUST_API_KEY=your_api_key_here`

## Typical Workflow Progression

### Initial Setup
1. **braintrust-core**: Create or select project → Get PROJECT_ID

### Daily Experimentation
2. **braintrust-experimentation**:
   - Create prompts
   - Build datasets
   - Run experiments
   - Analyze results
   - Iterate

### Evaluation & Testing
3. **braintrust-evaluation**: Run automated evaluations

### Production Monitoring
4. **braintrust-logs**: Monitor production usage, collect feedback

## Design Benefits

✅ **Token Efficiency**: Only load documentation for workflows you're actually using
✅ **Faster Triggering**: More specific descriptions = better skill selection
✅ **Clear Mental Model**: Workflow-based organization matches user thinking
✅ **Modular Installation**: Install only the skills you need
✅ **Independent Updates**: Update individual skills without affecting others
✅ **Better Context**: Each SKILL.md is focused and comprehensive for its domain

## Distribution Files

- [braintrust-core.zip](braintrust-core.zip) - 3.5KB
- [braintrust-experimentation.zip](braintrust-experimentation.zip) - 11KB
- [braintrust-evaluation.zip](braintrust-evaluation.zip) - 4.8KB
- [braintrust-logs.zip](braintrust-logs.zip) - 5.2KB

All skills are validated and ready for distribution!
