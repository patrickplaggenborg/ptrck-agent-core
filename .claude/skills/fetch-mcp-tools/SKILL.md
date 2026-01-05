---
name: fetch-mcp-tools
description: Fetch tool listings from MCP servers and generate OpenAI-compatible JSON configs. This skill should be used when needing to discover tools available on an MCP server, export MCP tools for use in Braintrust or other platforms, or document an MCP server's capabilities.
---

# Fetch MCP Tools

## Overview

This skill fetches tool definitions from MCP (Model Context Protocol) servers via HTTP and generates both human-readable documentation and OpenAI-compatible JSON tool configurations.

## When to Use

- Discovering what tools an MCP server provides
- Generating JSON tool configs for Braintrust (which accepts OpenAI tool format)
- Documenting an MCP server's capabilities
- Comparing tools between different MCP server environments (prod vs staging)

## Usage

Run the script with an MCP server URL:

```bash
python3 .claude/skills/fetch-mcp-tools/scripts/fetch_mcp_tools.py <mcp-url>
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `url` | Yes | The MCP server URL (e.g., `https://wbmcp.elmar.io/mcp`) |
| `--output-dir` | No | Output directory (default: `mcp-tools/`) |

### Output

The script creates a subdirectory based on the URL slug and generates two files:

```
mcp-tools/
└── wbmcp_elmar_io_mcp/
    ├── tool-config.md    # Human-readable documentation with full JSON
    └── tools.json        # OpenAI-compatible tool definitions
```

**URL Slug Format:** The URL is converted to snake_case (e.g., `https://wbmcp.elmar.io/mcp` → `wbmcp_elmar_io_mcp`). This ensures stable directory names even if the MCP server name changes.

### Example

```bash
# Fetch tools from an MCP server
python3 .claude/skills/fetch-mcp-tools/scripts/fetch_mcp_tools.py https://wbmcp.elmar.io/mcp

# Specify custom output directory
python3 .claude/skills/fetch-mcp-tools/scripts/fetch_mcp_tools.py https://wbmcp.elmar.io/mcp --output-dir ./my-output/
```

## Output Formats

### tool-config.md

Complete human-readable documentation including:
- Server metadata (name, version, protocol, URL)
- Server capabilities
- For each tool:
  - Description and annotations
  - Parameters table (name, type, required, description)
  - Full JSON schema embedded in code block

### tools.json

OpenAI-compatible tool array ready for use in Braintrust or any OpenAI-compatible platform:

```json
[
  {
    "type": "function",
    "function": {
      "name": "tool_name",
      "description": "Tool description",
      "parameters": { ... }
    }
  }
]
```

## Technical Details

MCP servers communicate via JSON-RPC over HTTP POST. The script:

1. Sends `initialize` request to get server info
2. Sends `tools/list` request to get tool definitions
3. Transforms MCP tool format to OpenAI tool format
4. Generates both output files

Required headers for MCP servers:
- `Content-Type: application/json`
- `Accept: application/json, text/event-stream`
