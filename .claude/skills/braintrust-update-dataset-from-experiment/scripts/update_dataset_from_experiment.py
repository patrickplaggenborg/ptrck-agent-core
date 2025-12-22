#!/usr/bin/env python3
"""
Update dataset records from experiment edits.
Syncs corrected 'expected' values from a Braintrust experiment back to the source dataset.
"""

import os
import sys
import json
import argparse
import subprocess
import requests
from typing import Optional, Dict, Any, List
from pathlib import Path

API_BASE_URL = "https://api.braintrust.dev"


def load_env():
    """Load environment variables from .env file if it exists"""
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key not in os.environ:
                        os.environ[key] = value


def get_api_key() -> str:
    """Get the Braintrust API key from environment"""
    load_env()
    api_key = os.environ.get("BRAINTRUST_API_KEY")
    if not api_key:
        raise ValueError("BRAINTRUST_API_KEY environment variable not set")
    return api_key


def make_request(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Make an authenticated request to the Braintrust API"""
    api_key = get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    url = f"{API_BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json() if response.text else {}
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)


def fetch_edited_records(experiment_id: str) -> List[Dict[str, Any]]:
    """
    Fetch edited records from an experiment using the fetch skill.

    Args:
        experiment_id: The experiment ID to fetch edited records from

    Returns:
        List of edited records with origin info
    """
    # Find the fetch script relative to this script
    script_dir = Path(__file__).parent.parent.parent
    fetch_script = script_dir / "braintrust-fetch-experiment-results" / "scripts" / "fetch_experiment_results.py"

    if not fetch_script.exists():
        raise FileNotFoundError(f"Fetch script not found at: {fetch_script}")

    try:
        result = subprocess.run(
            [sys.executable, str(fetch_script), experiment_id, "--edited-only"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching experiment results: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing fetch results: {e}", file=sys.stderr)
        sys.exit(1)


def prepare_dataset_events(edited_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prepare dataset events for upsert from edited experiment records.

    Args:
        edited_records: List of edited records from experiment

    Returns:
        List of events ready for dataset insert (upsert)
    """
    events = []
    for record in edited_records:
        origin = record.get("origin")
        if not origin or not origin.get("dataset_record_id"):
            print(f"Warning: Skipping record without dataset origin: {record.get('input', '')[:50]}", file=sys.stderr)
            continue

        event = {
            "id": origin["dataset_record_id"],  # Use same ID for upsert
            "input": record.get("input"),
            "expected": record.get("expected"),
        }

        # Include metadata if present
        if record.get("metadata"):
            event["metadata"] = record["metadata"]

        events.append(event)

    return events


def get_dataset_info(dataset_id: str) -> Dict[str, Any]:
    """
    Fetch dataset info including name and project.

    Args:
        dataset_id: The dataset ID

    Returns:
        Dataset info dict with name, project_id, etc.
    """
    return make_request("GET", f"/v1/dataset/{dataset_id}")


def get_project_info(project_id: str) -> Dict[str, Any]:
    """
    Fetch project info including name.

    Args:
        project_id: The project ID

    Returns:
        Project info dict with name, org_name, etc.
    """
    return make_request("GET", f"/v1/project/{project_id}")


def build_dataset_url(dataset_info: Dict[str, Any], project_info: Dict[str, Any], org_name: str = "HolidayDiscounter") -> str:
    """
    Build the Braintrust UI URL for a dataset.

    Args:
        dataset_info: Dataset info from API
        project_info: Project info from API
        org_name: Organization name (defaults to HolidayDiscounter)

    Returns:
        URL string to the dataset in Braintrust UI
    """
    from urllib.parse import quote

    project_name = quote(project_info.get("name", ""), safe="")
    dataset_name = quote(dataset_info.get("name", ""), safe="")

    return f"https://www.braintrust.dev/app/{org_name}/p/{project_name}/datasets/{dataset_name}"


def update_dataset(dataset_id: str, events: List[Dict[str, Any]], dry_run: bool = False) -> Dict[str, Any]:
    """
    Update dataset records via the insert API (upsert behavior).

    Args:
        dataset_id: The dataset ID to update
        events: List of events to upsert
        dry_run: If True, don't actually update, just return what would be done

    Returns:
        API response or dry-run summary
    """
    if dry_run:
        return {
            "dry_run": True,
            "dataset_id": dataset_id,
            "records_to_update": len(events),
            "events": events
        }

    data = {"events": events}
    return make_request("POST", f"/v1/dataset/{dataset_id}/insert", data=data)


def main():
    parser = argparse.ArgumentParser(
        description="Update dataset records from experiment edits",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be updated (dry run)
  %(prog)s EXPERIMENT_ID --dry-run

  # Update the dataset with edited records
  %(prog)s EXPERIMENT_ID

  # Show verbose output
  %(prog)s EXPERIMENT_ID --verbose
        """
    )

    parser.add_argument("experiment_id", help="Experiment ID to sync edits from")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without updating the dataset")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    try:
        # Step 1: Fetch edited records
        if args.verbose:
            print(f"Fetching edited records from experiment: {args.experiment_id}", file=sys.stderr)
            sys.stderr.flush()

        edited_records = fetch_edited_records(args.experiment_id)

        if not edited_records:
            print("No edited records found in experiment.", file=sys.stderr)
            sys.stderr.flush()
            print(json.dumps({"updated": 0, "message": "No edited records found"}))
            sys.exit(0)

        if args.verbose:
            print(f"Found {len(edited_records)} edited records", file=sys.stderr)
            sys.stderr.flush()

        # Step 2: Get dataset ID from first record
        dataset_id = edited_records[0].get("origin", {}).get("dataset_id")
        if not dataset_id:
            print("Error: Could not determine dataset ID from experiment records", file=sys.stderr)
            sys.exit(1)

        # Step 3: Fetch dataset and project info for URL
        if args.verbose:
            print(f"Fetching dataset info...", file=sys.stderr)
            sys.stderr.flush()

        dataset_info = get_dataset_info(dataset_id)
        project_id = dataset_info.get("project_id")
        project_info = get_project_info(project_id) if project_id else {}
        dataset_url = build_dataset_url(dataset_info, project_info)

        if args.verbose:
            print(f"Target dataset: {dataset_info.get('name', dataset_id)}", file=sys.stderr)
            print(f"Dataset URL: {dataset_url}", file=sys.stderr)
            sys.stderr.flush()

        # Step 4: Prepare events for upsert
        events = prepare_dataset_events(edited_records)

        if not events:
            print("No valid records to update (all records missing dataset origin).", file=sys.stderr)
            sys.stderr.flush()
            print(json.dumps({"updated": 0, "message": "No valid records to update"}))
            sys.exit(0)

        # Step 5: Update dataset (or dry run)
        if args.dry_run:
            if args.verbose:
                print("DRY RUN - No changes will be made", file=sys.stderr)
                sys.stderr.flush()
            result = update_dataset(dataset_id, events, dry_run=True)
            result["dataset_url"] = dataset_url
        else:
            if args.verbose:
                print(f"Updating {len(events)} records in dataset...", file=sys.stderr)
                sys.stderr.flush()
            result = update_dataset(dataset_id, events, dry_run=False)
            result["updated"] = len(events)
            result["dataset_id"] = dataset_id
            result["dataset_name"] = dataset_info.get("name")
            result["dataset_url"] = dataset_url

        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
