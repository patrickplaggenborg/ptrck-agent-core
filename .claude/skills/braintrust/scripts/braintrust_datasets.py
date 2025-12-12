#!/usr/bin/env python3
"""
Braintrust Datasets Management Tool
CRUD operations for Braintrust datasets via the REST API
"""

import os
import sys
import json
import argparse
import requests
from typing import Optional, Dict, Any, List

API_BASE_URL = "https://api.braintrust.dev"

def get_api_key() -> str:
    """Get the Braintrust API key from environment"""
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

def list_datasets(project_id: Optional[str] = None, limit: int = 100) -> None:
    """List all datasets"""
    params = {"limit": limit}
    if project_id:
        params["project_id"] = project_id

    result = make_request("GET", "/v1/dataset", params=params)
    print(json.dumps(result, indent=2))

def get_dataset(dataset_id: str) -> None:
    """Get a specific dataset by ID"""
    result = make_request("GET", f"/v1/dataset/{dataset_id}")
    print(json.dumps(result, indent=2))

def create_dataset(name: str, project_id: str, description: Optional[str] = None) -> None:
    """Create a new dataset"""
    data = {
        "name": name,
        "project_id": project_id
    }

    if description:
        data["description"] = description

    result = make_request("POST", "/v1/dataset", data=data)
    print(json.dumps(result, indent=2))

def update_dataset(dataset_id: str, name: Optional[str] = None, description: Optional[str] = None) -> None:
    """Update an existing dataset"""
    data = {}

    if name:
        data["name"] = name
    if description:
        data["description"] = description

    if not data:
        print("Error: No update fields provided", file=sys.stderr)
        sys.exit(1)

    result = make_request("PATCH", f"/v1/dataset/{dataset_id}", data=data)
    print(json.dumps(result, indent=2))

def delete_dataset(dataset_id: str) -> None:
    """Delete a dataset"""
    result = make_request("DELETE", f"/v1/dataset/{dataset_id}")
    print(json.dumps(result, indent=2))

def insert_events(dataset_id: str, events_file: str) -> None:
    """Insert events into a dataset from a JSON file"""
    try:
        with open(events_file, 'r') as f:
            events = json.load(f)

        if not isinstance(events, list):
            events = [events]

        data = {
            "dataset_id": dataset_id,
            "events": events
        }

        result = make_request("POST", "/v1/dataset-insert", data=data)
        print(json.dumps(result, indent=2))
    except FileNotFoundError:
        print(f"Error: File not found: {events_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}", file=sys.stderr)
        sys.exit(1)

def fetch_records(dataset_id: str, limit: int = 100, cursor: Optional[str] = None) -> None:
    """Fetch records from a dataset"""
    data = {
        "dataset_id": dataset_id,
        "limit": limit
    }

    if cursor:
        data["cursor"] = cursor

    result = make_request("POST", "/v1/dataset-fetch", data=data)
    print(json.dumps(result, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Manage Braintrust datasets")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # List datasets
    list_parser = subparsers.add_parser("list", help="List datasets")
    list_parser.add_argument("--project-id", help="Filter by project ID")
    list_parser.add_argument("--limit", type=int, default=100, help="Maximum number of datasets to return")

    # Get dataset
    get_parser = subparsers.add_parser("get", help="Get a specific dataset")
    get_parser.add_argument("dataset_id", help="Dataset ID")

    # Create dataset
    create_parser = subparsers.add_parser("create", help="Create a new dataset")
    create_parser.add_argument("--name", required=True, help="Dataset name")
    create_parser.add_argument("--project-id", required=True, help="Project ID")
    create_parser.add_argument("--description", help="Dataset description")

    # Update dataset
    update_parser = subparsers.add_parser("update", help="Update a dataset")
    update_parser.add_argument("dataset_id", help="Dataset ID")
    update_parser.add_argument("--name", help="New dataset name")
    update_parser.add_argument("--description", help="New dataset description")

    # Delete dataset
    delete_parser = subparsers.add_parser("delete", help="Delete a dataset")
    delete_parser.add_argument("dataset_id", help="Dataset ID")

    # Insert events
    insert_parser = subparsers.add_parser("insert", help="Insert events into a dataset")
    insert_parser.add_argument("dataset_id", help="Dataset ID")
    insert_parser.add_argument("--file", required=True, help="JSON file containing events")

    # Fetch records
    fetch_parser = subparsers.add_parser("fetch", help="Fetch records from a dataset")
    fetch_parser.add_argument("dataset_id", help="Dataset ID")
    fetch_parser.add_argument("--limit", type=int, default=100, help="Maximum number of records to return")
    fetch_parser.add_argument("--cursor", help="Cursor for pagination")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "list":
            list_datasets(args.project_id, args.limit)
        elif args.command == "get":
            get_dataset(args.dataset_id)
        elif args.command == "create":
            create_dataset(args.name, args.project_id, args.description)
        elif args.command == "update":
            update_dataset(args.dataset_id, args.name, args.description)
        elif args.command == "delete":
            delete_dataset(args.dataset_id)
        elif args.command == "insert":
            insert_events(args.dataset_id, args.file)
        elif args.command == "fetch":
            fetch_records(args.dataset_id, args.limit, args.cursor)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
