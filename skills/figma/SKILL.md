---
name: figma
description: Extract design assets and metadata from Figma using the REST API. Supports
  exporting frames as images (PNG/SVG/PDF), extracting file structure, design tokens
  (colors, typography, effects, spacing), published components, comments, versions,
  projects, and dev resources. Optionally integrates with Figma MCP Server for variables
  and AI-optimized design context. This skill should be used when users mention Figma
  URLs, request design-to-code workflows, need design tokens/variables extracted, or
  want to analyze a Figma file for implementation.
---

# Figma Skill

Extract design assets, structure, and tokens from Figma files. Uses REST API for most operations and optionally MCP Server for Figma Variables.

## When to Use

This skill activates when:
- User provides a Figma URL
- User asks to "implement this design" or "convert design to code"
- User needs design tokens (colors, fonts, spacing)
- User wants to export frames as images
- User asks about component structure in a Figma file
- User asks about comments or version history on a Figma file
- User needs to list team projects or dev resources
- User asks for "Figma variables" or "design tokens with modes" (requires MCP)

## Prerequisites

### 1. Figma Access Token

Obtain a Personal Access Token from Figma:
1. Go to Figma Settings > Account
2. Scroll to "Personal access tokens"
3. Generate a new token

Set the token via environment variable:
```bash
export FIGMA_ACCESS_TOKEN="your-token"
```

Or create a `.env` file (checked in order):
1. `~/.claude/skills/figma/.env`
2. `~/.claude/skills/.env`
3. `~/.claude/.env`
4. Current directory `.env`

### 2. Python Dependencies

```bash
pip install requests python-dotenv
```

## Quick Start

### Full Analysis (Recommended Starting Point)

For comprehensive design extraction, use `analyze`:

```bash
python scripts/figma_api.py analyze \
  --url "https://www.figma.com/file/ABC123/MyDesign" \
  --output-dir ./figma-export/
```

This creates:
- `structure.json` - File hierarchy and frame dimensions
- `tokens.json` - Colors, typography, effects, spacing
- `summary.json` - Quick overview for AI consumption
- `thumbnails/` - Preview images of frames

### Export Specific Frame

```bash
python scripts/figma_api.py export \
  --url "https://www.figma.com/file/ABC123/MyDesign?node-id=1-234" \
  --output hero-section.png \
  --scale 2
```

### Get File Structure

```bash
python scripts/figma_api.py structure \
  --url "https://www.figma.com/file/ABC123/MyDesign" \
  --output structure.json
```

### Extract Design Tokens

```bash
python scripts/figma_api.py tokens \
  --url "https://www.figma.com/file/ABC123/MyDesign" \
  --output tokens.json
```

## Commands Reference

### `export`

Export frames/nodes as images.

```bash
python scripts/figma_api.py export --url URL [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | Figma file or frame URL | Required |
| `--output`, `-o` | Output path (file or directory) | `output` |
| `--scale` | Export scale (1, 2, 3, 4) | `2` |
| `--format`, `-f` | Format (png, jpg, svg, pdf) | `png` |
| `--node-ids` | Comma-separated node IDs | From URL |
| `--no-cache` | Bypass local cache | `false` |

**Examples:**
```bash
# Export single frame from URL
python scripts/figma_api.py export \
  --url "https://figma.com/file/ABC/Design?node-id=1-234" \
  --output frame.png

# Export multiple frames
python scripts/figma_api.py export \
  --url "https://figma.com/file/ABC/Design" \
  --node-ids "1-234,1-235,1-236" \
  --output ./frames/

# Export as SVG at 1x
python scripts/figma_api.py export \
  --url "https://figma.com/file/ABC/Design?node-id=1-234" \
  --format svg --scale 1 \
  --output icon.svg
```

### `structure`

Get file/node structure as AI-optimized JSON.

```bash
python scripts/figma_api.py structure --url URL [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | Figma file URL | Required |
| `--output`, `-o` | Output JSON file | `structure.json` |
| `--depth` | Max depth for node tree | `5` |
| `--no-cache` | Bypass local cache | `false` |

**Output includes:**
- File metadata (name, lastModified)
- Page hierarchy
- Frame dimensions and layout properties
- Text content and styles
- Component references

### `tokens`

Extract design tokens from the file.

```bash
python scripts/figma_api.py tokens --url URL [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | Figma file URL | Required |
| `--output`, `-o` | Output JSON file | `tokens.json` |
| `--no-cache` | Bypass local cache | `false` |

**Extracts:**
- **Colors** - All solid fills with hex, RGB, opacity
- **Typography** - Font families, sizes, weights, line heights
- **Effects** - Drop shadows, blurs with full properties
- **Spacing** - Auto-layout gaps and padding values

### `components`

List published components and styles.

```bash
python scripts/figma_api.py components --url URL [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | Figma file URL | Required |
| `--output`, `-o` | Output JSON file | `components.json` |

**Lists:**
- Published components with descriptions
- Color styles
- Typography styles
- Effect styles
- Grid styles

### `analyze`

Full analysis combining structure, tokens, and thumbnails.

```bash
python scripts/figma_api.py analyze --url URL [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | Figma file URL | Required |
| `--output-dir`, `-o` | Output directory | `figma-export` |
| `--no-cache` | Bypass local cache | `false` |
| `--no-images` | Skip thumbnail export | `false` |

**Creates:**
```
figma-export/
├── structure.json    # File hierarchy
├── tokens.json       # Design tokens
├── summary.json      # Quick overview
└── thumbnails/       # Frame previews
    ├── 1-234.png
    └── 1-235.png
```

### `comments`

Get comments from a Figma file.

```bash
python scripts/figma_api.py comments --url URL [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | Figma file URL | Required |
| `--output`, `-o` | Output JSON file | `comments.json` |

**Output includes:**
- Comment ID, message, author
- Creation and resolution timestamps
- Node references (if comment is anchored)

### `comment-add`

Add a comment to a Figma file.

```bash
python scripts/figma_api.py comment-add --url URL --message TEXT [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | Figma file URL | Required |
| `--message`, `-m` | Comment message | Required |
| `--node-id` | Node ID to attach comment | From URL |

### `comment-delete`

Delete a comment from a Figma file.

```bash
python scripts/figma_api.py comment-delete --url URL --comment-id ID
```

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | Figma file URL | Required |
| `--comment-id` | Comment ID to delete | Required |

### `versions`

Get version history of a Figma file.

```bash
python scripts/figma_api.py versions --url URL [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | Figma file URL | Required |
| `--output`, `-o` | Output JSON file | `versions.json` |

**Output includes:**
- Version ID and timestamp
- Label and description (if set)
- User who created the version

### `projects`

List team projects.

```bash
python scripts/figma_api.py projects --team-id ID [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--team-id` | Figma team ID | Required |
| `--output`, `-o` | Output JSON file | `projects.json` |

### `project-files`

List files in a project.

```bash
python scripts/figma_api.py project-files --project-id ID [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--project-id` | Figma project ID | Required |
| `--output`, `-o` | Output JSON file | `project_files.json` |

### `dev-resources`

Get dev resources linked to a Figma file.

```bash
python scripts/figma_api.py dev-resources --url URL [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | Figma file URL | Required |
| `--node-ids` | Comma-separated node IDs | From URL |
| `--output`, `-o` | Output JSON file | `dev_resources.json` |

**Output includes:**
- Resource ID, name, URL
- File key and node ID references

## Design-to-Code Workflow

### Step 1: Analyze the Design

```bash
python scripts/figma_api.py analyze \
  --url "https://figma.com/file/ABC/Design" \
  --output-dir ./design-export/
```

### Step 2: Review the Output

Read the generated files:
- `summary.json` - Quick overview of what's in the design
- `structure.json` - Component hierarchy to understand layout
- `tokens.json` - Design values to use in code

### Step 3: Export High-Resolution Images

For frames that need visual reference:

```bash
python scripts/figma_api.py export \
  --url "https://figma.com/file/ABC/Design?node-id=1-234" \
  --output hero.png --scale 2
```

### Step 4: Generate Code

Use the extracted data to inform code generation:
- Use colors from `tokens.json` for CSS variables
- Use typography for font stacks
- Use structure to understand component hierarchy
- Use images as visual reference

## Output Formats

### Structure JSON

```json
{
  "file": {
    "key": "ABC123",
    "name": "My Design",
    "lastModified": "2025-01-13T10:00:00Z"
  },
  "pages": [
    {
      "id": "0:1",
      "name": "Page 1",
      "frames": [
        {
          "id": "1:234",
          "name": "Hero Section",
          "type": "FRAME",
          "width": 1440,
          "height": 800,
          "layout": {
            "mode": "VERTICAL",
            "direction": "vertical",
            "gap": 24,
            "padding": {"top": 48, "right": 64, "bottom": 48, "left": 64}
          },
          "children": [...]
        }
      ]
    }
  ]
}
```

### Tokens JSON

```json
{
  "colors": {
    "#3b82f6": {
      "hex": "#3b82f6",
      "rgb": [59, 130, 246],
      "opacity": 1,
      "usedIn": ["Button", "Link"]
    }
  },
  "typography": {
    "Inter/700/48": {
      "fontFamily": "Inter",
      "fontSize": 48,
      "fontWeight": 700,
      "lineHeight": 57.6,
      "letterSpacing": -0.5,
      "usedIn": ["Hero Title"]
    }
  },
  "effects": {
    "DROP_SHADOW/6": {
      "type": "DROP_SHADOW",
      "color": "rgba(0, 0, 0, 0.10)",
      "offset": {"x": 0, "y": 4},
      "radius": 6,
      "spread": 0
    }
  },
  "spacing": [4, 8, 12, 16, 24, 32, 48, 64]
}
```

## Caching

The script caches API responses locally at `~/.cache/figma-skill/` with a 1-hour TTL.

- **Benefit**: Reduces API calls, faster repeated access
- **Bypass**: Use `--no-cache` flag when design has changed
- **Clear**: Delete files in `~/.cache/figma-skill/`

## Rate Limits

Figma API allows 300 requests/minute on free tier.

The script handles rate limits automatically:
- Respects `Retry-After` header on 429 responses
- Implements exponential backoff on failures
- Caches responses to minimize API calls

## Best Practices

### Image Export
1. Use 2x scale for high-quality screenshots
2. Export specific frames, not entire files
3. Use PNG for UI with transparency, JPG for photos
4. Use SVG for icons and simple graphics

### Token Extraction
1. Ensure styles are properly defined in Figma
2. Use consistent naming in design file
3. Export tokens early to establish CSS variables
4. Re-extract when design system updates

### Performance
1. Use `analyze` once, then reference cached data
2. Export only the frames you need
3. Use `--no-images` if you only need JSON data
4. Clear cache when designs change significantly

## Troubleshooting

### "FIGMA_ACCESS_TOKEN not found"

Set the token via environment or `.env` file:
```bash
export FIGMA_ACCESS_TOKEN="figd_..."
```

### "Access forbidden" (403)

- Token may have expired - generate a new one
- Token may lack permissions - regenerate with correct scopes
- File may not be accessible to your account

### "File not found" (404)

- Check the file key in the URL
- Ensure you have access to the file
- Verify the URL format is correct

### Rate limited (429)

The script handles this automatically, but if persistent:
- Reduce request frequency
- Use cached data when possible
- Check if you're hitting plan limits

## Resources

- [Figma REST API Documentation](https://www.figma.com/developers/api)
- [Access Tokens](https://www.figma.com/developers/api#access-tokens)
- See `references/api_endpoints.md` for detailed endpoint documentation

---

## Figma MCP Server (Optional)

The Figma MCP Server provides additional capabilities not available via REST API:

| Feature | REST API | MCP Server |
|---------|:--------:|:----------:|
| File structure | Yes | Yes |
| Export images | Yes | Yes |
| Design tokens (from tree) | Yes | Yes |
| Comments | Yes | No |
| Versions | Yes | No |
| **Figma Variables** | Enterprise only | All plans |
| **AI design context** | No | Yes |
| **FigJam extraction** | Limited | AI-optimized |

### When to Use MCP

Use the Figma MCP Server when you need:
- **Figma Variables** (design tokens with modes/themes) - REST API requires Enterprise plan
- **AI-optimized design context** for code generation
- **FigJam content** extracted as AI-friendly XML

### MCP Setup

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

On first use, a browser will open for OAuth authorization.

### MCP Tools Available

| Tool | Purpose |
|------|---------|
| `get_variable_defs` | Get variables and styles from selection |
| `get_design_context` | AI-optimized design extraction for code generation |
| `get_screenshot` | Capture screenshot of selection |
| `get_metadata` | Get sparse XML representation of selection |
| `get_figjam` | Convert FigJam diagrams to XML with screenshots |
| `create_design_system_rules` | Generate design system rules for AI agents |
| `whoami` | Get current user info and plan type |

### Extracting Figma Variables

If the user asks for "Figma variables" or "design tokens with modes":

1. Check if `get_variable_defs` tool is available (MCP connected)
2. If not available, inform user: "Figma Variables require the MCP Server. Add to `~/.claude/mcp.json`"
3. If available, use the tool with the Figma URL containing selection

Example MCP usage:
```
Use the get_variable_defs tool with the Figma URL to extract variables.
The user should have a frame or component selected in Figma.
```

### AI Design Context

Use `get_design_context` for AI-optimized design extraction:
- Returns React + Tailwind code by default
- Customize framework/styling via prompts
- Best for "implement this design" workflows

### MCP Rate Limits

| Plan | Limit |
|------|-------|
| Free/Starter | 6 tool calls/month |
| Professional+ | Per-minute limits (Tier 1) |

### Remote vs Desktop MCP

Two MCP server options exist:

| Aspect | Remote MCP | Desktop MCP |
|--------|-----------|-------------|
| URL | `https://mcp.figma.com/mcp` | `http://127.0.0.1:3845/sse` |
| Setup | Add URL to mcp.json | Install Figma desktop app |
| Auth | OAuth (browser popup) | Already authenticated |
| Requirements | Internet connection | Figma app running |
| Plans | All (with limits) | Professional+ |

**Recommendation:** Use Remote MCP for simplicity. Desktop MCP requires the Figma app to be running and is only available on Professional+ plans.
