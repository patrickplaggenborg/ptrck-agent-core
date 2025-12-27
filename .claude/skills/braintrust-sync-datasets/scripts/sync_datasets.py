#!/usr/bin/env python3
"""
Sync multiple Braintrust datasets bidirectionally.

Compares entries by input across all datasets, uses timestamps to find
the newest version of each entry, and updates older entries in all other datasets.
"""

import argparse
import json
import os
import sys
from typing import Any

import requests


def get_api_key() -> str:
    """Get Braintrust API key from environment."""
    api_key = os.environ.get("BRAINTRUST_API_KEY")
    if not api_key:
        print("Error: BRAINTRUST_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    return api_key


def fetch_dataset_metadata(dataset_id: str, headers: dict) -> dict:
    """Fetch dataset metadata (name, etc.)."""
    url = f"https://api.braintrustdata.com/v1/dataset/{dataset_id}"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Error fetching metadata for {dataset_id}: {resp.status_code}", file=sys.stderr)
        return {"id": dataset_id, "name": dataset_id}
    return resp.json()


def fetch_dataset_entries(dataset_id: str, headers: dict) -> list[dict]:
    """Fetch all entries from a dataset."""
    url = f"https://api.braintrustdata.com/v1/dataset/{dataset_id}/fetch"
    resp = requests.post(url, headers=headers, json={})
    if resp.status_code != 200:
        print(f"Error fetching entries for {dataset_id}: {resp.status_code}", file=sys.stderr)
        return []
    return resp.json().get("events", [])


def update_dataset_entry(dataset_id: str, entry_id: str, input_val: Any, expected: Any, headers: dict) -> bool:
    """Update an entry in a dataset."""
    url = f"https://api.braintrustdata.com/v1/dataset/{dataset_id}/insert"
    payload = {
        "events": [{
            "id": entry_id,
            "input": input_val,
            "expected": expected
        }]
    }
    resp = requests.post(url, headers=headers, json=payload)
    return resp.status_code == 200


def serialize_input(input_val: Any) -> str:
    """Serialize input to a consistent string key."""
    return json.dumps(input_val, sort_keys=True)


def truncate_input(input_val: Any, max_len: int = 60) -> str:
    """Truncate input for display."""
    if isinstance(input_val, str):
        return input_val[:max_len] + ("..." if len(input_val) > max_len else "")
    s = str(input_val)
    return s[:max_len] + ("..." if len(s) > max_len else "")


def main():
    parser = argparse.ArgumentParser(
        description="Sync multiple Braintrust datasets bidirectionally"
    )
    parser.add_argument(
        "dataset_ids",
        nargs="+",
        help="Two or more dataset IDs to sync"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (default is dry-run)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    args = parser.parse_args()

    if len(args.dataset_ids) < 2:
        print("Error: At least 2 dataset IDs required", file=sys.stderr)
        sys.exit(1)

    api_key = get_api_key()
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # Fetch all datasets
    datasets = {}
    for ds_id in args.dataset_ids:
        meta = fetch_dataset_metadata(ds_id, headers)
        entries = fetch_dataset_entries(ds_id, headers)
        datasets[ds_id] = {
            "name": meta.get("name", ds_id),
            "entries": entries,
            "entry_map": {}  # input_key -> entry
        }
        # Build entry map - keep only the newest entry for each input
        for entry in entries:
            input_key = serialize_input(entry.get("input"))
            existing = datasets[ds_id]["entry_map"].get(input_key)
            if existing is None or entry.get("created", "") > existing.get("created", ""):
                datasets[ds_id]["entry_map"][input_key] = entry

    if not args.json:
        print(f"Syncing {len(datasets)} datasets...")
        for ds_id, ds in datasets.items():
            print(f'  {ds["name"]}: {len(ds["entries"])} entries')
        print()

    # Build global map: input_key -> [(dataset_id, entry), ...]
    global_map: dict[str, list[tuple[str, dict]]] = {}
    for ds_id, ds in datasets.items():
        for input_key, entry in ds["entry_map"].items():
            if input_key not in global_map:
                global_map[input_key] = []
            global_map[input_key].append((ds_id, entry))

    # Find inputs present in multiple datasets
    multi_dataset_inputs = {k: v for k, v in global_map.items() if len(v) > 1}

    # Determine updates needed
    updates_by_dataset: dict[str, list[dict]] = {ds_id: [] for ds_id in datasets}
    inputs_with_diffs = 0

    for input_key, entries in multi_dataset_inputs.items():
        # Find the newest entry
        newest_ds_id = None
        newest_entry = None
        newest_created = ""

        for ds_id, entry in entries:
            created = entry.get("created", "")
            if created > newest_created:
                newest_created = created
                newest_ds_id = ds_id
                newest_entry = entry

        # Check if any other dataset has different expected values
        newest_expected = newest_entry.get("expected")
        has_diff = False

        for ds_id, entry in entries:
            if ds_id == newest_ds_id:
                continue

            entry_expected = entry.get("expected")
            # Normalize None to {} for comparison
            norm_newest = newest_expected if newest_expected is not None else {}
            norm_entry = entry_expected if entry_expected is not None else {}

            if norm_newest != norm_entry:
                has_diff = True
                updates_by_dataset[ds_id].append({
                    "entry_id": entry.get("id"),
                    "input": json.loads(input_key),
                    "old_expected": entry_expected,
                    "new_expected": newest_expected,
                    "source_dataset": newest_ds_id
                })

        if has_diff:
            inputs_with_diffs += 1

    # Output results
    if args.json:
        result = {
            "datasets": {ds_id: {"name": ds["name"], "entry_count": len(ds["entries"])} for ds_id, ds in datasets.items()},
            "unique_inputs": len(global_map),
            "inputs_in_multiple": len(multi_dataset_inputs),
            "inputs_with_diffs": inputs_with_diffs,
            "updates": updates_by_dataset,
            "applied": args.apply
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"Unique inputs across all datasets: {len(global_map)}")
        print(f"Inputs present in multiple datasets: {len(multi_dataset_inputs)}")
        print(f"Inputs with differing expected values: {inputs_with_diffs}")
        print()

        total_updates = sum(len(u) for u in updates_by_dataset.values())
        if total_updates == 0:
            print("All datasets are in sync!")
        else:
            print("Updates needed:")
            for ds_id, updates in updates_by_dataset.items():
                ds_name = datasets[ds_id]["name"]
                if updates:
                    print(f'  → "{ds_name}": {len(updates)} update(s)')
                    for i, upd in enumerate(updates[:5], 1):
                        inp_display = truncate_input(upd["input"])
                        print(f'    {i}. "{inp_display}"')
                        print(f'       old: {upd["old_expected"]}')
                        print(f'       new: {upd["new_expected"]}')
                    if len(updates) > 5:
                        print(f"    ... and {len(updates) - 5} more")
                else:
                    print(f'  → "{ds_name}": already up to date')
            print()

    # Apply updates if requested
    if args.apply and total_updates > 0:
        if not args.json:
            print("Applying updates...")

        success_count = 0
        fail_count = 0

        for ds_id, updates in updates_by_dataset.items():
            for upd in updates:
                ok = update_dataset_entry(
                    ds_id,
                    upd["entry_id"],
                    upd["input"],
                    upd["new_expected"],
                    headers
                )
                if ok:
                    success_count += 1
                else:
                    fail_count += 1

        if not args.json:
            print(f"Done! {success_count} updated, {fail_count} failed")
    elif not args.apply and total_updates > 0 and not args.json:
        print("Run with --apply to sync changes.")


if __name__ == "__main__":
    main()
