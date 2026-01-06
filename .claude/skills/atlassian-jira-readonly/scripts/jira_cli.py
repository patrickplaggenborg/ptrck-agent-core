#!/usr/bin/env python3
"""
Jira CLI wrapper for Claude skills (READ-ONLY).
Wraps ankitpokhrel/jira-cli commands for read-only issue queries.
"""

import subprocess
import json
import sys
import argparse


def run_jira(args: list[str], raw: bool = True) -> str:
    """Run jira-cli command and return output."""
    cmd = ['jira'] + args
    if raw and '--raw' not in args:
        cmd.append('--raw')

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        error_msg = result.stderr or result.stdout or "Unknown error"
        return json.dumps({"error": error_msg.strip()})

    return result.stdout


def search(jql: str, limit: int = 50) -> str:
    """Search issues using JQL."""
    return run_jira(['issue', 'list', '-q', jql, '-l', str(limit)])


def get_issue(key: str) -> str:
    """Get issue details by key."""
    return run_jira(['issue', 'view', key])


def list_sprints(board_id: int, state: str | None = None) -> str:
    """List sprints for a board."""
    args = ['sprint', 'list', '-b', str(board_id)]
    if state:
        args.extend(['--state', state])
    return run_jira(args)


def main():
    parser = argparse.ArgumentParser(description="Jira CLI wrapper (READ-ONLY)")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Search
    search_parser = subparsers.add_parser("search", help="Search issues using JQL")
    search_parser.add_argument("jql", help="JQL query string")
    search_parser.add_argument("--limit", "-l", type=int, default=50, help="Max results")

    # Get
    get_parser = subparsers.add_parser("get", help="Get issue details")
    get_parser.add_argument("key", help="Issue key (e.g., PROJ-123)")

    # Sprints
    sprint_parser = subparsers.add_parser("sprints", help="List sprints")
    sprint_parser.add_argument("--board", "-b", type=int, required=True, help="Board ID")
    sprint_parser.add_argument("--state", "-s", help="Sprint state filter")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "search":
            print(search(args.jql, args.limit))
        elif args.command == "get":
            print(get_issue(args.key))
        elif args.command == "sprints":
            print(list_sprints(args.board, args.state))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
