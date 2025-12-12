#!/usr/bin/env python3
"""
Braintrust Logs Management Tool
Operations for Braintrust project logs via the REST API
"""

import os
import sys
import json
import argparse
import requests
from typing import Optional, Dict, Any

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

def insert_logs(project_id: str, events_file: str) -> None:
    """Insert log events into a project from a JSON file"""
    try:
        with open(events_file, 'r') as f:
            events = json.load(f)

        if not isinstance(events, list):
            events = [events]

        data = {
            "project_id": project_id,
            "events": events
        }

        result = make_request("POST", "/v1/project-logs-insert", data=data)
        print(json.dumps(result, indent=2))
    except FileNotFoundError:
        print(f"Error: File not found: {events_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}", file=sys.stderr)
        sys.exit(1)

def fetch_logs(project_id: str, limit: int = 100, cursor: Optional[str] = None, filters: Optional[str] = None) -> None:
    """Fetch logs from a project"""
    data = {
        "project_id": project_id,
        "limit": limit
    }

    if cursor:
        data["cursor"] = cursor

    if filters:
        try:
            data["filters"] = json.loads(filters)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in filters: {e}", file=sys.stderr)
            sys.exit(1)

    result = make_request("POST", "/v1/project-logs-fetch", data=data)
    print(json.dumps(result, indent=2))

def add_feedback(project_id: str, log_id: str, feedback_file: str) -> None:
    """Add feedback to a log entry"""
    try:
        with open(feedback_file, 'r') as f:
            feedback = json.load(f)

        data = {
            "project_id": project_id,
            "log_id": log_id,
            "feedback": feedback
        }

        result = make_request("POST", "/v1/project-logs-feedback", data=data)
        print(json.dumps(result, indent=2))
    except FileNotFoundError:
        print(f"Error: File not found: {feedback_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Manage Braintrust project logs")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Insert logs
    insert_parser = subparsers.add_parser("insert", help="Insert log events into a project")
    insert_parser.add_argument("--project-id", required=True, help="Project ID")
    insert_parser.add_argument("--file", required=True, help="JSON file containing log events")

    # Fetch logs
    fetch_parser = subparsers.add_parser("fetch", help="Fetch logs from a project")
    fetch_parser.add_argument("--project-id", required=True, help="Project ID")
    fetch_parser.add_argument("--limit", type=int, default=100, help="Maximum number of logs to return")
    fetch_parser.add_argument("--cursor", help="Cursor for pagination")
    fetch_parser.add_argument("--filters", help="JSON string with filters to apply")

    # Add feedback
    feedback_parser = subparsers.add_parser("feedback", help="Add feedback to a log entry")
    feedback_parser.add_argument("--project-id", required=True, help="Project ID")
    feedback_parser.add_argument("--log-id", required=True, help="Log ID")
    feedback_parser.add_argument("--file", required=True, help="JSON file containing feedback")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "insert":
            insert_logs(args.project_id, args.file)
        elif args.command == "fetch":
            fetch_logs(args.project_id, args.limit, args.cursor, args.filters)
        elif args.command == "feedback":
            add_feedback(args.project_id, args.log_id, args.file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
