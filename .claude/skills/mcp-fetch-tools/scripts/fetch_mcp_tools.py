#!/usr/bin/env python3
"""
Fetch tool listings from MCP servers and generate OpenAI-compatible JSON configs.

Usage:
    python3 fetch_mcp_tools.py <mcp-url> [--output-dir <dir>]

Example:
    python3 fetch_mcp_tools.py https://wbmcp.elmar.io/mcp
    python3 fetch_mcp_tools.py https://wbmcp.elmar.io/mcp --output-dir ./my-output/
"""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Error: 'requests' package is required. Install with: pip install requests")
    sys.exit(1)


def url_to_slug(url: str) -> str:
    """Convert URL to snake_case slug for directory naming."""
    parsed = urlparse(url)
    # Combine host and path, remove protocol
    raw = f"{parsed.netloc}{parsed.path}"
    # Replace non-alphanumeric with underscores, collapse multiple underscores
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', raw)
    slug = re.sub(r'_+', '_', slug)
    # Remove leading/trailing underscores
    slug = slug.strip('_')
    return slug.lower()


def mcp_request(url: str, method: str, params: dict = None) -> dict:
    """Send a JSON-RPC request to an MCP server."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1
    }
    if params:
        payload["params"] = params

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    result = response.json()
    if "error" in result:
        raise Exception(f"MCP error: {result['error']}")

    return result.get("result", {})


def fetch_server_info(url: str) -> dict:
    """Fetch server info via initialize method."""
    params = {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "fetch-mcp-tools", "version": "1.0"}
    }
    return mcp_request(url, "initialize", params)


def fetch_tools(url: str) -> list:
    """Fetch tool listings from MCP server."""
    result = mcp_request(url, "tools/list")
    return result.get("tools", [])


def mcp_tool_to_openai(tool: dict) -> dict:
    """Convert MCP tool format to OpenAI tool format."""
    return {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool.get("description", ""),
            "parameters": tool.get("inputSchema", {"type": "object", "properties": {}})
        }
    }


def generate_markdown(url: str, server_info: dict, tools: list) -> str:
    """Generate human-readable markdown documentation."""
    lines = []

    # Header
    server_name = server_info.get("serverInfo", {}).get("name", "Unknown")
    server_version = server_info.get("serverInfo", {}).get("version", "Unknown")
    protocol = server_info.get("protocolVersion", "Unknown")

    lines.append(f"# MCP Server: {server_name}")
    lines.append("")
    lines.append(f"**URL:** {url}")
    lines.append(f"**Version:** {server_version}")
    lines.append(f"**Protocol:** {protocol}")
    lines.append("")

    # Capabilities
    capabilities = server_info.get("capabilities", {})
    if capabilities:
        lines.append("## Server Capabilities")
        lines.append("")
        for cap_name, cap_value in capabilities.items():
            if isinstance(cap_value, dict):
                cap_details = ", ".join(f"{k}: {v}" for k, v in cap_value.items())
                lines.append(f"- **{cap_name}:** {cap_details}")
            else:
                lines.append(f"- **{cap_name}:** {cap_value}")
        lines.append("")

    # Tools
    lines.append("## Tools")
    lines.append("")

    for tool in tools:
        tool_name = tool.get("name", "Unknown")
        description = tool.get("description", "No description")
        input_schema = tool.get("inputSchema", {})
        annotations = tool.get("annotations", {})

        lines.append(f"### {tool_name}")
        lines.append("")
        lines.append(f"**Description:** {description}")
        lines.append("")

        # Annotations
        if annotations:
            lines.append("**Annotations:**")
            lines.append("")
            for ann_key, ann_value in annotations.items():
                lines.append(f"- {ann_key}: `{ann_value}`")
            lines.append("")

        # Parameters table
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])

        if properties:
            lines.append("**Parameters:**")
            lines.append("")
            lines.append("| Name | Type | Required | Default | Description |")
            lines.append("|------|------|----------|---------|-------------|")

            for prop_name, prop_def in properties.items():
                prop_type = prop_def.get("type", "any")
                # Handle array types with items
                if prop_type == "array" and "items" in prop_def:
                    items = prop_def["items"]
                    if "enum" in items:
                        prop_type = f"array[enum]"
                    else:
                        prop_type = f"array[{items.get('type', 'any')}]"
                # Handle enums
                elif "enum" in prop_def:
                    prop_type = "enum"

                is_required = "yes" if prop_name in required else "no"
                default = prop_def.get("default", "-")
                if default != "-":
                    default = f"`{default}`"
                prop_desc = prop_def.get("description", "-")
                # Escape pipes in description
                prop_desc = prop_desc.replace("|", "\\|")

                lines.append(f"| {prop_name} | {prop_type} | {is_required} | {default} | {prop_desc} |")

            lines.append("")

        # Full JSON schema
        openai_tool = mcp_tool_to_openai(tool)
        lines.append("**Full JSON Schema (OpenAI format):**")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(openai_tool, indent=2))
        lines.append("```")
        lines.append("")

        # Include raw MCP tool definition for reference
        lines.append("<details>")
        lines.append("<summary>Raw MCP Tool Definition</summary>")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(tool, indent=2))
        lines.append("```")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch tool listings from MCP servers and generate configs"
    )
    parser.add_argument("url", help="MCP server URL")
    parser.add_argument(
        "--output-dir",
        default="mcp-tools",
        help="Output directory (default: mcp-tools)"
    )

    args = parser.parse_args()

    url = args.url
    output_base = Path(args.output_dir)

    print(f"Fetching MCP tools from: {url}")
    print()

    # Fetch server info
    print("Fetching server info...")
    try:
        server_info = fetch_server_info(url)
        server_name = server_info.get("serverInfo", {}).get("name", "Unknown")
        server_version = server_info.get("serverInfo", {}).get("version", "Unknown")
        print(f"  Server: {server_name} v{server_version}")
    except Exception as e:
        print(f"  Warning: Could not fetch server info: {e}")
        server_info = {}

    # Fetch tools
    print("Fetching tools...")
    tools = fetch_tools(url)
    print(f"  Found {len(tools)} tool(s)")

    if not tools:
        print("\nNo tools found on this MCP server.")
        return

    # Create output directory
    url_slug = url_to_slug(url)
    output_dir = output_base / url_slug
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate OpenAI-compatible tools.json
    openai_tools = [mcp_tool_to_openai(tool) for tool in tools]
    tools_json_path = output_dir / "tools.json"
    with open(tools_json_path, "w") as f:
        json.dump(openai_tools, f, indent=2)
    print(f"\nGenerated: {tools_json_path}")

    # Generate markdown documentation
    markdown = generate_markdown(url, server_info, tools)
    md_path = output_dir / "tool-config.md"
    with open(md_path, "w") as f:
        f.write(markdown)
    print(f"Generated: {md_path}")

    print(f"\nDone! Output saved to: {output_dir}")


if __name__ == "__main__":
    main()
