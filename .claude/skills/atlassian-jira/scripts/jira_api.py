#!/usr/bin/env python3
"""
Jira API wrapper for Claude skills.
Uses atlassian-python-api with support for scoped API tokens.
"""

import argparse
import json
import os
import sys
from typing import Optional

from atlassian import Jira


def get_jira_client() -> Jira:
    """Create Jira client using JIRA_* environment variables."""
    email = os.environ.get('JIRA_EMAIL')
    token = os.environ.get('JIRA_API_TOKEN')
    cloud_id = os.environ.get('JIRA_CLOUD_ID')

    if not email or not token:
        raise ValueError("JIRA_EMAIL and JIRA_API_TOKEN are required")

    if not cloud_id:
        raise ValueError("JIRA_CLOUD_ID is required")

    url = f"https://api.atlassian.com/ex/jira/{cloud_id}"
    return Jira(url=url, username=email, password=token)


def get_token_type() -> str:
    """Return description of token type being used."""
    cloud_id = os.environ.get('JIRA_CLOUD_ID', 'not set')
    return f"scoped (api.atlassian.com/ex/jira/{cloud_id})"


def format_response(data) -> str:
    """Format response as JSON."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_error(message: str) -> str:
    """Format error as JSON."""
    return json.dumps({"error": message}, ensure_ascii=False, indent=2)


# Commands

def test_connection() -> str:
    """Test connection and show token info."""
    try:
        jira = get_jira_client()
        myself = jira.myself()
        return format_response({
            "success": True,
            "token_type": get_token_type(),
            "user": {
                "displayName": myself.get("displayName"),
                "emailAddress": myself.get("emailAddress"),
                "accountId": myself.get("accountId"),
            }
        })
    except Exception as e:
        return format_error(str(e))


def search_issues(jql: str, limit: int = 50) -> str:
    """Search issues using JQL."""
    try:
        jira = get_jira_client()
        results = jira.jql(jql, limit=limit)
        issues = []
        for issue in results.get("issues", []):
            fields = issue.get("fields", {})
            issues.append({
                "key": issue.get("key"),
                "summary": fields.get("summary"),
                "status": fields.get("status", {}).get("name") if fields.get("status") else None,
                "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
                "issuetype": fields.get("issuetype", {}).get("name") if fields.get("issuetype") else None,
            })
        return format_response({"total": results.get("total", 0), "issues": issues})
    except Exception as e:
        return format_error(str(e))


def get_issue(key: str) -> str:
    """Get issue details by key."""
    try:
        jira = get_jira_client()
        issue = jira.issue(key)
        fields = issue.get("fields", {})
        return format_response({
            "key": issue.get("key"),
            "summary": fields.get("summary"),
            "description": fields.get("description"),
            "status": fields.get("status", {}).get("name") if fields.get("status") else None,
            "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
            "reporter": fields.get("reporter", {}).get("displayName") if fields.get("reporter") else None,
            "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
            "issuetype": fields.get("issuetype", {}).get("name") if fields.get("issuetype") else None,
            "created": fields.get("created"),
            "updated": fields.get("updated"),
            "labels": fields.get("labels", []),
            "components": [c.get("name") for c in fields.get("components", [])],
        })
    except Exception as e:
        return format_error(str(e))


def create_issue(
    project: str,
    issue_type: str,
    summary: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    labels: Optional[list] = None,
    components: Optional[list] = None
) -> str:
    """Create a new issue."""
    try:
        jira = get_jira_client()
        fields = {
            "project": {"key": project},
            "issuetype": {"name": issue_type},
            "summary": summary,
        }
        if description:
            fields["description"] = description
        if priority:
            fields["priority"] = {"name": priority}
        if assignee:
            fields["assignee"] = {"name": assignee}
        if labels:
            fields["labels"] = labels
        if components:
            fields["components"] = [{"name": c} for c in components]

        result = jira.create_issue(fields=fields)
        return format_response({
            "success": True,
            "key": result.get("key"),
            "id": result.get("id"),
            "self": result.get("self"),
        })
    except Exception as e:
        return format_error(str(e))


def update_issue(
    key: str,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    labels: Optional[list] = None,
    components: Optional[list] = None
) -> str:
    """Update an existing issue."""
    try:
        jira = get_jira_client()
        fields = {}
        if summary:
            fields["summary"] = summary
        if description:
            fields["description"] = description
        if priority:
            fields["priority"] = {"name": priority}
        if assignee:
            fields["assignee"] = {"name": assignee}
        if labels:
            fields["labels"] = labels
        if components:
            fields["components"] = [{"name": c} for c in components]

        if not fields:
            return format_error("No update fields provided")

        jira.update_issue_field(key, fields)
        return format_response({"success": True, "key": key})
    except Exception as e:
        return format_error(str(e))


def delete_issue(key: str) -> str:
    """Delete an issue."""
    try:
        jira = get_jira_client()
        jira.delete_issue(key)
        return format_response({"success": True, "key": key, "deleted": True})
    except Exception as e:
        return format_error(str(e))


def add_comment(key: str, body: str) -> str:
    """Add a comment to an issue."""
    try:
        jira = get_jira_client()
        result = jira.issue_add_comment(key, body)
        return format_response({
            "success": True,
            "key": key,
            "comment_id": result.get("id"),
        })
    except Exception as e:
        return format_error(str(e))


def transition_issue(key: str, state: str) -> str:
    """Transition an issue to a new state."""
    try:
        jira = get_jira_client()
        # Get available transitions
        transitions = jira.get_issue_transitions(key)
        target_transition = None
        for t in transitions:
            if t.get("name", "").lower() == state.lower():
                target_transition = t
                break

        if not target_transition:
            available = [t.get("name") for t in transitions]
            return format_error(f"Transition '{state}' not found. Available: {available}")

        jira.set_issue_status(key, target_transition["name"])
        return format_response({"success": True, "key": key, "status": state})
    except Exception as e:
        return format_error(str(e))


def add_worklog(key: str, time_spent: str, comment: Optional[str] = None) -> str:
    """Add a worklog entry to an issue."""
    try:
        jira = get_jira_client()
        result = jira.issue_worklog(key, timeSpent=time_spent, comment=comment)
        return format_response({
            "success": True,
            "key": key,
            "worklog_id": result.get("id"),
            "time_spent": time_spent,
        })
    except Exception as e:
        return format_error(str(e))


def link_issues(inward_key: str, outward_key: str, link_type: str = "relates to") -> str:
    """Link two issues together."""
    try:
        jira = get_jira_client()
        jira.create_issue_link(
            type=link_type,
            inwardIssue=inward_key,
            outwardIssue=outward_key
        )
        return format_response({
            "success": True,
            "inward_key": inward_key,
            "outward_key": outward_key,
            "link_type": link_type,
        })
    except Exception as e:
        return format_error(str(e))


def add_to_epic(epic_key: str, issue_keys: list) -> str:
    """Add issues to an epic."""
    try:
        jira = get_jira_client()
        # The epic link field name varies by instance
        for issue_key in issue_keys:
            jira.update_issue_field(issue_key, {"parent": {"key": epic_key}})
        return format_response({
            "success": True,
            "epic_key": epic_key,
            "issues_added": issue_keys,
        })
    except Exception as e:
        return format_error(str(e))


def list_sprints(board_id: int, state: Optional[str] = None) -> str:
    """List sprints for a board."""
    try:
        jira = get_jira_client()
        sprints = jira.get_all_sprints_from_board(board_id, state=state)
        result = []
        for sprint in sprints:
            result.append({
                "id": sprint.get("id"),
                "name": sprint.get("name"),
                "state": sprint.get("state"),
                "startDate": sprint.get("startDate"),
                "endDate": sprint.get("endDate"),
            })
        return format_response({"sprints": result})
    except Exception as e:
        return format_error(str(e))


def main():
    parser = argparse.ArgumentParser(description="Jira API wrapper for Claude skills")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Test
    subparsers.add_parser("test", help="Test connection")

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
    sprint_parser.add_argument("--state", "-s", help="Sprint state filter (active, future, closed)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "test":
            print(test_connection())
        elif args.command == "search":
            print(search_issues(args.jql, args.limit))
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
        print(format_error(str(e)))
        sys.exit(1)


if __name__ == "__main__":
    main()
