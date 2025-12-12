# Braintrust Skill Quick Start

This guide will help you get started with the Braintrust skill in minutes.

## Setup (One-time)

### 1. Install Braintrust
```bash
pip install braintrust
```

### 2. Get Your API Key
1. Go to [Braintrust Settings](https://www.braintrust.dev/app/settings)
2. Copy your API key
3. Set it as an environment variable:

```bash
export BRAINTRUST_API_KEY=your_api_key_here
```

To make it permanent, add to your `~/.zshrc` or `~/.bashrc`:
```bash
echo 'export BRAINTRUST_API_KEY=your_api_key_here' >> ~/.zshrc
```

## Quick Examples

### List Your Projects
```bash
cd .claude/skills/braintrust/tools
python3 braintrust_projects.py list
```

### Create a New Project
```bash
python3 braintrust_projects.py create --name "My First Project"
```

### Create a Dataset
First, create a JSON file with your data (`dataset.json`):
```json
[
  {
    "input": "What is the capital of France?",
    "expected": "Paris"
  },
  {
    "input": "What is 2+2?",
    "expected": "4"
  }
]
```

Then create the dataset and insert data:
```bash
# Create dataset (use PROJECT_ID from previous step)
python3 braintrust_datasets.py create --name "Test Dataset" --project-id PROJECT_ID

# Insert data (use DATASET_ID from output)
python3 braintrust_datasets.py insert DATASET_ID --file dataset.json

# Fetch data to verify
python3 braintrust_datasets.py fetch DATASET_ID
```

### Create a Prompt
```bash
python3 braintrust_prompts.py create \
  --name "QA Assistant" \
  --project-id PROJECT_ID \
  --prompt-data "You are a helpful assistant that answers questions accurately and concisely."
```

### Run an Evaluation

Create an evaluation file (`eval_example.py`):
```python
from braintrust import Eval

def is_equal(expected, output):
    return expected == output

Eval(
    "Simple Math Eval",
    data=lambda: [
        {"input": "What is 2+2?", "expected": "4"},
        {"input": "What is 3+3?", "expected": "6"},
    ],
    task=lambda input: "4" if "2+2" in input else "6",
    scores=[is_equal],
)
```

Run it:
```bash
python3 braintrust_eval.py eval eval_example.py
```

### View Logs
```bash
python3 braintrust_logs.py fetch --project-id PROJECT_ID --limit 10
```

## Common Workflows

### 1. Create a Complete Experiment
```bash
# 1. Create project
python3 braintrust_projects.py create --name "My Experiment"

# 2. Create dataset
python3 braintrust_datasets.py create --name "Test Data" --project-id PROJECT_ID

# 3. Insert test data
python3 braintrust_datasets.py insert DATASET_ID --file test_data.json

# 4. Create experiment
python3 braintrust_experiments.py create \
  --name "Experiment 1" \
  --project-id PROJECT_ID \
  --dataset-id DATASET_ID

# 5. Run eval and log results
python3 braintrust_eval.py eval my_eval.py

# 6. Summarize results
python3 braintrust_experiments.py summarize EXPERIMENT_ID
```

### 2. Monitor Production Logs
```bash
# Insert production logs
python3 braintrust_logs.py insert --project-id PROJECT_ID --file prod_logs.json

# Fetch recent logs
python3 braintrust_logs.py fetch --project-id PROJECT_ID --limit 50

# Add feedback to a log
python3 braintrust_logs.py feedback \
  --project-id PROJECT_ID \
  --log-id LOG_ID \
  --file feedback.json
```

### 3. Iterate on Prompts
```bash
# Create initial prompt
python3 braintrust_prompts.py create \
  --name "Assistant v1" \
  --project-id PROJECT_ID \
  --prompt-data "You are a helpful assistant."

# Update prompt
python3 braintrust_prompts.py update PROMPT_ID \
  --prompt-data "You are a helpful and friendly assistant that provides detailed answers."

# Get current version
python3 braintrust_prompts.py get PROMPT_ID
```

## Tips

1. **Save IDs**: After creating resources, save their IDs for later use
2. **Use JSON files**: Keep your data in JSON files for easy version control
3. **Watch mode**: Use `--watch` with eval to auto-rerun on file changes
4. **Pagination**: Use `--cursor` to fetch more results in list operations
5. **Filters**: Use `--filter` with eval to run specific test cases

## Troubleshooting

### "BRAINTRUST_API_KEY environment variable not set"
```bash
export BRAINTRUST_API_KEY=your_key_here
```

### "braintrust CLI not found"
```bash
pip install braintrust
```

### "Authentication failed"
Check that your API key is valid at [Braintrust Settings](https://www.braintrust.dev/app/settings)

### JSON parse errors
Validate your JSON files:
```bash
python3 -m json.tool < your_file.json
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check the [Braintrust API Docs](https://www.braintrust.dev/docs/reference/api)
- Explore [example evaluations](https://www.braintrust.dev/docs/guides/evals)
- Learn about [Braintrust Functions](https://www.braintrust.dev/docs/guides/functions)

## Getting Help

- Braintrust Documentation: https://www.braintrust.dev/docs
- API Reference: https://www.braintrust.dev/docs/reference/api
- GitHub: https://github.com/braintrustdata/braintrust-sdk
- Support: https://support.usebraintrust.com/hc/en-us
