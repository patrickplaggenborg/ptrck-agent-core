# Figma REST API Reference

Base URL: `https://api.figma.com/v1`

## Authentication

All requests require the `X-Figma-Token` header with a Personal Access Token.

```bash
curl -H "X-Figma-Token: YOUR_TOKEN" https://api.figma.com/v1/files/FILE_KEY
```

### Getting a Token

1. Go to Figma Settings > Account
2. Scroll to "Personal access tokens"
3. Generate a new token with appropriate scopes

### Required Scopes

| Endpoint | Required Scope |
|----------|---------------|
| Files, Nodes, Images | `file_content:read` |
| Styles, Components | `file_content:read` |
| File Metadata | `file_metadata:read` |
| Versions | `file_versions:read` |
| Comments (read) | `file_comments:read` |
| Comments (write) | `file_comments:write` |
| Projects | `projects:read` |
| Dev Resources (read) | `file_dev_resources:read` |
| Dev Resources (write) | `file_dev_resources:write` |
| Variables (Enterprise) | `file_variables:read` |

## Endpoints

### GET /v1/files/:key

Get file metadata and full document tree.

**Parameters:**
- `key` (path) - File key from URL

**Query Parameters:**
- `version` - Specific version ID
- `ids` - Comma-separated node IDs to retrieve
- `depth` - Depth of children to retrieve
- `geometry` - Include geometry data (`paths`)
- `plugin_data` - Include plugin data

**Response:**
```json
{
  "name": "File Name",
  "lastModified": "2025-01-13T10:00:00Z",
  "thumbnailUrl": "https://...",
  "version": "123456789",
  "document": {
    "id": "0:0",
    "name": "Document",
    "type": "DOCUMENT",
    "children": [
      {
        "id": "0:1",
        "name": "Page 1",
        "type": "CANVAS",
        "children": [...]
      }
    ]
  },
  "styles": {...},
  "components": {...}
}
```

### GET /v1/files/:key/nodes

Get specific nodes by ID.

**Parameters:**
- `key` (path) - File key
- `ids` (query, required) - Comma-separated node IDs

**Query Parameters:**
- `version` - Specific version ID
- `depth` - Depth of children to retrieve
- `geometry` - Include geometry data
- `plugin_data` - Include plugin data

**Response:**
```json
{
  "nodes": {
    "1:234": {
      "document": {...},
      "components": {...},
      "styles": {...}
    }
  }
}
```

### GET /v1/images/:key

Render nodes as images.

**Parameters:**
- `key` (path) - File key
- `ids` (query, required) - Comma-separated node IDs

**Query Parameters:**
- `scale` - Scale factor (0.01 to 4, default 1)
- `format` - `jpg`, `png`, `svg`, `pdf` (default `png`)
- `svg_include_id` - Include IDs in SVG
- `svg_include_node_id` - Include node-id attribute in SVG
- `svg_simplify_stroke` - Simplify strokes in SVG
- `use_absolute_bounds` - Use absolute bounds
- `version` - Specific version ID

**Response:**
```json
{
  "images": {
    "1:234": "https://figma-alpha-api.s3.us-west-2.amazonaws.com/images/...",
    "1:235": "https://figma-alpha-api.s3.us-west-2.amazonaws.com/images/..."
  }
}
```

**Notes:**
- Image URLs expire after 30 days
- Maximum image size: 32 megapixels (larger images scaled down)
- `null` values indicate rendering failure

### GET /v1/files/:key/images

Get download URLs for image fills (user-uploaded images).

**Parameters:**
- `key` (path) - File key

**Response:**
```json
{
  "images": {
    "imageRef1": "https://...",
    "imageRef2": "https://..."
  }
}
```

**Notes:**
- URLs expire after 14 days
- These are user-uploaded images, not rendered nodes

### GET /v1/files/:key/styles

Get published styles from file.

**Parameters:**
- `key` (path) - File key

**Response:**
```json
{
  "meta": {
    "styles": [
      {
        "key": "abc123",
        "name": "Primary Blue",
        "style_type": "FILL",
        "description": "Main brand color"
      }
    ]
  }
}
```

**Style Types:**
- `FILL` - Color/gradient styles
- `TEXT` - Typography styles
- `EFFECT` - Shadow/blur effects
- `GRID` - Layout grid styles

### GET /v1/files/:key/components

Get published components from file.

**Parameters:**
- `key` (path) - File key

**Response:**
```json
{
  "meta": {
    "components": [
      {
        "key": "xyz789",
        "name": "Button/Primary",
        "description": "Primary action button",
        "containing_frame": {
          "name": "Components",
          "nodeId": "1:100"
        }
      }
    ]
  }
}
```

### GET /v1/files/:key/comments

Get comments from a file.

**Parameters:**
- `key` (path) - File key

**Query Parameters:**
- `as_md` - Return comments in markdown format

**Response:**
```json
{
  "comments": [
    {
      "id": "123456789",
      "message": "Comment text here",
      "created_at": "2025-01-13T10:00:00Z",
      "resolved_at": null,
      "user": {
        "handle": "user@example.com",
        "img_url": "https://..."
      },
      "client_meta": {
        "node_id": "1:234",
        "node_offset": {"x": 100, "y": 50}
      },
      "order_id": "1"
    }
  ]
}
```

### POST /v1/files/:key/comments

Create a comment on a file.

**Parameters:**
- `key` (path) - File key

**Request Body:**
```json
{
  "message": "Comment text",
  "client_meta": {
    "node_id": "1:234",
    "node_offset": {"x": 100, "y": 50}
  }
}
```

**Notes:**
- `client_meta` is optional
- Can attach comment to a specific node using `node_id`

### DELETE /v1/files/:key/comments/:comment_id

Delete a comment.

**Parameters:**
- `key` (path) - File key
- `comment_id` (path) - Comment ID

**Response:**
- 200 OK on success

### GET /v1/files/:key/versions

Get version history of a file.

**Parameters:**
- `key` (path) - File key

**Response:**
```json
{
  "versions": [
    {
      "id": "123456789",
      "created_at": "2025-01-13T10:00:00Z",
      "label": "Version 1.0",
      "description": "Initial release",
      "user": {
        "handle": "user@example.com",
        "img_url": "https://..."
      }
    }
  ]
}
```

**Notes:**
- Versions are returned in reverse chronological order (newest first)
- Label and description are optional user-defined fields

### GET /v1/teams/:team_id/projects

Get projects for a team.

**Parameters:**
- `team_id` (path) - Team ID

**Response:**
```json
{
  "projects": [
    {
      "id": "123456789",
      "name": "Project Name"
    }
  ]
}
```

**Notes:**
- Requires `projects:read` scope

### GET /v1/projects/:project_id/files

Get files in a project.

**Parameters:**
- `project_id` (path) - Project ID

**Response:**
```json
{
  "files": [
    {
      "key": "ABC123",
      "name": "Design File",
      "thumbnail_url": "https://...",
      "last_modified": "2025-01-13T10:00:00Z"
    }
  ]
}
```

### GET /v1/files/:key/dev_resources

Get dev resources linked to a file.

**Parameters:**
- `key` (path) - File key

**Query Parameters:**
- `node_ids` - Comma-separated node IDs to filter

**Response:**
```json
{
  "dev_resources": [
    {
      "id": "123456789",
      "name": "Documentation",
      "url": "https://docs.example.com/button",
      "file_key": "ABC123",
      "node_id": "1:234"
    }
  ]
}
```

**Notes:**
- Dev resources are links to external documentation, code, or other resources
- Requires `file_dev_resources:read` scope

## Rate Limits

| Tier | Limit |
|------|-------|
| Free | 300 requests/minute |
| Paid | Higher (plan-dependent) |

**Handling Rate Limits:**
- 429 responses include `Retry-After` header
- Implement exponential backoff
- Cache responses to reduce API calls

## Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| 400 | Bad request | Check URL format, node IDs |
| 403 | Forbidden | Verify token, check file permissions |
| 404 | Not found | File key or node ID doesn't exist |
| 429 | Rate limited | Wait for `Retry-After` duration |
| 500 | Server error | Retry with backoff |

## URL Parsing

Figma URLs follow these patterns:

```
https://www.figma.com/file/{file_key}/{file_name}
https://www.figma.com/file/{file_key}/{file_name}?node-id={node_id}
https://www.figma.com/design/{file_key}/{file_name}
https://www.figma.com/design/{file_key}/{file_name}?node-id={node_id}
```

**Examples:**
- Full file: `https://www.figma.com/file/ABC123/MyDesign`
- Specific frame: `https://www.figma.com/file/ABC123/MyDesign?node-id=1-234`

**Note:** URLs use `-` in node IDs, but API uses `:` (e.g., `1-234` → `1:234`)

## Node Types

Common node types in the document tree:

| Type | Description |
|------|-------------|
| `DOCUMENT` | Root node |
| `CANVAS` | Page |
| `FRAME` | Frame/Artboard |
| `GROUP` | Group of nodes |
| `COMPONENT` | Component definition |
| `COMPONENT_SET` | Variant set |
| `INSTANCE` | Component instance |
| `TEXT` | Text layer |
| `RECTANGLE` | Rectangle shape |
| `ELLIPSE` | Ellipse/circle |
| `VECTOR` | Vector path |
| `BOOLEAN_OPERATION` | Boolean operation |

## Resources

- [Official API Documentation](https://www.figma.com/developers/api)
- [OpenAPI Spec](https://github.com/figma/rest-api-spec)
- [Access Tokens](https://www.figma.com/developers/api#access-tokens)

---

## Figma MCP Server Tools

The Figma MCP Server provides additional tools not available via REST API.

### Configuration

Add to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "figma": {
      "url": "https://mcp.figma.com/mcp"
    }
  }
}
```

### Available Tools

#### get_variable_defs

Get variables and styles from a Figma selection. Works on all plans (REST API requires Enterprise).

**Parameters:**
- `figmaUrl` (required) - Figma URL with selection

**Returns:**
- Variables with values, types, and modes
- Published styles (colors, typography, effects)

**Use Case:** Extract design tokens with mode support (light/dark themes)

#### get_design_context

AI-optimized design extraction for code generation.

**Parameters:**
- `figmaUrl` (required) - Figma URL with selection
- Various customization options for framework/styling

**Returns:**
- Simplified design hierarchy
- React + Tailwind code by default
- Responsive layout information

**Use Case:** "Implement this design" workflows

#### get_screenshot

Capture a screenshot of the current selection.

**Parameters:**
- `figmaUrl` (required) - Figma URL with selection

**Returns:**
- PNG image of the selection

#### get_metadata

Get sparse XML representation of selection.

**Parameters:**
- `figmaUrl` (required) - Figma URL with selection

**Returns:**
- XML hierarchy with node IDs and properties

**Use Case:** Understanding layer structure

#### get_figjam

Convert FigJam diagrams to AI-friendly XML with screenshots.

**Parameters:**
- `figmaUrl` (required) - FigJam URL

**Returns:**
- XML representation of FigJam content
- Screenshots of elements

**Use Case:** Extracting FigJam content for AI processing

#### create_design_system_rules

Generate design system rules for AI agents.

**Parameters:**
- `figmaUrl` (required) - Figma URL with design system

**Returns:**
- Rules and patterns for consistent code generation

#### whoami

Get current user info and plan type.

**Returns:**
- User handle and email
- Plan type (Free, Professional, Organization, Enterprise)
- Seat type

### MCP Rate Limits

| Plan | Limit |
|------|-------|
| Free/Starter | 6 tool calls/month |
| Professional+ | Per-minute limits |

### REST API vs MCP Comparison

| Feature | REST API | MCP Server |
|---------|:--------:|:----------:|
| File structure | Yes | Yes |
| Export images | Yes | Yes |
| Design tokens (from tree) | Yes | Yes |
| Comments | Yes | No |
| Versions | Yes | No |
| Projects | Yes | No |
| Dev Resources | Yes | No |
| **Figma Variables** | Enterprise only | **All plans** |
| **AI design context** | No | **Yes** |
| **FigJam extraction** | Limited | **AI-optimized** |
