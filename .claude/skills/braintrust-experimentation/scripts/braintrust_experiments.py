#!/usr/bin/env python3
"""
Braintrust Experiments Management Tool
CRUD operations for Braintrust experiments via the REST API
"""

import os
import sys
import json
import argparse
import requests
from typing import Optional, Dict, Any
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
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json() if response.text else {}
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)

def list_experiments(project_id: Optional[str] = None, limit: int = 100) -> None:
    """List all experiments"""
    params = {"limit": limit}
    if project_id:
        params["project_id"] = project_id

    result = make_request("GET", "/v1/experiment", params=params)
    print(json.dumps(result, indent=2))

def get_experiment(experiment_id: str) -> None:
    """Get a specific experiment by ID"""
    result = make_request("GET", f"/v1/experiment/{experiment_id}")
    print(json.dumps(result, indent=2))

def create_experiment(name: str, project_id: str, description: Optional[str] = None, dataset_id: Optional[str] = None) -> None:
    """Create a new experiment"""
    data = {
        "name": name,
        "project_id": project_id
    }

    if description:
        data["description"] = description
    if dataset_id:
        data["dataset_id"] = dataset_id

    result = make_request("POST", "/v1/experiment", data=data)
    print(json.dumps(result, indent=2))

def update_experiment(experiment_id: str, name: Optional[str] = None, description: Optional[str] = None) -> None:
    """Update an existing experiment"""
    data = {}

    if name:
        data["name"] = name
    if description:
        data["description"] = description

    if not data:
        print("Error: No update fields provided", file=sys.stderr)
        sys.exit(1)

    result = make_request("PATCH", f"/v1/experiment/{experiment_id}", data=data)
    print(json.dumps(result, indent=2))

def delete_experiment(experiment_id: str) -> None:
    """Delete an experiment"""
    result = make_request("DELETE", f"/v1/experiment/{experiment_id}")
    print(json.dumps(result, indent=2))

def insert_events(experiment_id: str, events_file: str) -> None:
    """Insert events into an experiment from a JSON file"""
    try:
        with open(events_file, 'r') as f:
            events = json.load(f)

        if not isinstance(events, list):
            events = [events]

        data = {
            "experiment_id": experiment_id,
            "events": events
        }

        result = make_request("POST", "/v1/experiment-insert", data=data)
        print(json.dumps(result, indent=2))
    except FileNotFoundError:
        print(f"Error: File not found: {events_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}", file=sys.stderr)
        sys.exit(1)

def summarize_experiment(experiment_id: str, summarize_scores: bool = True) -> None:
    """Summarize experiment results"""
    data = {
        "experiment_id": experiment_id,
        "summarize_scores": summarize_scores
    }

    result = make_request("POST", "/v1/experiment-summarize", data=data)
    print(json.dumps(result, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Manage Braintrust experiments")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # List experiments
    list_parser = subparsers.add_parser("list", help="List experiments")
    list_parser.add_argument("--project-id", help="Filter by project ID")
    list_parser.add_argument("--limit", type=int, default=100, help="Maximum number of experiments to return")

    # Get experiment
    get_parser = subparsers.add_parser("get", help="Get a specific experiment")
    get_parser.add_argument("experiment_id", help="Experiment ID")

    # Create experiment
    create_parser = subparsers.add_parser("create", help="Create a new experiment")
    create_parser.add_argument("--name", required=True, help="Experiment name")
    create_parser.add_argument("--project-id", required=True, help="Project ID")
    create_parser.add_argument("--description", help="Experiment description")
    create_parser.add_argument("--dataset-id", help="Dataset ID to link to this experiment")

    # Update experiment
    update_parser = subparsers.add_parser("update", help="Update an experiment")
    update_parser.add_argument("experiment_id", help="Experiment ID")
    update_parser.add_argument("--name", help="New experiment name")
    update_parser.add_argument("--description", help="New experiment description")

    # Delete experiment
    delete_parser = subparsers.add_parser("delete", help="Delete an experiment")
    delete_parser.add_argument("experiment_id", help="Experiment ID")

    # Insert events
    insert_parser = subparsers.add_parser("insert", help="Insert events into an experiment")
    insert_parser.add_argument("experiment_id", help="Experiment ID")
    insert_parser.add_argument("--file", required=True, help="JSON file containing events")

    # Summarize experiment
    summarize_parser = subparsers.add_parser("summarize", help="Summarize experiment results")
    summarize_parser.add_argument("experiment_id", help="Experiment ID")
    summarize_parser.add_argument("--no-scores", action="store_false", dest="summarize_scores", help="Don't summarize scores")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "list":
            list_experiments(args.project_id, args.limit)
        elif args.command == "get":
            get_experiment(args.experiment_id)
        elif args.command == "create":
            create_experiment(args.name, args.project_id, args.description, args.dataset_id)
        elif args.command == "update":
            update_experiment(args.experiment_id, args.name, args.description)
        elif args.command == "delete":
            delete_experiment(args.experiment_id)
        elif args.command == "insert":
            insert_events(args.experiment_id, args.file)
        elif args.command == "summarize":
            summarize_experiment(args.experiment_id, args.summarize_scores)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
