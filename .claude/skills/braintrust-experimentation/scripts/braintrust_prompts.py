#!/usr/bin/env python3
"""
Braintrust Prompts Management Tool
CRUD operations for Braintrust prompts via the REST API
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
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
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

def list_prompts(project_id: Optional[str] = None, limit: int = 100) -> None:
    """List all prompts"""
    params = {"limit": limit}
    if project_id:
        params["project_id"] = project_id

    result = make_request("GET", "/v1/prompt", params=params)
    print(json.dumps(result, indent=2))

def get_prompt(prompt_id: str) -> None:
    """Get a specific prompt by ID"""
    result = make_request("GET", f"/v1/prompt/{prompt_id}")
    print(json.dumps(result, indent=2))

def create_prompt(name: str, project_id: str, slug: Optional[str] = None, prompt_data: Optional[str] = None, description: Optional[str] = None, tags: Optional[str] = None) -> None:
    """Create a new prompt"""
    # Auto-generate slug from name if not provided
    if not slug:
        slug = name.lower().replace(' ', '-').replace('_', '-')
        # Remove special characters except hyphens
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        # Remove consecutive hyphens
        while '--' in slug:
            slug = slug.replace('--', '-')
        slug = slug.strip('-')

    data = {
        "name": name,
        "slug": slug,
        "project_id": project_id
    }

    if prompt_data:
        try:
            data["prompt_data"] = json.loads(prompt_data)
        except json.JSONDecodeError:
            data["prompt_data"] = {"prompt": prompt_data}

    if description:
        data["description"] = description

    if tags is not None:
        data["tags"] = parse_tags(tags)

    result = make_request("POST", "/v1/prompt", data=data)
    print(json.dumps(result, indent=2))

def update_prompt(prompt_id: str, name: Optional[str] = None, prompt_data: Optional[str] = None, description: Optional[str] = None, tags: Optional[str] = None, tools_file: Optional[str] = None) -> None:
    """Update an existing prompt"""
    data = {}

    if name:
        data["name"] = name
    if prompt_data:
        try:
            data["prompt_data"] = json.loads(prompt_data)
        except json.JSONDecodeError:
            data["prompt_data"] = {"prompt": prompt_data}
    if description:
        data["description"] = description

    if tags is not None:
        data["tags"] = parse_tags(tags)

    if tools_file:
        tools_path = Path(tools_file)
        if not tools_path.exists():
            print(f"Error: Tools file not found: {tools_file}", file=sys.stderr)
            sys.exit(1)
        with open(tools_path) as f:
            tools_data = json.load(f)
        if "prompt_data" not in data:
            data["prompt_data"] = {}
        data["prompt_data"]["tools"] = tools_data

    if not data:
        print("Error: No update fields provided", file=sys.stderr)
        sys.exit(1)

    result = make_request("PUT", f"/v1/prompt/{prompt_id}", data=data)
    print(json.dumps(result, indent=2))

def delete_prompt(prompt_id: str) -> None:
    """Delete a prompt"""
    result = make_request("DELETE", f"/v1/prompt/{prompt_id}")
    print(json.dumps(result, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Manage Braintrust prompts")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # List prompts
    list_parser = subparsers.add_parser("list", help="List prompts")
    list_parser.add_argument("--project-id", help="Filter by project ID")
    list_parser.add_argument("--limit", type=int, default=100, help="Maximum number of prompts to return")

    # Get prompt
    get_parser = subparsers.add_parser("get", help="Get a specific prompt")
    get_parser.add_argument("prompt_id", help="Prompt ID")

    # Create prompt
    create_parser = subparsers.add_parser("create", help="Create a new prompt")
    create_parser.add_argument("--name", required=True, help="Prompt name")
    create_parser.add_argument("--project-id", required=True, help="Project ID")
    create_parser.add_argument("--slug", help="Prompt slug (auto-generated from name if not provided)")
    create_parser.add_argument("--prompt-data", help="Prompt data (JSON string or text)")
    create_parser.add_argument("--description", help="Prompt description")
    create_parser.add_argument("--tags", help="Tags as JSON array '[\"tag1\", \"tag2\"]' or single string")

    # Update prompt
    update_parser = subparsers.add_parser("update", help="Update a prompt")
    update_parser.add_argument("prompt_id", help="Prompt ID")
    update_parser.add_argument("--name", help="New prompt name")
    update_parser.add_argument("--prompt-data", help="New prompt data (JSON string or text)")
    update_parser.add_argument("--description", help="New prompt description")
    update_parser.add_argument("--tags", help="Tags as JSON array '[\"tag1\", \"tag2\"]' or single string")
    update_parser.add_argument("--tools-file", help="Path to JSON file containing tool definitions (OpenAI function calling format)")

    # Delete prompt
    delete_parser = subparsers.add_parser("delete", help="Delete a prompt")
    delete_parser.add_argument("prompt_id", help="Prompt ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "list":
            list_prompts(args.project_id, args.limit)
        elif args.command == "get":
            get_prompt(args.prompt_id)
        elif args.command == "create":
            create_prompt(args.name, args.project_id, args.slug, args.prompt_data, args.description, args.tags)
        elif args.command == "update":
            update_prompt(args.prompt_id, args.name, args.prompt_data, args.description, args.tags, args.tools_file)
        elif args.command == "delete":
            delete_prompt(args.prompt_id)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
