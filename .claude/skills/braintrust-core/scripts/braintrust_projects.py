#!/usr/bin/env python3
"""
Braintrust Projects Management Tool
CRUD operations for Braintrust projects via the REST API
"""

import os
import sys
import json
import argparse
import requests
from typing import Optional, Dict, Any
from pathlib import Path

API_BASE_URL = "https://api.braintrust.dev"


def parse_tags(tags: Optional[str]) -> Optional[list]:
    """Parse tags from CLI argument. Returns None if no tags provided."""
    if tags is None:
        return None
    try:
        parsed = json.loads(tags)
        return parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        return [tags] if tags else []

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

def list_projects(org_name: Optional[str] = None, limit: int = 100) -> None:
    """List all projects"""
    params = {"limit": limit}
    if org_name:
        params["org_name"] = org_name

    result = make_request("GET", "/v1/project", params=params)
    print(json.dumps(result, indent=2))

def get_project(project_id: str) -> None:
    """Get a specific project by ID"""
    result = make_request("GET", f"/v1/project/{project_id}")
    print(json.dumps(result, indent=2))

def create_project(name: str, org_name: Optional[str] = None, tags: Optional[str] = None) -> None:
    """Create a new project"""
    data = {
        "name": name
    }

    if org_name:
        data["org_name"] = org_name

    if tags is not None:
        data["tags"] = parse_tags(tags)

    result = make_request("POST", "/v1/project", data=data)
    print(json.dumps(result, indent=2))

def update_project(project_id: str, name: Optional[str] = None, tags: Optional[str] = None) -> None:
    """Update an existing project"""
    data = {}

    if name:
        data["name"] = name

    if tags is not None:
        data["tags"] = parse_tags(tags)

    if not data:
        print("Error: No update fields provided", file=sys.stderr)
        sys.exit(1)

    result = make_request("PATCH", f"/v1/project/{project_id}", data=data)
    print(json.dumps(result, indent=2))

def delete_project(project_id: str) -> None:
    """Delete a project"""
    result = make_request("DELETE", f"/v1/project/{project_id}")
    print(json.dumps(result, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Manage Braintrust projects")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # List projects
    list_parser = subparsers.add_parser("list", help="List projects")
    list_parser.add_argument("--org-name", help="Filter by organization name")
    list_parser.add_argument("--limit", type=int, default=100, help="Maximum number of projects to return")

    # Get project
    get_parser = subparsers.add_parser("get", help="Get a specific project")
    get_parser.add_argument("project_id", help="Project ID")

    # Create project
    create_parser = subparsers.add_parser("create", help="Create a new project")
    create_parser.add_argument("--name", required=True, help="Project name")
    create_parser.add_argument("--org-name", help="Organization name")
    create_parser.add_argument("--tags", help="Tags as JSON array '[\"tag1\", \"tag2\"]' or single string")

    # Update project
    update_parser = subparsers.add_parser("update", help="Update a project")
    update_parser.add_argument("project_id", help="Project ID")
    update_parser.add_argument("--name", help="New project name")
    update_parser.add_argument("--tags", help="Tags as JSON array '[\"tag1\", \"tag2\"]' or single string")

    # Delete project
    delete_parser = subparsers.add_parser("delete", help="Delete a project")
    delete_parser.add_argument("project_id", help="Project ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "list":
            list_projects(args.org_name, args.limit)
        elif args.command == "get":
            get_project(args.project_id)
        elif args.command == "create":
            create_project(args.name, args.org_name, args.tags)
        elif args.command == "update":
            update_project(args.project_id, args.name, args.tags)
        elif args.command == "delete":
            delete_project(args.project_id)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
