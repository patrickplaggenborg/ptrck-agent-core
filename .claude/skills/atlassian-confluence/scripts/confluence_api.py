#!/usr/bin/env python3
"""
Confluence API wrapper for Claude skills.
Uses atlassian-python-api with support for scoped API tokens.
"""

import argparse
import json
import os
import sys
from typing import Optional

from atlassian import Confluence


def get_confluence_client() -> Confluence:
    """Create Confluence client with appropriate URL based on token type."""
    email = os.environ.get('ATLASSIAN_EMAIL')
    token = os.environ.get('ATLASSIAN_API_TOKEN')
    cloud_id = os.environ.get('ATLASSIAN_CLOUD_ID')
    use_scoped = os.environ.get('ATLASSIAN_USE_SCOPED_TOKEN', '').lower() == 'true'

    if not email or not token:
        raise ValueError("ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN are required")

    if use_scoped and cloud_id:
        # Scoped token - use api.atlassian.com
        url = f"https://api.atlassian.com/ex/confluence/{cloud_id}"
    else:
        # Classic token - use site URL with /wiki suffix
        base_url = os.environ.get('ATLASSIAN_URL')
        if not base_url:
            raise ValueError("ATLASSIAN_URL is required for classic tokens")
        url = f"{base_url.rstrip('/')}/wiki"

    return Confluence(url=url, username=email, password=token)


def get_token_type() -> str:
    """Return description of token type being used."""
    cloud_id = os.environ.get('ATLASSIAN_CLOUD_ID')
    use_scoped = os.environ.get('ATLASSIAN_USE_SCOPED_TOKEN', '').lower() == 'true'

    if use_scoped and cloud_id:
        return f"scoped (api.atlassian.com/ex/confluence/{cloud_id})"
    else:
        url = os.environ.get('ATLASSIAN_URL', 'not set')
        return f"classic ({url}/wiki)"


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
        confluence = get_confluence_client()
        # Get current user info
        user = confluence.get_current_user()
        return format_response({
            "success": True,
            "token_type": get_token_type(),
            "user": {
                "displayName": user.get("displayName"),
                "email": user.get("email"),
                "accountId": user.get("accountId"),
            }
        })
    except Exception as e:
        return format_error(str(e))


def search_pages(query: str, space: Optional[str] = None, limit: int = 25) -> str:
    """Search for pages."""
    try:
        confluence = get_confluence_client()
        cql = f'text ~ "{query}"'
        if space:
            cql += f' AND space = "{space}"'

        results = confluence.cql(cql, limit=limit)
        pages = []
        for result in results.get("results", []):
            content = result.get("content", result)
            pages.append({
                "id": content.get("id"),
                "title": content.get("title"),
                "type": content.get("type"),
                "space": content.get("space", {}).get("key") if content.get("space") else None,
                "_links": {
                    "webui": content.get("_links", {}).get("webui"),
                }
            })
        return format_response({"total": results.get("totalSize", len(pages)), "pages": pages})
    except Exception as e:
        return format_error(str(e))


def get_page(page_id: str) -> str:
    """Get page content by ID."""
    try:
        confluence = get_confluence_client()
        page = confluence.get_page_by_id(page_id, expand="body.storage,version,space")
        return format_response({
            "id": page.get("id"),
            "title": page.get("title"),
            "type": page.get("type"),
            "space": page.get("space", {}).get("key") if page.get("space") else None,
            "version": page.get("version", {}).get("number"),
            "body": page.get("body", {}).get("storage", {}).get("value"),
            "_links": {
                "webui": page.get("_links", {}).get("webui"),
            }
        })
    except Exception as e:
        return format_error(str(e))


def create_page(
    space: str,
    title: str,
    content: str,
    parent_id: Optional[str] = None
) -> str:
    """Create a new page."""
    try:
        confluence = get_confluence_client()
        result = confluence.create_page(
            space=space,
            title=title,
            body=content,
            parent_id=parent_id
        )
        return format_response({
            "success": True,
            "id": result.get("id"),
            "title": result.get("title"),
            "space": space,
            "_links": {
                "webui": result.get("_links", {}).get("webui"),
            }
        })
    except Exception as e:
        return format_error(str(e))


def update_page(
    page_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None
) -> str:
    """Update an existing page."""
    try:
        confluence = get_confluence_client()

        # Get current page to get version and current values
        current = confluence.get_page_by_id(page_id, expand="body.storage,version")

        new_title = title if title else current.get("title")
        new_content = content if content else current.get("body", {}).get("storage", {}).get("value", "")

        result = confluence.update_page(
            page_id=page_id,
            title=new_title,
            body=new_content
        )
        return format_response({
            "success": True,
            "id": result.get("id"),
            "title": result.get("title"),
            "version": result.get("version", {}).get("number"),
        })
    except Exception as e:
        return format_error(str(e))


def delete_page(page_id: str) -> str:
    """Delete a page."""
    try:
        confluence = get_confluence_client()
        confluence.remove_page(page_id)
        return format_response({"success": True, "id": page_id, "deleted": True})
    except Exception as e:
        return format_error(str(e))


def list_spaces() -> str:
    """List all available spaces."""
    try:
        confluence = get_confluence_client()
        spaces = confluence.get_all_spaces(expand="description.plain")
        result = []
        for space in spaces.get("results", []):
            result.append({
                "key": space.get("key"),
                "name": space.get("name"),
                "type": space.get("type"),
                "description": space.get("description", {}).get("plain", {}).get("value") if space.get("description") else None,
            })
        return format_response({"spaces": result})
    except Exception as e:
        return format_error(str(e))


def main():
    parser = argparse.ArgumentParser(description="Confluence API wrapper for Claude skills")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Test
    subparsers.add_parser("test", help="Test connection")

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
    create_parser.add_argument("--content", "-c", required=True, help="Page content (HTML or storage format)")
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
        if args.command == "test":
            print(test_connection())
        elif args.command == "search":
            print(search_pages(args.query, args.space, args.limit))
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
        print(format_error(str(e)))
        sys.exit(1)


if __name__ == "__main__":
    main()
