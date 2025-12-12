# Braintrust CLI Skill

A comprehensive Claude Code skill for managing Braintrust resources including prompts, datasets, experiments, logs, and projects through the Braintrust REST API and CLI.

## Prerequisites

1. **Install Braintrust SDK**:
   ```bash
   pip install braintrust
   ```

2. **Set up API Key**:
   ```bash
   export BRAINTRUST_API_KEY=your_api_key_here
   ```

   Get your API key from [Braintrust Settings](https://www.braintrust.dev/app/settings).

## Available Tools

### 1. braintrust_prompts
Manage Braintrust prompts with full CRUD operations.

**Commands:**
- `list` - List all prompts
- `get` - Get a specific prompt by ID
- `create` - Create a new prompt
- `update` - Update an existing prompt
- `delete` - Delete a prompt

**Examples:**
```bash
# List all prompts
python3 braintrust_prompts.py list

# List prompts for a specific project
python3 braintrust_prompts.py list --project-id PROJECT_ID

# Get a specific prompt
python3 braintrust_prompts.py get PROMPT_ID

# Create a new prompt
python3 braintrust_prompts.py create --name "My Prompt" --project-id PROJECT_ID --prompt-data "You are a helpful assistant"

# Update a prompt
python3 braintrust_prompts.py update PROMPT_ID --name "Updated Prompt" --description "New description"

# Delete a prompt
python3 braintrust_prompts.py delete PROMPT_ID
```

### 2. braintrust_datasets
Manage Braintrust datasets with CRUD operations and data insertion.

**Commands:**
- `list` - List all datasets
- `get` - Get a specific dataset by ID
- `create` - Create a new dataset
- `update` - Update an existing dataset
- `delete` - Delete a dataset
- `insert` - Insert events into a dataset
- `fetch` - Fetch records from a dataset

**Examples:**
```bash
# List all datasets
python3 braintrust_datasets.py list

# Create a new dataset
python3 braintrust_datasets.py create --name "My Dataset" --project-id PROJECT_ID --description "Test dataset"

# Insert events from a JSON file
python3 braintrust_datasets.py insert DATASET_ID --file events.json

# Fetch records from a dataset
python3 braintrust_datasets.py fetch DATASET_ID --limit 50
```

### 3. braintrust_experiments
Manage Braintrust experiments with full lifecycle support.

**Commands:**
- `list` - List all experiments
- `get` - Get a specific experiment by ID
- `create` - Create a new experiment
- `update` - Update an existing experiment
- `delete` - Delete an experiment
- `insert` - Insert events into an experiment
- `summarize` - Summarize experiment results

**Examples:**
```bash
# List all experiments
python3 braintrust_experiments.py list --project-id PROJECT_ID

# Create a new experiment
python3 braintrust_experiments.py create --name "My Experiment" --project-id PROJECT_ID --dataset-id DATASET_ID

# Insert events into an experiment
python3 braintrust_experiments.py insert EXPERIMENT_ID --file results.json

# Summarize experiment results
python3 braintrust_experiments.py summarize EXPERIMENT_ID
```

### 4. braintrust_logs
Manage project logs with insertion, fetching, and feedback operations.

**Commands:**
- `insert` - Insert log events into a project
- `fetch` - Fetch logs from a project
- `feedback` - Add feedback to a log entry

**Examples:**
```bash
# Insert logs
python3 braintrust_logs.py insert --project-id PROJECT_ID --file logs.json

# Fetch logs
python3 braintrust_logs.py fetch --project-id PROJECT_ID --limit 100

# Fetch logs with filters
python3 braintrust_logs.py fetch --project-id PROJECT_ID --filters '{"level": "error"}'

# Add feedback to a log
python3 braintrust_logs.py feedback --project-id PROJECT_ID --log-id LOG_ID --file feedback.json
```

### 5. braintrust_projects
Manage Braintrust projects.

**Commands:**
- `list` - List all projects
- `get` - Get a specific project by ID
- `create` - Create a new project
- `update` - Update an existing project
- `delete` - Delete a project

**Examples:**
```bash
# List all projects
python3 braintrust_projects.py list

# Create a new project
python3 braintrust_projects.py create --name "My Project" --org-name "My Org"

# Update a project
python3 braintrust_projects.py update PROJECT_ID --name "Updated Project"
```

### 6. braintrust_eval
Run Braintrust evaluations locally and push code to Braintrust.

**Commands:**
- `eval` - Run evaluations locally
- `push` - Push code to Braintrust

**Examples:**
```bash
# Run evaluations in current directory
python3 braintrust_eval.py eval

# Run specific evaluation file
python3 braintrust_eval.py eval path/to/eval.py

# Run with watch mode
python3 braintrust_eval.py eval --watch

# Run with filters
python3 braintrust_eval.py eval --filter "metadata.priority='^P0$'"

# List evaluators without running
python3 braintrust_eval.py eval --list

# Run without sending logs to Braintrust
python3 braintrust_eval.py eval --no-send-logs

# Run in dev mode
python3 braintrust_eval.py eval --dev --dev-port 8300

# Push code to Braintrust
python3 braintrust_eval.py push my_function.py

# Push with replace existing
python3 braintrust_eval.py push my_function.py --if-exists replace
```

## Data Format Examples

### Prompt Data
```json
{
  "prompt": "You are a helpful assistant that answers questions about {{topic}}.",
  "model": "gpt-4",
  "temperature": 0.7
}
```

### Dataset Events
```json
[
  {
    "input": "What is the capital of France?",
    "expected": "Paris",
    "metadata": {
      "category": "geography"
    }
  },
  {
    "input": "What is 2+2?",
    "expected": "4",
    "metadata": {
      "category": "math"
    }
  }
]
```

### Experiment Events
```json
[
  {
    "input": "What is the capital of France?",
    "output": "Paris",
    "expected": "Paris",
    "scores": {
      "accuracy": 1.0
    },
    "metadata": {
      "latency_ms": 123
    }
  }
]
```

### Log Events
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

### Feedback Data
```json
{
  "rating": 5,
  "comment": "Great response!",
  "metadata": {
    "helpful": true
  }
}
```

## Environment Variables

- `BRAINTRUST_API_KEY` (required) - Your Braintrust API key
- `BRAINTRUST_ORG_NAME` (optional) - Default organization name

## Error Handling

All tools provide detailed error messages:
- Authentication errors (missing or invalid API key)
- Network errors (connection issues)
- Validation errors (invalid data format)
- Resource not found errors

## API Documentation

For more details on the Braintrust API:
- [API Reference](https://www.braintrust.dev/docs/reference/api)
- [API Walkthrough](https://www.braintrust.dev/docs/guides/api)
- [Python SDK](https://github.com/braintrustdata/braintrust-api-py)

## Notes

- All tools output JSON for easy parsing and integration
- Tools use the official Braintrust REST API at `https://api.braintrust.dev`
- Evaluation tool uses the Braintrust CLI (`braintrust eval` and `braintrust push`)
- All data files should be valid JSON
- IDs are returned in API responses for chaining operations

## Support

For issues with the Braintrust skill, check:
1. API key is set correctly
2. Braintrust SDK is installed
3. Network connectivity to api.braintrust.dev
4. Data files are valid JSON
5. Resource IDs are correct

For Braintrust platform issues, visit [Braintrust Support](https://support.usebraintrust.com/hc/en-us)
