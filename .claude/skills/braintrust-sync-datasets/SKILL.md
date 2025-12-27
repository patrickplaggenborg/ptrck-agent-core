---
name: braintrust-sync-datasets
description: Sync multiple Braintrust datasets bidirectionally. Compares entries by input across all datasets, uses timestamps to find the newest version of each entry, and updates older entries in all other datasets.
---

# Sync Braintrust Datasets

## Overview

Bidirectionally sync multiple Braintrust datasets by comparing entries using their `input` field as the matching key. For each unique input present in multiple datasets, the entry with the newest `created` timestamp wins, and all other datasets are updated to match.

## When to Use This Skill

Use this skill when:
- You have edited entries in a subset/filtered dataset and want to push changes back to the original
- You have multiple related datasets that should have consistent `expected` values
- You want to ensure all datasets have the latest corrections after experiment iterations

## Workflow

### Step 1: Identify the Datasets

Get the dataset IDs you want to sync. You can find these in:
- The Braintrust UI URL
- Field-level `braintrust.yaml` files
- Previous experiment logs

### Step 2: Run the Sync Script (Dry Run)

By default, the script shows what would be updated without making changes:

```bash
python3 .claude/skills/braintrust-sync-datasets/scripts/sync_datasets.py \
  717c04f4-7b43-472a-a3b9-68f100f5d755 \
  ae0d7731-33af-4012-8e1c-0820b48776dd
```

### Step 3: Review the Output

The script will show:
- How many entries each dataset has
- How many unique inputs exist across all datasets
- Which entries need updating and in which direction

### Step 4: Apply Changes

If the changes look correct, run with `--apply`:

```bash
python3 .claude/skills/braintrust-sync-datasets/scripts/sync_datasets.py \
  717c04f4-7b43-472a-a3b9-68f100f5d755 \
  ae0d7731-33af-4012-8e1c-0820b48776dd \
  --apply
```

## How It Works

### Input Matching

Entries are matched across datasets by serializing their `input` field to JSON. This means two entries are considered "the same" if they have identical input values.

### Timestamp Comparison

For each input that appears in multiple datasets:
1. Compare the `created` timestamp of each entry
2. The entry with the newest timestamp is the "winner"
3. If the winner has different `expected` values than older entries, queue updates

### Bidirectional Updates

Updates flow in whatever direction is needed:
- If Dataset A has newer edits → update Dataset B
- If Dataset B has newer edits → update Dataset A
- Works with 3+ datasets: newest version updates all others

## Example Usage

**Syncing a "failed" subset back to the original:**

```bash
# Dry run first
python3 .claude/skills/braintrust-sync-datasets/scripts/sync_datasets.py \
  717c04f4-7b43-472a-a3b9-68f100f5d755 \
  ae0d7731-33af-4012-8e1c-0820b48776dd

# Apply changes
python3 .claude/skills/braintrust-sync-datasets/scripts/sync_datasets.py \
  717c04f4-7b43-472a-a3b9-68f100f5d755 \
  ae0d7731-33af-4012-8e1c-0820b48776dd \
  --apply
```

**Syncing 3 datasets:**

```bash
python3 .claude/skills/braintrust-sync-datasets/scripts/sync_datasets.py \
  dataset-id-1 \
  dataset-id-2 \
  dataset-id-3 \
  --apply
```

## Resources

### scripts/sync_datasets.py

Python script that performs the sync. Requires:
- Python 3.7+
- `requests` library
- `BRAINTRUST_API_KEY` environment variable

**Usage:**
```bash
python3 .claude/skills/braintrust-sync-datasets/scripts/sync_datasets.py <dataset_id> <dataset_id> [dataset_id ...] [--apply] [--json]
```

**Arguments:**
- `dataset_ids` - Two or more dataset IDs to sync
- `--apply` - Apply changes (default is dry-run)
- `--json` - Output results as JSON
