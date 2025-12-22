#!/usr/bin/env python3
"""
Fetch experiment results from Braintrust
Retrieves all datapoints (inputs, outputs, expected, scores, metadata) from an experiment
"""

import os
import sys
import json
import argparse
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

def make_request(method: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
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
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json() if response.text else {}
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)

def transform_to_flat_dataset(raw_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform raw Braintrust results into a clean flat dataset structure

    Args:
        raw_results: Raw results from Braintrust API

    Returns:
        List of flat datapoints with input, output, expected, metadata, and scores
    """
    # First, build a map of root_span_id to scores
    scores_map = {}
    for item in raw_results:
        if item.get("span_attributes", {}).get("type") == "score":
            root_span_id = item.get("root_span_id")
            if root_span_id:
                if root_span_id not in scores_map:
                    scores_map[root_span_id] = {}
                # Merge all scores for this root span
                item_scores = item.get("scores", {})
                scores_map[root_span_id].update(item_scores)

    # Now collect root items and attach their scores
    flat_dataset = []
    for item in raw_results:
        # Only process root eval items (where span_id == root_span_id and is_root == True)
        if item.get("is_root") and item.get("span_id") == item.get("root_span_id"):
            root_span_id = item.get("root_span_id")

            flat_record = {
                "root_span_id": root_span_id,
                "input": item.get("input"),
                "output": item.get("output"),
                "expected": item.get("expected"),
                "metadata": item.get("metadata", {}),
                "scores": scores_map.get(root_span_id, {})
            }

            flat_dataset.append(flat_record)

    return flat_dataset

def fetch_experiment_results(experiment_id: str, limit: Optional[int] = None, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Fetch all results from an experiment using pagination

    Args:
        experiment_id: The experiment ID to fetch results from
        limit: Number of results per page (default: 1000, max per Braintrust API)
        max_results: Maximum total results to fetch (default: unlimited)

    Returns:
        List of all experiment datapoints
    """
    all_results = []
    cursor = None
    page_limit = limit or 1000  # Default to max allowed by API

    while True:
        params = {"limit": page_limit}
        if cursor:
            params["cursor"] = cursor

        response = make_request("GET", f"/v1/experiment/{experiment_id}/fetch", params=params)

        # Extract events from response
        events = response.get("events", [])
        all_results.extend(events)

        # Check if we've reached max_results
        if max_results and len(all_results) >= max_results:
            all_results = all_results[:max_results]
            break

        # Check if there are more pages
        cursor = response.get("cursor")
        if not cursor:
            break

    return all_results

def main():
    parser = argparse.ArgumentParser(
        description="Fetch experiment results from Braintrust",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch all results from an experiment
  %(prog)s abc-123-def

  # Fetch with pagination control
  %(prog)s abc-123-def --limit 500

  # Fetch only first 100 results
  %(prog)s abc-123-def --max-results 100

  # Save to file
  %(prog)s abc-123-def > results.json
        """
    )

    parser.add_argument("experiment_id", help="Experiment ID to fetch results from")
    parser.add_argument("--limit", type=int, help="Number of results per page (default: 1000)")
    parser.add_argument("--max-results", type=int, help="Maximum total results to fetch (default: unlimited)")

    args = parser.parse_args()

    try:
        raw_results = fetch_experiment_results(args.experiment_id, args.limit, args.max_results)
        flat_dataset = transform_to_flat_dataset(raw_results)
        print(json.dumps(flat_dataset, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
