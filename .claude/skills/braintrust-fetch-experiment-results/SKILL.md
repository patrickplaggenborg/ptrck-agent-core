---
name: braintrust-fetch-experiment-results
description: Fetch experiment results from Braintrust API. Use this skill when retrieving datapoints (inputs, outputs, expected values, scores, metadata) from a completed Braintrust experiment. Returns a clean flat dataset structure optimized for analysis.
---

# Braintrust Fetch Experiment Results

> **Note:** Always use this skill to fetch experiment data instead of making raw API calls. This script handles pagination, transforms raw events into clean records, and extracts dataset linkage information.

## Overview

Retrieve all datapoints from a Braintrust experiment via the API and transform them into a clean flat dataset structure. Returns experiment results with input, output, expected, metadata, scores, and origin (dataset linkage) in an easy-to-analyze format.

## When to Use This Skill

Use this skill when:
- Fetching results from a completed Braintrust experiment
- Retrieving experiment data for local storage or analysis
- Pulling experiment outputs to compare against expected values
- Exporting experiment results to JSON files
- Tracing experiment records back to their source dataset (for updating expected values)

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

Fetch only first N clean records:

```bash
python3 .claude/skills/braintrust-fetch-experiment-results/scripts/fetch_experiment_results.py EXPERIMENT_ID --max-results 10
```

Note: `--max-results` limits the number of clean experiment records returned, not raw API events. The script fetches all raw events and then returns up to N transformed records.

### Fetch Only Edited Records

Fetch only records where the `expected` field was manually edited in the Braintrust UI:

```bash
python3 .claude/skills/braintrust-fetch-experiment-results/scripts/fetch_experiment_results.py EXPERIMENT_ID --edited-only
```

This is useful for syncing experiment corrections back to the source dataset. Records returned with `--edited-only` will include `"edited": true`.

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
    },
    "origin": {
      "dataset_id": "ae0d7731-33af-4012-8e1c-0820b48776dd",
      "dataset_record_id": "af5e76af-e321-4a8c-bf6a-f1c109195051"
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
- `origin` - Dataset linkage info (if experiment was run against a dataset):
  - `dataset_id` - The source dataset ID
  - `dataset_record_id` - The specific record ID in the dataset (use this to update the record)

Note: The script filters to only include root-level test cases (is_root=true), excluding individual scorer execution records. The `origin` field is `null` if the experiment was not run against a dataset.

## Integration with Other Workflows

This skill is commonly used in conjunction with:
- **`run-field-experiment`** - After launching an experiment, fetch its results
- **`braintrust-experimentation`** - For managing experiments before fetching results
- **Dataset updates** - Use `origin.dataset_record_id` to update records in the source dataset via upsert
- Local analysis scripts - Process fetched results for scoring and analysis

### Updating Dataset Records from Experiment Corrections

When you correct an `expected` value in Braintrust's experiment UI, you can trace it back to the source dataset:

1. Fetch edited records using `--edited-only` flag
2. Each record includes `origin.dataset_id` and `origin.dataset_record_id`
3. Use the **`braintrust-update-dataset-from-experiment`** skill to automatically sync edits back to the dataset

Or manually:
1. Fetch experiment results using this skill with `--edited-only`
2. Use `origin.dataset_record_id` as the `id` field when upserting to the dataset
3. Call the dataset insert API (upsert behavior overwrites existing records with same ID)

## Error Handling

The script will exit with an error if:
- `BRAINTRUST_API_KEY` is not set
- Experiment ID is invalid or doesn't exist
- Network connectivity issues to `api.braintrust.dev`
- API rate limits are exceeded

Check errors by examining stderr output.
