---
name: braintrust-launch-experiment
description: Launch Braintrust experiments on the platform by triggering the /v1/eval API. Takes prompt ID, dataset ID, and scorer to start an experiment. Returns experiment ID immediately without waiting for completion. Use this to trigger experiments as part of evaluation workflows.
---

# Braintrust Launch Experiment

Launch experiments on the Braintrust platform using the /v1/eval API endpoint. This skill triggers experiments to run server-side and returns immediately with the experiment ID.

## When to Use This Skill

Use this skill when the user wants to:
- Launch a new experiment on Braintrust platform
- Trigger a baseline evaluation for a field
- Start an experiment without waiting for completion
- Automate the "Create Experiment" workflow from the UI
- Kick off experiments as part of an iteration/finetuning cycle

**Important**: This skill only **launches** experiments - it does not wait for completion or fetch detailed results.

## What This Skill Does

✅ **Does:**
- Triggers experiment execution on Braintrust platform
- Takes prompt ID, dataset ID, experiment name, scorer
- Returns experiment ID immediately
- Shows initial status and links

❌ **Does Not:**
- Wait for experiment completion
- Fetch detailed results
- Analyze results or provide recommendations
- Display per-record scores

For complete results and analysis, use companion skills after the experiment completes.

## Prerequisites

Before using this skill:

1. **Python requests library**: `pip install requests`
2. **API key configured**:
   - Set in `.env` file: `BRAINTRUST_API_KEY=your_api_key_here` (automatically loaded)
   - Or export manually: `export BRAINTRUST_API_KEY=your_api_key_here`
3. **Resources exist in Braintrust**:
   - Prompt ID (from `braintrust-experimentation` skill)
   - Dataset ID (from `braintrust-experimentation` skill)
   - Project ID (from `braintrust-core` skill)

**Note**: The script automatically loads environment variables from a `.env` file in the current directory if it exists.

## Available Tools

The main tool is a Python script in the `scripts/` directory that launches experiments via API.

### Launch Experiment (`launch_experiment.py`)

Launches a Braintrust evaluation on the platform using the /v1/eval API endpoint.

**Basic Usage:**
```bash
# Launch experiment with prompt and dataset
python3 .claude/skills/braintrust-launch-experiment/scripts/launch_experiment.py \
  --prompt-id PROMPT_ID \
  --dataset-id DATASET_ID \
  --experiment-name "My Experiment" \
  --project-id PROJECT_ID
```

**Available Options:**

- `--prompt-id` (required): Braintrust prompt ID to use
- `--dataset-id` (required): Braintrust dataset ID to use
- `--experiment-name` (required): Name for the experiment
- `--project-id` (required): Braintrust project ID
- `--scorer`: Scorer to use (default: `Factuality`)
  - See "Available Scorers" section below for options
- `--field-name`: Optional field name for future custom scoring
- `--json`: Output raw JSON response (for debugging)

**Examples:**

```bash
# Launch baseline experiment with Factuality scorer
python3 .claude/skills/braintrust-launch-experiment/scripts/launch_experiment.py \
  --prompt-id d3599976-c611-48e4-9b57-0763c6e52fb5 \
  --dataset-id 913d0e08-fdb3-4154-96db-23eb90d3d032 \
  --experiment-name "Duration Baseline" \
  --project-id 5956ce58-88ac-42f7-88ce-c2be352de28c

# Launch with different scorer
python3 .claude/skills/braintrust-launch-experiment/scripts/launch_experiment.py \
  --prompt-id d3599976-c611-48e4-9b57-0763c6e52fb5 \
  --dataset-id 913d0e08-fdb3-4154-96db-23eb90d3d032 \
  --experiment-name "Duration Test - ExactMatch" \
  --project-id 5956ce58-88ac-42f7-88ce-c2be352de28c \
  --scorer ExactMatch

# Get raw JSON response (for debugging)
python3 .claude/skills/braintrust-launch-experiment/scripts/launch_experiment.py \
  --prompt-id PROMPT_ID \
  --dataset-id DATASET_ID \
  --experiment-name "Test" \
  --project-id PROJECT_ID \
  --json
```

## How It Works

The script:
1. Takes prompt ID, dataset ID, experiment name, and scorer
2. Calls Braintrust `/v1/eval` API endpoint
3. Braintrust platform starts running the experiment server-side
4. Returns immediately with experiment ID and status
5. Experiment continues running on platform (typically 1-5 minutes for 100 records)

## Available Scorers

The skill uses Braintrust's built-in autoevals scorers. Common options:

- **Factuality**: Measures factual accuracy (default, good for most cases)
- **ExactMatch**: Exact string matching
- **Levenshtein**: Edit distance similarity
- **JsonDiff**: JSON structure comparison
- **ClosedQA**: For question answering tasks
- **Summary**: For summarization quality

See [Braintrust AutoEvals](https://github.com/braintrustdata/autoevals) for full list.

## Common Workflows

### Launching a Baseline Experiment

When starting to finetune a field:

1. Have prompt ID and dataset ID ready (from braintrust.yaml or Braintrust UI)
2. Launch baseline experiment:
   ```bash
   python3 .claude/skills/braintrust-launch-experiment/scripts/launch_experiment.py \
     --prompt-id YOUR_PROMPT_ID \
     --dataset-id YOUR_DATASET_ID \
     --experiment-name "Baseline Run 1" \
     --project-id YOUR_PROJECT_ID \
     --scorer Factuality
   ```
3. Script returns experiment ID immediately
4. **Wait 1-5 minutes** for experiment to complete on platform
5. Use `braintrust-fetch-experiment` skill to get results (when ready)
6. Use `braintrust-analyze-experiment` skill to identify patterns (when ready)

### Iterative Finetuning Workflow

1. Launch baseline experiment
2. Wait for completion
3. Fetch and analyze results
4. Update prompt description in Braintrust
5. Launch new experiment with updated prompt
6. Compare results between experiments
7. Repeat until satisfied

### Experiment Tracking

After launching, save the experiment ID to track it:
- Add to `braintrust.yaml` under `experiments` list
- Use ID to fetch results later
- Reference ID when comparing experiments

## Output Format

The script outputs a simple confirmation with experiment ID:

```
Experiment launched successfully on Braintrust platform!

Experiment ID: exp-abc123-def456
Experiment Name: Duration Baseline - Run 1
Project ID: 5956ce58-88ac-42f7-88ce-c2be352de28c
Scorer: Factuality

Status: Running on Braintrust platform
Estimated completion: 1-5 minutes for 100 records

Next steps:
  1. Wait for experiment to complete
  2. Use braintrust-fetch-experiment skill to get detailed results
  3. Use braintrust-analyze-experiment skill to identify patterns

Initial metrics (may be incomplete):
  - Score: 0.5960 (Factuality)
  - Test cases: 100
```

Use `--json` flag for raw API response (for debugging).

## Error Handling

The tool provides detailed errors for:
- Missing or invalid API key
- Prompt/dataset/project not found
- Invalid scorer configuration
- Network connectivity issues
- API execution errors

When errors occur:
1. Verify API key: `echo $BRAINTRUST_API_KEY`
2. Check requests library installed: `pip list | grep requests`
3. Verify resource IDs exist (use `braintrust-experimentation` skill)
4. Check network connectivity to `api.braintrust.dev`

## Integration with Other Skills

**Upstream Skills** (use before this):
- **`braintrust-core`**: Get project IDs
- **`braintrust-experimentation`**: Create/manage prompts and datasets

**Downstream Skills** (use after this):
- **`braintrust-fetch-experiment`**: Retrieve complete results when experiment finishes
- **`braintrust-analyze-experiment`**: Analyze results and identify improvement patterns
- **Field finetuning workflows**: Part of the complete iteration cycle

## Modular Workflow

```
1. braintrust-launch-experiment (this skill)
   └─> Returns: experiment_id

2. [Wait 1-5 minutes]

3. braintrust-fetch-experiment
   └─> Input: experiment_id
   └─> Returns: complete results with scores, URLs, metrics

4. braintrust-analyze-experiment
   └─> Input: experiment results
   └─> Returns: patterns, recommendations, suggested improvements
```

## Reference Documentation

For detailed API usage:
- [Braintrust /v1/eval API](https://www.braintrust.dev/docs/api-reference/evals/launch-an-eval)
- [Braintrust Eval Guide](https://www.braintrust.dev/docs/guides/evals)
- [AutoEvals Library](https://github.com/braintrustdata/autoevals)
- [Scorers](https://www.braintrust.dev/docs/guides/functions/scorers)
