#!/usr/bin/env python3
"""
Confluence CLI wrapper for Claude skills.
Wraps pchuri/confluence-cli commands for page management.
"""

import subprocess
import json
import sys
import argparse
from typing import Optional


def run_confluence(args: list[str]) -> str:
    """Run confluence-cli command and return output."""
    cmd = ['confluence-cli'] + args

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        error_msg = result.stderr or result.stdout or "Unknown error"
        return json.dumps({"error": error_msg.strip()})

    # Try to parse as JSON, otherwise return as-is
    output = result.stdout.strip()
    try:
        # Validate it's valid JSON
        json.loads(output)
        return output
    except json.JSONDecodeError:
        # Return raw output wrapped in JSON
        return json.dumps({"output": output})


def search(query: str, space: Optional[str] = None, limit: int = 25) -> str:
    """Search for pages."""
    args = ['search', query]
    if space:
        args.extend(['--space', space])
    args.extend(['--limit', str(limit)])
    return run_confluence(args)


def get_page(page_id: str) -> str:
    """Get page content by ID."""
    return run_confluence(['get', page_id])


def create_page(
    space: str,
    title: str,
    content: str,
    parent_id: Optional[str] = None
) -> str:
    """Create a new page."""
    args = ['create', '--space', space, '--title', title, '--content', content]
    if parent_id:
        args.extend(['--parent', parent_id])
    return run_confluence(args)


def update_page(
    page_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None
) -> str:
    """Update an existing page."""
    args = ['update', page_id]
    if title:
        args.extend(['--title', title])
    if content:
        args.extend(['--content', content])

    if len(args) == 2:
        return json.dumps({"error": "No update fields provided"})

    return run_confluence(args)


def delete_page(page_id: str) -> str:
    """Delete a page."""
    return run_confluence(['delete', page_id])


def list_spaces() -> str:
    """List all available spaces."""
    return run_confluence(['spaces'])


def main():
    parser = argparse.ArgumentParser(description="Confluence CLI wrapper for Claude skills")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Search
    search_parser = subparsers.add_parser("search", help="Search pages")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--space", "-s", help="Filter by space key")
    search_parser.add_argument("--limit", "-l", type=int, default=25, help="Max results")

    # Get
    get_parser = subparsers.add_parser("get", help="Get page content")
    get_parser.add_argument("page_id", help="Page ID")

    # Create
    create_parser = subparsers.add_parser("create", help="Create a new page")
    create_parser.add_argument("--space", "-s", required=True, help="Space key")
    create_parser.add_argument("--title", "-t", required=True, help="Page title")
    create_parser.add_argument("--content", "-c", required=True, help="Page content")
    create_parser.add_argument("--parent", "-p", help="Parent page ID")

    # Update
    update_parser = subparsers.add_parser("update", help="Update a page")
    update_parser.add_argument("page_id", help="Page ID")
    update_parser.add_argument("--title", "-t", help="New title")
    update_parser.add_argument("--content", "-c", help="New content")

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete a page")
    delete_parser.add_argument("page_id", help="Page ID")

    # Spaces
    subparsers.add_parser("spaces", help="List all spaces")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "search":
            print(search(args.query, args.space, args.limit))
        elif args.command == "get":
            print(get_page(args.page_id))
        elif args.command == "create":
            print(create_page(args.space, args.title, args.content, args.parent))
        elif args.command == "update":
            print(update_page(args.page_id, args.title, args.content))
        elif args.command == "delete":
            print(delete_page(args.page_id))
        elif args.command == "spaces":
            print(list_spaces())
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
