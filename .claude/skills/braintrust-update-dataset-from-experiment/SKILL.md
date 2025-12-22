---
name: braintrust-update-dataset-from-experiment
description: Update dataset records from experiment edits. Use this skill when you've corrected 'expected' values in a Braintrust experiment UI and want to sync those corrections back to the source dataset.
---

# Braintrust Update Dataset from Experiment

## Quick Start

```bash
# 1. Preview changes (always do this first!)
python3 skills/braintrust-update-dataset-from-experiment/scripts/update_dataset_from_experiment.py EXPERIMENT_ID --dry-run

# 2. Apply changes
python3 skills/braintrust-update-dataset-from-experiment/scripts/update_dataset_from_experiment.py EXPERIMENT_ID
```

## Overview

Sync corrected `expected` values from a Braintrust experiment back to the source dataset. When you manually edit expected values in the Braintrust experiment UI, this skill detects those edits and updates the corresponding records in the original dataset.

## Complete Workflow

1. **Run an experiment** in Braintrust against a dataset
2. **Review results** in the Braintrust experiment UI
3. **Edit expected values** where they were incorrect
4. **Run this skill with `--dry-run`** to preview what will be updated
5. **Verify** the changes look correct
6. **Run this skill without `--dry-run`** to apply updates
7. **Check the dataset URL** in the output to verify changes in Braintrust

## When to Use This Skill

Use this skill when:
- You've corrected `expected` values in a Braintrust experiment UI
- You want to sync those corrections back to the source dataset
- You need to keep your dataset in sync with experiment corrections

This skill automates the workflow of:
1. Fetching edited records from an experiment (uses `braintrust-fetch-experiment-results` internally)
2. Identifying the source dataset records via `origin.dataset_record_id`
3. Upserting the corrected values back to the dataset

## Prerequisites

1. **Braintrust API key configured**:
   - Set in `.env` file: `BRAINTRUST_API_KEY=your_api_key_here`
   - Or export: `export BRAINTRUST_API_KEY=your_api_key_here`
2. **Experiment ID** from an experiment where you've edited expected values
3. **The fetch skill** must be available at `../braintrust-fetch-experiment-results/`

## Usage

### Preview Changes (Dry Run)

Always preview changes before applying them:

```bash
python3 skills/braintrust-update-dataset-from-experiment/scripts/update_dataset_from_experiment.py EXPERIMENT_ID --dry-run
```

This shows what records would be updated without making any changes.

### Apply Updates

Update the dataset with corrected expected values:

```bash
python3 skills/braintrust-update-dataset-from-experiment/scripts/update_dataset_from_experiment.py EXPERIMENT_ID
```

### Verbose Output

Get detailed progress information:

```bash
python3 skills/braintrust-update-dataset-from-experiment/scripts/update_dataset_from_experiment.py EXPERIMENT_ID --verbose
```

## How It Works

1. **Fetch edited records**: Uses the `braintrust-fetch-experiment-results` skill with `--edited-only` to get records where the `expected` field was manually edited
2. **Extract dataset linkage**: Each experiment record has an `origin` field with `dataset_id` and `dataset_record_id`
3. **Prepare upsert payload**: Creates dataset events using the original record ID (triggers upsert behavior)
4. **Update dataset**: Calls the Braintrust dataset insert API, which overwrites existing records with the same ID

## Output Format

### Dry Run Output

```json
{
  "dry_run": true,
  "dataset_id": "ae0d7731-33af-4012-8e1c-0820b48776dd",
  "records_to_update": 7,
  "events": [
    {
      "id": "a359ecb8-0a1e-46e4-860a-bd0eb6e2b3d6",
      "input": "...",
      "expected": { ... }
    }
  ],
  "dataset_url": "https://www.braintrust.dev/app/ORG/p/PROJECT/datasets/DATASET_NAME"
}
```

### Update Output

```json
{
  "row_ids": ["a359ecb8-...", "a91967f6-...", ...],
  "updated": 7,
  "dataset_id": "ae0d7731-33af-4012-8e1c-0820b48776dd",
  "dataset_name": "departureAirports (100)",
  "dataset_url": "https://www.braintrust.dev/app/ORG/p/PROJECT/datasets/DATASET_NAME"
}
```

The `dataset_url` field provides a direct link to verify the changes in Braintrust.

## Integration with Other Skills

This skill uses:
- **`braintrust-fetch-experiment-results`** - Fetches edited records with `--edited-only` flag

## Error Handling

The script will exit with an error if:
- `BRAINTRUST_API_KEY` is not set
- Experiment ID is invalid or doesn't exist
- No edited records found in the experiment
- Records don't have valid dataset origin info
- Network connectivity issues to `api.braintrust.dev`

## Safety

- **Always use `--dry-run` first** to preview what will be updated
- The script uses **upsert** behavior - existing records with the same ID are overwritten
- Only the `input`, `expected`, and `metadata` fields are updated
- Other dataset record fields remain unchanged
