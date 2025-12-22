#!/usr/bin/env python3
"""
Braintrust Scorers Management Tool
CRUD operations for Braintrust project scores (scorers) via the REST API
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
                    key = key.strip()
                    value = value.strip()
                    if key and key not in os.environ:
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
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
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

def check_project_access(project_id: str) -> bool:
    """Check if we have access to a project. Returns True if accessible, False otherwise."""
    api_key = get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{API_BASE_URL}/v1/project/{project_id}",
            headers=headers
        )
        if response.status_code == 403:
            return False
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False

def list_scorers(project_id: Optional[str] = None, limit: int = 100, function_type: str = "scorer") -> None:
    """List all scorers (functions with type 'scorer')"""
    # Check project access first if project_id is provided
    if project_id:
        if not check_project_access(project_id):
            print(f"Error: No access to project {project_id} or project does not exist", file=sys.stderr)
            sys.exit(1)

    params = {"limit": limit, "function_type": function_type}
    if project_id:
        params["project_id"] = project_id

    result = make_request("GET", "/v1/function", params=params)

    # Provide helpful message if no scorers found
    if len(result.get("objects", [])) == 0:
        if project_id:
            print(f"No scorers found in project {project_id}", file=sys.stderr)
            print(f"You can use global scorers (e.g., 'Factuality', 'ExactMatch') or create custom scorers.", file=sys.stderr)
        else:
            print("No scorers found", file=sys.stderr)

    print(json.dumps(result, indent=2))

def get_scorer(scorer_id: str) -> None:
    """Get a specific scorer by ID (using Functions API)"""
    result = make_request("GET", f"/v1/function/{scorer_id}")
    print(json.dumps(result, indent=2))

def create_scorer(
    name: str,
    project_id: str,
    description: Optional[str] = None,
    config_file: Optional[str] = None,
    scorer_type: Optional[str] = None,
    tags: Optional[str] = None
) -> None:
    """Create a new scorer (function)"""
    data = {
        "name": name,
        "project_id": project_id,
        "function_type": "scorer"
    }

    if description:
        data["description"] = description

    # Load configuration from file if provided
    if config_file:
        config_path = Path(config_file)
        if not config_path.exists():
            print(f"Error: Config file not found: {config_file}", file=sys.stderr)
            sys.exit(1)

        with open(config_path) as f:
            config_data = json.load(f)
            # Merge config data into request
            data.update(config_data)

    if scorer_type:
        data["score_type"] = scorer_type

    if tags is not None:
        data["tags"] = parse_tags(tags)

    result = make_request("POST", "/v1/function", data=data)
    print(json.dumps(result, indent=2))

def update_scorer(
    scorer_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    config_file: Optional[str] = None,
    tags: Optional[str] = None
) -> None:
    """Update an existing scorer"""
    data = {}

    if name:
        data["name"] = name
    if description:
        data["description"] = description

    # Load configuration from file if provided
    if config_file:
        config_path = Path(config_file)
        if not config_path.exists():
            print(f"Error: Config file not found: {config_file}", file=sys.stderr)
            sys.exit(1)

        with open(config_path) as f:
            config_data = json.load(f)
            data.update(config_data)

    if tags is not None:
        data["tags"] = parse_tags(tags)

    if not data:
        print("Error: No update parameters provided", file=sys.stderr)
        sys.exit(1)

    result = make_request("PATCH", f"/v1/function/{scorer_id}", data=data)
    print(json.dumps(result, indent=2))

def delete_scorer(scorer_id: str) -> None:
    """Delete a scorer (function)"""
    result = make_request("DELETE", f"/v1/function/{scorer_id}")
    print(json.dumps(result, indent=2))

def main():
    parser = argparse.ArgumentParser(
        description="Manage Braintrust project scores (scorers)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all scorers in a project
  python3 braintrust_scorers.py list --project-id PROJECT_ID

  # Get a specific scorer
  python3 braintrust_scorers.py get SCORER_ID

  # Create a custom scorer
  python3 braintrust_scorers.py create \\
    --name "My Scorer" \\
    --project-id PROJECT_ID \\
    --description "Custom scoring function" \\
    --config-file scorer_config.json

  # Update a scorer
  python3 braintrust_scorers.py update SCORER_ID \\
    --name "Updated Name" \\
    --description "Updated description"

  # Delete a scorer
  python3 braintrust_scorers.py delete SCORER_ID
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List command
    list_parser = subparsers.add_parser("list", help="List all scorers")
    list_parser.add_argument("--project-id", help="Filter by project ID")
    list_parser.add_argument("--limit", type=int, default=100, help="Maximum number of results")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get a specific scorer")
    get_parser.add_argument("scorer_id", help="Scorer ID")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new scorer")
    create_parser.add_argument("--name", required=True, help="Scorer name")
    create_parser.add_argument("--project-id", required=True, help="Project ID")
    create_parser.add_argument("--description", help="Scorer description")
    create_parser.add_argument("--config-file", help="Path to JSON config file with scorer configuration")
    create_parser.add_argument("--scorer-type", help="Scorer type (python, typescript, llm)")
    create_parser.add_argument("--tags", help="Tags as JSON array '[\"tag1\", \"tag2\"]' or single string")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update a scorer")
    update_parser.add_argument("scorer_id", help="Scorer ID")
    update_parser.add_argument("--name", help="New scorer name")
    update_parser.add_argument("--description", help="New description")
    update_parser.add_argument("--config-file", help="Path to JSON config file with updates")
    update_parser.add_argument("--tags", help="Tags as JSON array '[\"tag1\", \"tag2\"]' or single string")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a scorer")
    delete_parser.add_argument("scorer_id", help="Scorer ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "list":
            list_scorers(project_id=args.project_id, limit=args.limit)
        elif args.command == "get":
            get_scorer(args.scorer_id)
        elif args.command == "create":
            create_scorer(
                name=args.name,
                project_id=args.project_id,
                description=args.description,
                config_file=args.config_file,
                scorer_type=args.scorer_type,
                tags=args.tags
            )
        elif args.command == "update":
            update_scorer(
                scorer_id=args.scorer_id,
                name=args.name,
                description=args.description,
                config_file=args.config_file,
                tags=args.tags
            )
        elif args.command == "delete":
            delete_scorer(args.scorer_id)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
