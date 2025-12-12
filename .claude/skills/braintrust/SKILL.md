---
name: braintrust
description: Manage Braintrust AI development platform resources including projects, prompts, datasets, experiments, logs, and evaluations. Use this skill when working with Braintrust API operations, running evaluations, or managing AI experimentation workflows.
---

# Braintrust Management Skill

Comprehensive management of Braintrust platform resources through Python scripts that interact with the Braintrust REST API and CLI.

## When to Use This Skill

Use this skill when the user wants to:
- Create, read, update, or delete Braintrust resources (projects, prompts, datasets, experiments)
- Run Braintrust evaluations locally
- Manage project logs and add feedback
- Interact with the Braintrust platform programmatically
- Set up or manage AI experimentation workflows

## Prerequisites

Before using this skill, ensure the following prerequisites are met:

1. **Braintrust SDK Installation**: Verify the Braintrust Python SDK is installed:
   ```bash
   pip install braintrust
   ```

2. **API Key Configuration**: Check that the `BRAINTRUST_API_KEY` environment variable is set:
   ```bash
   echo $BRAINTRUST_API_KEY
   ```

   If not set, guide the user to:
   - Visit [Braintrust Settings](https://www.braintrust.dev/app/settings)
   - Copy their API key
   - Set it as an environment variable:
     ```bash
     export BRAINTRUST_API_KEY=your_api_key_here
     ```

## Available Tools

All tools are Python scripts located in the `scripts/` directory. Execute them using `python3` with appropriate command-line arguments.

### 1. Project Management (`braintrust_projects.py`)

Manage Braintrust projects with full CRUD operations.

**Commands:**
- `list` - List all projects in the organization
- `get` - Get details of a specific project by ID
- `create` - Create a new project (requires `--name` and `--org-name`)
- `update` - Update project properties (requires project ID)
- `delete` - Delete a project (requires project ID)

**Common Usage:**
```bash
# List all projects
python3 scripts/braintrust_projects.py list

# Create a new project
python3 scripts/braintrust_projects.py create --name "My Project" --org-name "My Org"

# Get project details
python3 scripts/braintrust_projects.py get PROJECT_ID
```

### 2. Prompt Management (`braintrust_prompts.py`)

Manage AI prompts with versioning and template support.

**Commands:**
- `list` - List all prompts (optionally filter by `--project-id`)
- `get` - Get a specific prompt by ID
- `create` - Create a new prompt (requires `--name`, `--project-id`, and optionally `--prompt-data`)
- `update` - Update an existing prompt
- `delete` - Delete a prompt

**Prompt Data Format:**
Prompt data can be passed as a JSON string or plain text. If plain text, it will be wrapped in `{"prompt": "text"}`.

**Common Usage:**
```bash
# Create a simple prompt
python3 scripts/braintrust_prompts.py create \
  --name "QA Assistant" \
  --project-id PROJECT_ID \
  --prompt-data "You are a helpful assistant that answers questions accurately."

# List prompts for a project
python3 scripts/braintrust_prompts.py list --project-id PROJECT_ID
```

### 3. Dataset Management (`braintrust_datasets.py`)

Manage test datasets with CRUD operations and data insertion.

**Commands:**
- `list` - List all datasets
- `get` - Get dataset details by ID
- `create` - Create a new dataset (requires `--name` and `--project-id`)
- `update` - Update dataset properties
- `delete` - Delete a dataset
- `insert` - Insert events into a dataset from a JSON file (requires `--file`)
- `fetch` - Fetch records from a dataset (supports `--limit` and `--cursor`)

**Data Format:**
Dataset events should be JSON arrays with objects containing `input`, `expected`, and optional `metadata`:
```json
[
  {
    "input": "What is the capital of France?",
    "expected": "Paris",
    "metadata": {"category": "geography"}
  }
]
```

**Common Usage:**
```bash
# Create a dataset
python3 scripts/braintrust_datasets.py create \
  --name "Test Dataset" \
  --project-id PROJECT_ID

# Insert data from file
python3 scripts/braintrust_datasets.py insert DATASET_ID --file data.json

# Fetch records
python3 scripts/braintrust_datasets.py fetch DATASET_ID --limit 50
```

### 4. Experiment Management (`braintrust_experiments.py`)

Manage experiments with full lifecycle support including event insertion and summarization.

**Commands:**
- `list` - List all experiments (filter with `--project-id`)
- `get` - Get experiment details by ID
- `create` - Create a new experiment (requires `--name`, `--project-id`, optionally `--dataset-id`)
- `update` - Update experiment properties
- `delete` - Delete an experiment
- `insert` - Insert experiment results from a JSON file
- `summarize` - Get summary statistics for an experiment

**Experiment Events Format:**
```json
[
  {
    "input": "What is the capital of France?",
    "output": "Paris",
    "expected": "Paris",
    "scores": {"accuracy": 1.0},
    "metadata": {"latency_ms": 123}
  }
]
```

**Common Usage:**
```bash
# Create an experiment
python3 scripts/braintrust_experiments.py create \
  --name "Experiment 1" \
  --project-id PROJECT_ID \
  --dataset-id DATASET_ID

# Summarize results
python3 scripts/braintrust_experiments.py summarize EXPERIMENT_ID
```

### 5. Log Management (`braintrust_logs.py`)

Manage project logs with insertion, fetching, and feedback capabilities.

**Commands:**
- `insert` - Insert log events into a project (requires `--project-id` and `--file`)
- `fetch` - Fetch logs from a project (requires `--project-id`, supports `--limit`, `--cursor`, `--filters`)
- `feedback` - Add feedback to a log entry (requires `--project-id`, `--log-id`, `--file`)

**Log Events Format:**
```json
[
  {
    "input": "User query",
    "output": "Assistant response",
    "metadata": {
      "user_id": "123",
      "session_id": "abc"
    }
  }
]
```

**Feedback Format:**
```json
{
  "rating": 5,
  "comment": "Great response!",
  "metadata": {"helpful": true}
}
```

**Common Usage:**
```bash
# Insert logs
python3 scripts/braintrust_logs.py insert --project-id PROJECT_ID --file logs.json

# Fetch recent logs
python3 scripts/braintrust_logs.py fetch --project-id PROJECT_ID --limit 100

# Add feedback
python3 scripts/braintrust_logs.py feedback \
  --project-id PROJECT_ID \
  --log-id LOG_ID \
  --file feedback.json
```

### 6. Evaluation Runner (`braintrust_eval.py`)

Run Braintrust evaluations locally and push code to the Braintrust platform.

**Commands:**
- `eval` - Run evaluations locally (optionally specify file path)
- `push` - Push code to Braintrust (requires file path)

**Eval Options:**
- `--watch` - Auto-rerun on file changes
- `--filter` - Filter test cases (e.g., `"metadata.priority='^P0$'"`)
- `--list` - List evaluators without running
- `--no-send-logs` - Run without sending logs to Braintrust
- `--dev` - Run in dev mode with `--dev-port`

**Push Options:**
- `--if-exists` - Strategy when function exists (`replace`, `skip`, `error`)

**Common Usage:**
```bash
# Run evaluation file
python3 scripts/braintrust_eval.py eval path/to/eval.py

# Run with watch mode
python3 scripts/braintrust_eval.py eval --watch

# Push code to Braintrust
python3 scripts/braintrust_eval.py push my_function.py --if-exists replace
```

## Common Workflows

### Complete Experiment Setup

To set up a complete experiment from scratch:

1. Create a project using `braintrust_projects.py create`
2. Create a dataset using `braintrust_datasets.py create`
3. Insert test data using `braintrust_datasets.py insert`
4. Create an experiment using `braintrust_experiments.py create`
5. Run evaluations using `braintrust_eval.py eval`
6. Summarize results using `braintrust_experiments.py summarize`

### Production Log Monitoring

To monitor and manage production logs:

1. Insert logs using `braintrust_logs.py insert`
2. Fetch recent logs using `braintrust_logs.py fetch`
3. Add feedback using `braintrust_logs.py feedback`

### Prompt Iteration

To iterate on prompts:

1. Create initial prompt using `braintrust_prompts.py create`
2. Test and gather feedback
3. Update prompt using `braintrust_prompts.py update`
4. Retrieve current version using `braintrust_prompts.py get`

## Working with JSON Files

When inserting data (datasets, experiments, logs), always work with JSON files:

1. Create or prepare the JSON file with the appropriate format
2. Validate JSON syntax if needed: `python3 -m json.tool < file.json`
3. Pass the file path using the `--file` argument

## Error Handling

All tools provide detailed error messages for:
- Missing or invalid API key (authentication errors)
- Network connectivity issues
- Invalid data format (JSON validation)
- Resource not found errors
- Missing required parameters

When encountering errors, check:
1. API key is set correctly: `echo $BRAINTRUST_API_KEY`
2. Braintrust SDK is installed: `pip list | grep braintrust`
3. JSON files are valid
4. Resource IDs are correct
5. Network connectivity to `api.braintrust.dev`

## Reference Documentation

For detailed examples and troubleshooting, refer to:
- `references/QUICKSTART.md` - Quick start guide with common examples
- `references/API_DOCS.md` - Complete API documentation reference

For Braintrust platform documentation:
- API Reference: https://www.braintrust.dev/docs/reference/api
- Evaluation Guides: https://www.braintrust.dev/docs/guides/evals
- Python SDK: https://github.com/braintrustdata/braintrust-api-py

## Notes

- All tools output JSON for easy parsing and integration
- Tools use the official Braintrust REST API at `https://api.braintrust.dev`
- Evaluation tool uses the Braintrust CLI (`braintrust eval` and `braintrust push`)
- Resource IDs are returned in API responses for chaining operations
- Always save resource IDs after creating resources for later reference
