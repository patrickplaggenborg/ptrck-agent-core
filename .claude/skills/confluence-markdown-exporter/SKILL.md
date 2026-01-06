---
name: confluence-markdown-exporter
description: Export Confluence pages to markdown format with hierarchy, attachments, and metadata preserved. Use this skill when users want to export Confluence content to markdown for documentation, migration to Obsidian/git, or offline use.
---

# Confluence Markdown Exporter

Export Confluence pages to well-formatted markdown files with preserved hierarchy, images, attachments, and metadata.

## When to Use This Skill

Use this skill when the user wants to:
- Export Confluence pages to markdown files
- Migrate Confluence content to markdown-based systems (Obsidian, Azure DevOps, git)
- Create offline documentation from Confluence
- Export page trees with preserved hierarchy

For reading/searching Confluence without export, use the `confluence-readonly` skill instead.

## Prerequisites

1. **Install confluence-markdown-exporter**:
   ```bash
   pip install confluence-markdown-exporter --upgrade
   ```

2. **Configure authentication**:
   ```bash
   confluence-markdown-exporter config
   ```
   This opens an interactive menu to configure your Confluence URL, username, and API token.

3. **Verify setup**:
   ```bash
   cf-export config
   ```

## Exporter Tool

The exporter tool is located at `.claude/skills/confluence-markdown-exporter/scripts/confluence_export.py`. Execute it using `python3` with appropriate commands.

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `page` | Export single page | `page 12345 /output/` |
| `tree` | Export page with all descendants | `tree 12345 /output/` |
| `space` | Export entire space | `space MYSPACE /output/` |
| `config` | Configure authentication | `config` |

### Common Usage Patterns

#### Export Single Page
```bash
# By page ID
python3 .claude/skills/confluence-markdown-exporter/scripts/confluence_export.py page 12345 /output/

# By page URL
python3 .claude/skills/confluence-markdown-exporter/scripts/confluence_export.py page "https://mycompany.atlassian.net/wiki/spaces/PROJ/pages/12345" /output/
```

#### Export Page Tree (with descendants)
```bash
python3 .claude/skills/confluence-markdown-exporter/scripts/confluence_export.py tree 12345 /output/docs/
```

#### Export Entire Space
```bash
python3 .claude/skills/confluence-markdown-exporter/scripts/confluence_export.py space MYSPACE /output/myspace/
```

#### Configure Authentication
```bash
python3 .claude/skills/confluence-markdown-exporter/scripts/confluence_export.py config
```

## Output Features

The exporter produces high-quality markdown with:
- **Preserved hierarchy** - Directory structure matches page tree
- **Images and attachments** - Downloaded and linked correctly
- **Front matter metadata** - Page properties, labels, timestamps
- **Breadcrumb navigation** - Links to parent pages
- **Mermaid diagrams** - Extracted from draw.io attachments
- **Tables and code blocks** - Properly converted

## Default Output Path

If not specified, exports default to the `/output/` directory.

## Error Handling

When errors occur, check:
1. CLI is installed: `which cf-export` or `pip show confluence-markdown-exporter`
2. Authentication is configured: `cf-export config`
3. Network connectivity to your Confluence instance
4. Page/space permissions

## CLI Documentation

For additional features and configuration options: https://github.com/Spenhouet/confluence-markdown-exporter
