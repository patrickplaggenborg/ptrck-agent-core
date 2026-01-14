#!/usr/bin/env python3
"""
Confluence API wrapper for Claude skills.
Uses Confluence REST API v2 for pages, v1 for search and spaces.
"""

import argparse
import base64
import json
import os
import sys
from typing import Optional
from urllib.parse import quote

import requests


def get_auth_header() -> dict:
    """Create authorization header for API requests."""
    email = os.environ.get('CONFLUENCE_EMAIL')
    token = os.environ.get('CONFLUENCE_API_TOKEN')

    if not email or not token:
        raise ValueError("CONFLUENCE_EMAIL and CONFLUENCE_API_TOKEN are required")

    credentials = base64.b64encode(f"{email}:{token}".encode()).decode()
    return {"Authorization": f"Basic {credentials}", "Content-Type": "application/json"}


def get_base_url() -> str:
    """Get the base URL for API requests."""
    cloud_id = os.environ.get('CONFLUENCE_CLOUD_ID')
    if not cloud_id:
        raise ValueError("CONFLUENCE_CLOUD_ID is required")
    return f"https://api.atlassian.com/ex/confluence/{cloud_id}/wiki/api/v2"


def format_response(data) -> str:
    """Format response as JSON."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_error(message: str) -> str:
    """Format error as JSON."""
    return json.dumps({"error": message}, ensure_ascii=False, indent=2)


def handle_response(response: requests.Response) -> dict:
    """Handle API response and raise errors if needed."""
    if response.status_code >= 400:
        try:
            error_data = response.json()
            message = error_data.get("message", response.text)
        except Exception:
            message = response.text
        raise Exception(f"{response.status_code}: {message}")
    return response.json() if response.text else {}


# Commands

def test_connection() -> str:
    """Test connection by fetching pages list."""
    try:
        base_url = get_base_url()
        headers = get_auth_header()
        response = requests.get(f"{base_url}/pages?limit=1", headers=headers)
        handle_response(response)
        cloud_id = os.environ.get('CONFLUENCE_CLOUD_ID', 'not set')
        return format_response({
            "success": True,
            "api_version": "v2",
            "endpoint": f"api.atlassian.com/ex/confluence/{cloud_id}"
        })
    except Exception as e:
        return format_error(str(e))


def search_pages(query: str, space: Optional[str] = None, limit: int = 25) -> str:
    """Search for pages using CQL (Confluence Query Language)."""
    try:
        cloud_id = os.environ.get('CONFLUENCE_CLOUD_ID')
        if not cloud_id:
            raise ValueError("CONFLUENCE_CLOUD_ID is required")

        # Use v1 search API with CQL (works with search:confluence scope)
        search_url = f"https://api.atlassian.com/ex/confluence/{cloud_id}/wiki/rest/api/search"
        headers = get_auth_header()

        # Build CQL query
        cql = f'title~"{query}" AND type=page'
        if space:
            cql += f' AND space="{space}"'

        params = {"cql": cql, "limit": limit}
        response = requests.get(search_url, headers=headers, params=params)
        data = handle_response(response)

        pages = []
        for result in data.get("results", []):
            content = result.get("content", {})
            if content.get("type") == "page":
                pages.append({
                    "id": content.get("id"),
                    "title": content.get("title"),
                    "status": content.get("status"),
                    "space": result.get("resultGlobalContainer", {}).get("title"),
                    "_links": {
                        "webui": content.get("_links", {}).get("webui"),
                    }
                })
        return format_response({"total": len(pages), "pages": pages})
    except Exception as e:
        return format_error(str(e))


def get_page(page_id: str) -> str:
    """Get page content by ID."""
    try:
        base_url = get_base_url()
        headers = get_auth_header()

        response = requests.get(
            f"{base_url}/pages/{page_id}?body-format=storage",
            headers=headers
        )
        page = handle_response(response)

        return format_response({
            "id": page.get("id"),
            "title": page.get("title"),
            "status": page.get("status"),
            "spaceId": page.get("spaceId"),
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
        base_url = get_base_url()
        headers = get_auth_header()

        # Get space ID from space key
        space_response = requests.get(f"{base_url}/spaces?keys={space}", headers=headers)
        space_data = handle_response(space_response)
        if not space_data.get("results"):
            raise Exception(f"Space '{space}' not found")
        space_id = space_data["results"][0]["id"]

        body = {
            "spaceId": space_id,
            "status": "current",
            "title": title,
            "body": {
                "representation": "storage",
                "value": content
            }
        }

        if parent_id:
            body["parentId"] = parent_id

        response = requests.post(f"{base_url}/pages", headers=headers, json=body)
        result = handle_response(response)

        return format_response({
            "success": True,
            "id": result.get("id"),
            "title": result.get("title"),
            "spaceId": result.get("spaceId"),
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
        base_url = get_base_url()
        headers = get_auth_header()

        # Get current page to get version and current values
        current_response = requests.get(
            f"{base_url}/pages/{page_id}?body-format=storage",
            headers=headers
        )
        current = handle_response(current_response)

        new_title = title if title else current.get("title")
        new_content = content if content else current.get("body", {}).get("storage", {}).get("value", "")
        current_version = current.get("version", {}).get("number", 1)

        body = {
            "id": page_id,
            "status": "current",
            "title": new_title,
            "body": {
                "representation": "storage",
                "value": new_content
            },
            "version": {
                "number": current_version + 1
            }
        }

        response = requests.put(f"{base_url}/pages/{page_id}", headers=headers, json=body)
        result = handle_response(response)

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
        base_url = get_base_url()
        headers = get_auth_header()

        response = requests.delete(f"{base_url}/pages/{page_id}", headers=headers)
        if response.status_code == 204:
            return format_response({"success": True, "id": page_id, "deleted": True})
        handle_response(response)
        return format_response({"success": True, "id": page_id, "deleted": True})
    except Exception as e:
        return format_error(str(e))


def list_spaces() -> str:
    """List all available spaces."""
    try:
        cloud_id = os.environ.get('CONFLUENCE_CLOUD_ID')
        if not cloud_id:
            raise ValueError("CONFLUENCE_CLOUD_ID is required")

        # Use v1 space API (works with read:confluence-space.summary scope)
        space_url = f"https://api.atlassian.com/ex/confluence/{cloud_id}/wiki/rest/api/space"
        headers = get_auth_header()

        response = requests.get(f"{space_url}?limit=250", headers=headers)
        data = handle_response(response)

        result = []
        for space in data.get("results", []):
            result.append({
                "id": space.get("id"),
                "key": space.get("key"),
                "name": space.get("name"),
                "type": space.get("type"),
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
