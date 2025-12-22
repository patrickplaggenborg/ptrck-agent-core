---
name: braintrust-scorers
description: Manage Braintrust scorers (project scores) for evaluating AI outputs. Use this skill when listing available scorers, creating custom scorers, or managing scoring functions for experiments.
---

# Braintrust Scorers

Manage scorers (project scores) for evaluating AI model outputs with built-in and custom scoring functions.

## When to Use This Skill

Use this skill when the user wants to:
- List available scorers in a project
- Get details about a specific scorer
- Create custom scorers (code-based or LLM-as-a-judge)
- Update existing scorers
- Delete scorers
- Find the right scorer ID for experiments

## What Are Scorers?

Scorers in Braintrust evaluate LLM outputs and assign performance scores (0-100%). There are two types:

### 1. Global Scorers (Built-in)
Pre-built scorers from the autoevals library, referenced by name (not ID):
- `Factuality` - Checks if output is factually correct
- `ExactMatch` - Exact string matching
- `Levenshtein` - String similarity scoring
- `ContextRecall` - For RAG systems
- And many more...

**Note**: Global scorers are referenced by name in experiments (e.g., `"Factuality"`), not by ID.

### 2. Custom Scorers (Functions)
User-defined scoring functions stored as Braintrust functions:
- Code-based (TypeScript/Python)
- LLM-as-a-judge (using prompts)
- Project-specific evaluation logic
- Referenced by **function ID** in experiments

**Important**: Scorers are stored as functions with `function_type: "scorer"` in Braintrust, not as separate project_score objects.

## Prerequisites

Before using this skill:

1. **Braintrust API key configured**:
   - Set in `.env` file: `BRAINTRUST_API_KEY=your_api_key_here` (automatically loaded)
   - Or export manually: `export BRAINTRUST_API_KEY=your_api_key_here`
2. **Project ID available**: Use `braintrust-core` skill to list or create projects

**Note**: All scripts automatically load environment variables from a `.env` file in the current directory if it exists.

## Tags Support

Scorers support tags for organization. Tags format:
- **JSON array**: `'["tag1", "tag2"]'` - multiple tags
- **Single string**: `"production"` - converted to `["production"]`
- **Empty array**: `'[]'` - clears all tags

When updating, `--tags` replaces all existing tags (not a merge).

## Available Commands

All tools are Python scripts in the `scripts/` directory. Execute with `python3` and appropriate arguments.

### Scorer Management (`braintrust_scorers.py`)

**Commands:**
- `list` - List all scorers/project scores in a project
- `get` - Get a specific scorer by ID
- `create` - Create a new custom scorer
- `update` - Update an existing scorer
- `delete` - Delete a scorer

### Common Usage

```bash
# List all scorers in a project
python3 .claude/skills/braintrust-scorers/scripts/braintrust_scorers.py list \
  --project-id PROJECT_ID

# Get details about a specific scorer
python3 .claude/skills/braintrust-scorers/scripts/braintrust_scorers.py get SCORER_ID

# Create a custom Python scorer
python3 .claude/skills/braintrust-scorers/scripts/braintrust_scorers.py create \
  --name "My Custom Scorer" \
  --project-id PROJECT_ID \
  --description "Evaluates X based on Y criteria" \
  --scorer-type python \
  --config-file scorer_config.json

# Create scorer with tags
python3 .claude/skills/braintrust-scorers/scripts/braintrust_scorers.py create \
  --name "Production Scorer" \
  --project-id PROJECT_ID \
  --tags '["production", "v2"]' \
  --description "Production scoring function"

# Update a scorer
python3 .claude/skills/braintrust-scorers/scripts/braintrust_scorers.py update SCORER_ID \
  --name "Updated Scorer Name" \
  --description "Updated description"

# Update scorer tags
python3 .claude/skills/braintrust-scorers/scripts/braintrust_scorers.py update SCORER_ID \
  --tags '["deprecated"]'

# Delete a scorer
python3 .claude/skills/braintrust-scorers/scripts/braintrust_scorers.py delete SCORER_ID
```

## Scorer Configuration Format

When creating custom scorers, provide configuration in JSON format:

```json
{
  "name": "My Scorer",
  "project_id": "PROJECT_ID",
  "description": "What this scorer evaluates",
  "score_type": "python",
  "config": {
    "code": "def score(output, expected, input=None):\n    # Your scoring logic\n    return score_value"
  }
}
```

## Integration with Other Skills

- **`braintrust-core`**: Get project IDs before listing scorers
- **`braintrust-launch-experiment`**: Use scorer IDs when launching experiments
- **`braintrust-experimentation`**: Reference scorers in experiment configurations

## Common Workflows

### Find Scorer for Experiment
1. List scorers in your project: `python3 braintrust_scorers.py list --project-id PROJECT_ID`
2. Review available scorers and their descriptions
3. Note the scorer ID or name
4. Use in experiment launch with `braintrust-launch-experiment` skill

### Create Custom Scorer
1. Define scoring logic (Python/TypeScript code or LLM prompt)
2. Create scorer configuration JSON
3. Create scorer: `python3 braintrust_scorers.py create ...`
4. Test scorer in an experiment
5. Iterate and update as needed

## Output Format

All commands output JSON for easy parsing and integration. Save scorer IDs from responses for use in experiments.

## Error Handling

Tools provide detailed error messages for:
- Missing or invalid API key
- Network connectivity issues
- Invalid scorer IDs
- JSON format validation errors
- Missing required parameters

## Reference Documentation

- Braintrust Scorers Guide: https://www.braintrust.dev/docs/platform/functions/scorers
- Functions API: https://www.braintrust.dev/docs/reference/api/Functions
- Autoevals Library: https://github.com/braintrustdata/autoevals

## Important Notes

- **Scorers are Functions**: This skill uses the `/v1/function` API endpoint, not `/v1/project_score`
- **Function Type Filter**: Lists only functions with `function_type: "scorer"`
- **Access Control**: Service accounts need ACL permissions to read scorer functions
- **Global vs Custom**: Global scorers (Factuality, ExactMatch) are referenced by name; custom scorers are referenced by function ID
