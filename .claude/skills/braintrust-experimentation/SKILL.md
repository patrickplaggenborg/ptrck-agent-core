---
name: braintrust-experimentation
description: Manage Braintrust prompts, datasets, and experiments for AI model testing and iteration. Use this skill when working with prompt engineering, managing test datasets, creating experiments, or analyzing experiment results.
---

# Braintrust Experimentation

Comprehensive management of prompts, datasets, and experiments for AI model testing and iteration workflows.

## When to Use This Skill

Use this skill when the user wants to:
- Create, update, or manage AI prompts
- Build and maintain test datasets
- Create and run experiments
- Insert test data or experiment results
- Analyze and summarize experiment outcomes
- Iterate on prompt engineering

This is the core skill for day-to-day AI experimentation workflows on Braintrust.

## Prerequisites

Before using this skill:

1. **Braintrust SDK installed**: `pip install braintrust`
2. **API key configured**:
   - Set in `.env` file: `BRAINTRUST_API_KEY=your_api_key_here` (automatically loaded)
   - Or export manually: `export BRAINTRUST_API_KEY=your_api_key_here`
3. **Project ID available**: Use `braintrust-core` skill to list or create projects

**Note**: All scripts automatically load environment variables from a `.env` file in the current directory if it exists.

## Available Tools

All tools are Python scripts in the `scripts/` directory. Execute with `python3` and appropriate arguments.

### 1. Prompt Management (`braintrust_prompts.py`)

Manage AI prompts with versioning and template support.

**Commands:**
- `list` - List all prompts (filter with `--project-id`)
- `get` - Get a specific prompt by ID
- `create` - Create a new prompt
- `update` - Update an existing prompt
- `delete` - Delete a prompt

**Prompt Data Format:**
Prompt data can be JSON or plain text. Plain text is automatically wrapped as `{"prompt": "text"}`.

**Common Usage:**
```bash
# List prompts for a project
python3 .claude/skills/braintrust-experimentation/scripts/braintrust_prompts.py list --project-id PROJECT_ID

# Create a simple prompt (slug auto-generated from name)
python3 .claude/skills/braintrust-experimentation/scripts/braintrust_prompts.py create \
  --name "QA Assistant" \
  --project-id PROJECT_ID \
  --prompt-data "You are a helpful assistant that answers questions accurately."

# Create with custom slug
python3 .claude/skills/braintrust-experimentation/scripts/braintrust_prompts.py create \
  --name "QA Assistant" \
  --slug "qa-assistant-v2" \
  --project-id PROJECT_ID \
  --prompt-data "You are a helpful assistant that answers questions accurately."

# Create with JSON template
python3 .claude/skills/braintrust-experimentation/scripts/braintrust_prompts.py create \
  --name "Structured Prompt" \
  --project-id PROJECT_ID \
  --prompt-data '{"prompt": "Answer about {{topic}}", "model": "gpt-4", "temperature": 0.7}'

# Get current prompt version
python3 .claude/skills/braintrust-experimentation/scripts/braintrust_prompts.py get PROMPT_ID

# Update prompt
python3 .claude/skills/braintrust-experimentation/scripts/braintrust_prompts.py update PROMPT_ID \
  --prompt-data "You are a helpful and friendly assistant."

# Delete prompt
python3 .claude/skills/braintrust-experimentation/scripts/braintrust_prompts.py delete PROMPT_ID
```

### 2. Dataset Management (`braintrust_datasets.py`)

Manage test datasets with CRUD operations and data insertion.

**Commands:**
- `list` - List all datasets
- `get` - Get dataset details by ID
- `create` - Create a new dataset
- `update` - Update dataset properties
- `delete` - Delete a dataset
- `insert` - Insert events into a dataset from JSON file
- `fetch` - Fetch records from a dataset (supports `--limit`, `--cursor`)

**Dataset Event Format:**
JSON array with objects containing `input`, `expected`, and optional `metadata`:
```json
[
  {
    "input": "What is the capital of France?",
    "expected": "Paris",
    "metadata": {"category": "geography", "difficulty": "easy"}
  },
  {
    "input": "What is 2+2?",
    "expected": "4",
    "metadata": {"category": "math", "difficulty": "easy"}
  }
]
```

**Common Usage:**
```bash
# Create a dataset
python3 scripts/braintrust_datasets.py create \
  --name "QA Test Set" \
  --project-id PROJECT_ID \
  --description "General knowledge questions"

# Insert data from JSON file
python3 scripts/braintrust_datasets.py insert DATASET_ID --file test_data.json

# Fetch records to verify
python3 scripts/braintrust_datasets.py fetch DATASET_ID --limit 50

# List all datasets
python3 scripts/braintrust_datasets.py list

# Update dataset metadata
python3 scripts/braintrust_datasets.py update DATASET_ID \
  --name "Updated QA Test Set" \
  --description "Updated description"
```

### 3. Experiment Management (`braintrust_experiments.py`)

Manage experiments with full lifecycle support including results insertion and summarization.

**Commands:**
- `list` - List all experiments (filter with `--project-id`)
- `get` - Get experiment details by ID
- `create` - Create a new experiment
- `update` - Update experiment properties
- `delete` - Delete an experiment
- `insert` - Insert experiment results from JSON file
- `summarize` - Get summary statistics for an experiment

**Experiment Event Format:**
JSON array with objects containing `input`, `output`, `expected`, `scores`, and optional `metadata`:
```json
[
  {
    "input": "What is the capital of France?",
    "output": "Paris",
    "expected": "Paris",
    "scores": {
      "accuracy": 1.0,
      "relevance": 1.0
    },
    "metadata": {
      "latency_ms": 123,
      "model": "gpt-4"
    }
  },
  {
    "input": "What is 2+2?",
    "output": "4",
    "expected": "4",
    "scores": {
      "accuracy": 1.0
    },
    "metadata": {
      "latency_ms": 98
    }
  }
]
```

**Common Usage:**
```bash
# Create an experiment
python3 scripts/braintrust_experiments.py create \
  --name "GPT-4 Baseline" \
  --project-id PROJECT_ID \
  --dataset-id DATASET_ID \
  --description "Baseline experiment with GPT-4"

# Insert experiment results
python3 scripts/braintrust_experiments.py insert EXPERIMENT_ID --file results.json

# Summarize results
python3 scripts/braintrust_experiments.py summarize EXPERIMENT_ID

# List experiments for a project
python3 scripts/braintrust_experiments.py list --project-id PROJECT_ID

# Get experiment details
python3 scripts/braintrust_experiments.py get EXPERIMENT_ID
```

## Common Workflows

### Prompt Iteration Workflow
1. Create initial prompt with `braintrust_prompts.py create`
2. Test the prompt manually or with evaluations
3. Update prompt based on results with `braintrust_prompts.py update`
4. Retrieve current version with `braintrust_prompts.py get`
5. Repeat until satisfied

### Dataset Creation Workflow
1. Prepare test data in JSON format (see format above)
2. Create dataset with `braintrust_datasets.py create`
3. Insert data with `braintrust_datasets.py insert`
4. Verify data with `braintrust_datasets.py fetch`
5. Use dataset ID in experiments

### Experiment Workflow
1. Ensure prompt and dataset exist
2. Create experiment with `braintrust_experiments.py create`
3. Run model and collect results in JSON format
4. Insert results with `braintrust_experiments.py insert`
5. Analyze with `braintrust_experiments.py summarize`
6. Compare multiple experiments to find best approach

### Complete Experimentation Cycle
1. **Setup** (use `braintrust-core`): Get or create project ID
2. **Create Prompt**: Use `braintrust_prompts.py create`
3. **Create Dataset**: Use `braintrust_datasets.py create` and `insert`
4. **Create Experiment**: Use `braintrust_experiments.py create`
5. **Run Tests**: Execute model and collect results
6. **Insert Results**: Use `braintrust_experiments.py insert`
7. **Analyze**: Use `braintrust_experiments.py summarize`
8. **Iterate**: Update prompt and repeat

## Working with JSON Files

When inserting data (datasets or experiments):
1. Create JSON file with proper format (see formats above)
2. Validate JSON: `python3 -m json.tool < file.json`
3. Pass file path using `--file` argument
4. Tool will validate and insert data

## Output Format

All tools output JSON for easy parsing and integration. Save IDs from responses for chaining operations.

## Error Handling

Tools provide detailed error messages for:
- Missing or invalid API key
- Network connectivity issues
- Invalid resource IDs
- JSON format validation errors
- Missing required parameters

When errors occur:
1. Verify API key: `echo $BRAINTRUST_API_KEY`
2. Check SDK installed: `pip list | grep braintrust`
3. Validate JSON files
4. Verify resource IDs exist
5. Check network connectivity to `api.braintrust.dev`

## Integration with Other Skills

- **`braintrust-core`**: Get project IDs before creating resources
- **`braintrust-evaluation`**: Run evaluations on experiments
- **`braintrust-logs`**: Monitor production usage after experimentation

## Reference Documentation

For detailed examples and API specifics:
- Braintrust API: https://www.braintrust.dev/docs/reference/api
- Evaluation Guides: https://www.braintrust.dev/docs/guides/evals
- Python SDK: https://github.com/braintrustdata/braintrust-api-py
