#!/usr/bin/env python3
"""
Confluence CLI wrapper for Claude skills (READ-ONLY).
Wraps pchuri/confluence-cli commands for read-only page queries.
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

    output = result.stdout.strip()
    try:
        json.loads(output)
        return output
    except json.JSONDecodeError:
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


def list_spaces() -> str:
    """List all available spaces."""
    return run_confluence(['spaces'])


def main():
    parser = argparse.ArgumentParser(description="Confluence CLI wrapper (READ-ONLY)")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Search
    search_parser = subparsers.add_parser("search", help="Search pages")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--space", "-s", help="Filter by space key")
    search_parser.add_argument("--limit", "-l", type=int, default=25, help="Max results")

    # Get
    get_parser = subparsers.add_parser("get", help="Get page content")
    get_parser.add_argument("page_id", help="Page ID")

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
        elif args.command == "spaces":
            print(list_spaces())
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
