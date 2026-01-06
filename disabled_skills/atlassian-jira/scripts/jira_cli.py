#!/usr/bin/env python3
"""
Jira CLI wrapper for Claude skills.
Wraps ankitpokhrel/jira-cli commands for issue management.
"""

import subprocess
import json
import sys
import argparse
from typing import Optional


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


def create_issue(
    project: str,
    issue_type: str,
    summary: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    labels: Optional[list[str]] = None,
    components: Optional[list[str]] = None
) -> str:
    """Create a new issue."""
    args = [
        'issue', 'create',
        '-t', issue_type,
        '-s', summary,
        '-p', project,
        '--no-input'
    ]

    if description:
        args.extend(['-b', description])
    if priority:
        args.extend(['--priority', priority])
    if assignee:
        args.extend(['-a', assignee])
    if labels:
        for label in labels:
            args.extend(['-l', label])
    if components:
        for component in components:
            args.extend(['-C', component])

    return run_jira(args)


def update_issue(
    key: str,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    labels: Optional[list[str]] = None,
    components: Optional[list[str]] = None
) -> str:
    """Update an existing issue."""
    args = ['issue', 'edit', key, '--no-input']

    if summary:
        args.extend(['-s', summary])
    if description:
        args.extend(['-b', description])
    if priority:
        args.extend(['--priority', priority])
    if assignee:
        args.extend(['-a', assignee])
    if labels:
        for label in labels:
            args.extend(['-l', label])
    if components:
        for component in components:
            args.extend(['-C', component])

    return run_jira(args)


def delete_issue(key: str) -> str:
    """Delete an issue."""
    return run_jira(['issue', 'delete', key, '--no-input'])


def add_comment(key: str, body: str) -> str:
    """Add a comment to an issue."""
    return run_jira(['issue', 'comment', 'add', key, '-b', body, '--no-input'])


def transition_issue(key: str, state: str) -> str:
    """Transition an issue to a new state."""
    return run_jira(['issue', 'move', key, state])


def add_worklog(key: str, time_spent: str, comment: Optional[str] = None) -> str:
    """Add a worklog entry to an issue."""
    args = ['issue', 'worklog', 'add', key, time_spent, '--no-input']
    if comment:
        args.extend(['-c', comment])
    return run_jira(args)


def link_issues(inward_key: str, outward_key: str, link_type: str) -> str:
    """Link two issues together."""
    return run_jira(['issue', 'link', inward_key, outward_key, link_type])


def add_to_epic(epic_key: str, issue_keys: list[str]) -> str:
    """Add issues to an epic."""
    return run_jira(['epic', 'add', epic_key] + issue_keys)


def list_sprints(board_id: int, state: Optional[str] = None) -> str:
    """List sprints for a board."""
    args = ['sprint', 'list', '-b', str(board_id)]
    if state:
        args.extend(['--state', state])
    return run_jira(args)


def main():
    parser = argparse.ArgumentParser(description="Jira CLI wrapper for Claude skills")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Search
    search_parser = subparsers.add_parser("search", help="Search issues using JQL")
    search_parser.add_argument("jql", help="JQL query string")
    search_parser.add_argument("--limit", "-l", type=int, default=50, help="Max results")

    # Get
    get_parser = subparsers.add_parser("get", help="Get issue details")
    get_parser.add_argument("key", help="Issue key (e.g., PROJ-123)")

    # Create
    create_parser = subparsers.add_parser("create", help="Create a new issue")
    create_parser.add_argument("--project", "-p", required=True, help="Project key")
    create_parser.add_argument("--type", "-t", required=True, help="Issue type")
    create_parser.add_argument("--summary", "-s", required=True, help="Issue summary")
    create_parser.add_argument("--description", "-d", help="Issue description")
    create_parser.add_argument("--priority", help="Priority level")
    create_parser.add_argument("--assignee", "-a", help="Assignee username")
    create_parser.add_argument("--labels", "-l", nargs="+", help="Labels")
    create_parser.add_argument("--components", "-C", nargs="+", help="Components")

    # Update
    update_parser = subparsers.add_parser("update", help="Update an issue")
    update_parser.add_argument("key", help="Issue key")
    update_parser.add_argument("--summary", "-s", help="New summary")
    update_parser.add_argument("--description", "-d", help="New description")
    update_parser.add_argument("--priority", help="New priority")
    update_parser.add_argument("--assignee", "-a", help="New assignee")
    update_parser.add_argument("--labels", "-l", nargs="+", help="Labels")
    update_parser.add_argument("--components", "-C", nargs="+", help="Components")

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete an issue")
    delete_parser.add_argument("key", help="Issue key")

    # Comment
    comment_parser = subparsers.add_parser("comment", help="Add a comment")
    comment_parser.add_argument("key", help="Issue key")
    comment_parser.add_argument("body", help="Comment body")

    # Transition
    transition_parser = subparsers.add_parser("transition", help="Transition issue status")
    transition_parser.add_argument("key", help="Issue key")
    transition_parser.add_argument("state", help="Target state")

    # Worklog
    worklog_parser = subparsers.add_parser("worklog", help="Add worklog entry")
    worklog_parser.add_argument("key", help="Issue key")
    worklog_parser.add_argument("--time", "-t", required=True, help="Time spent (e.g., 2h, 30m)")
    worklog_parser.add_argument("--comment", "-c", help="Worklog comment")

    # Link
    link_parser = subparsers.add_parser("link", help="Link two issues")
    link_parser.add_argument("inward_key", help="Inward issue key")
    link_parser.add_argument("outward_key", help="Outward issue key")
    link_parser.add_argument("--type", "-t", default="relates to", help="Link type")

    # Epic add
    epic_parser = subparsers.add_parser("epic-add", help="Add issues to epic")
    epic_parser.add_argument("epic_key", help="Epic key")
    epic_parser.add_argument("issue_keys", nargs="+", help="Issue keys to add")

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
        elif args.command == "create":
            print(create_issue(
                args.project, args.type, args.summary,
                args.description, args.priority, args.assignee,
                args.labels, args.components
            ))
        elif args.command == "update":
            print(update_issue(
                args.key, args.summary, args.description,
                args.priority, args.assignee, args.labels, args.components
            ))
        elif args.command == "delete":
            print(delete_issue(args.key))
        elif args.command == "comment":
            print(add_comment(args.key, args.body))
        elif args.command == "transition":
            print(transition_issue(args.key, args.state))
        elif args.command == "worklog":
            print(add_worklog(args.key, args.time, args.comment))
        elif args.command == "link":
            print(link_issues(args.inward_key, args.outward_key, args.type))
        elif args.command == "epic-add":
            print(add_to_epic(args.epic_key, args.issue_keys))
        elif args.command == "sprints":
            print(list_sprints(args.board, args.state))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
