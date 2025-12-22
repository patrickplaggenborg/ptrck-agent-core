---
name: braintrust-fetch-experiment-results
description: Fetch experiment results from Braintrust API. Use this skill when retrieving datapoints (inputs, outputs, expected values, scores, metadata) from a completed Braintrust experiment. Returns a clean flat dataset structure optimized for analysis.
---

# Braintrust Fetch Experiment Results

## Overview

Retrieve all datapoints from a Braintrust experiment via the API and transform them into a clean flat dataset structure. Returns experiment results with input, output, expected, metadata, and scores in an easy-to-analyze format.

## When to Use This Skill

Use this skill when:
- Fetching results from a completed Braintrust experiment
- Retrieving experiment data for local storage or analysis
- Pulling experiment outputs to compare against expected values
- Exporting experiment results to JSON files

This skill is commonly used as part of experiment analysis workflows where results need to be pulled from Braintrust and stored locally.

## Prerequisites

1. **Braintrust API key configured**:
   - Set in `.env` file: `BRAINTRUST_API_KEY=your_api_key_here`
   - Or export: `export BRAINTRUST_API_KEY=your_api_key_here`
2. **Valid experiment ID** from a completed experiment

## Usage

### Basic Usage

Fetch all results from an experiment:

```bash
python3 .claude/skills/braintrust-fetch-experiment-results/scripts/fetch_experiment_results.py EXPERIMENT_ID
```

### Pagination Control

Fetch with custom page size (default is 1000):

```bash
python3 .claude/skills/braintrust-fetch-experiment-results/scripts/fetch_experiment_results.py EXPERIMENT_ID --limit 500
```

### Limit Total Results

Fetch only first N results:

```bash
python3 .claude/skills/braintrust-fetch-experiment-results/scripts/fetch_experiment_results.py EXPERIMENT_ID --max-results 100
```

### Save to File

```bash
python3 .claude/skills/braintrust-fetch-experiment-results/scripts/fetch_experiment_results.py EXPERIMENT_ID > results.json
```

## Output Format

Returns a JSON array of flat datapoints optimized for analysis:

```json
[
  {
    "root_span_id": "74a267ee-63b3-402f-8636-c3f6285d2f66",
    "input": "What is the capital of France?",
    "output": {
      "answer": "Paris"
    },
    "expected": {
      "answer": "Paris"
    },
    "metadata": {
      "keysChecked": ["answer"]
    },
    "scores": {
      "Exact Match": 1.0,
      "Accuracy": 1.0
    }
  },
  {
    "root_span_id": "a627267a-78e7-4837-b839-302567983358",
    "input": "What is 2+2?",
    "output": {
      "answer": "4"
    },
    "expected": {
      "answer": "4"
    },
    "metadata": {
      "keysChecked": ["answer"]
    },
    "scores": {
      "Exact Match": 1.0,
      "Accuracy": 1.0
    }
  }
]
```

Each datapoint includes:
- `root_span_id` - Unique identifier for the test case (useful for referencing in Braintrust UI)
- `input` - The input text that was tested
- `output` - The model's output (structured object)
- `expected` - The expected/correct output (structured object)
- `metadata` - Additional metadata about the test case
- `scores` - Score metrics from all scorers that were applied

Note: The script filters to only include root-level test cases (is_root=true), excluding individual scorer execution records.

## Integration with Other Workflows

This skill is commonly used in conjunction with:
- **`run-field-experiment`** - After launching an experiment, fetch its results
- **`braintrust-experimentation`** - For managing experiments before fetching results
- Local analysis scripts - Process fetched results for scoring and analysis

## Error Handling

The script will exit with an error if:
- `BRAINTRUST_API_KEY` is not set
- Experiment ID is invalid or doesn't exist
- Network connectivity issues to `api.braintrust.dev`
- API rate limits are exceeded

Check errors by examining stderr output.
