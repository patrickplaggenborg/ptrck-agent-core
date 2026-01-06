---
name: skill-seekers
description: Convert documentation websites, GitHub repositories, and PDFs into Claude AI skills. This skill should be used when the user wants to create a new skill from external documentation, API docs, or code repositories.
---

# Skill Seekers

Automatically convert documentation into production-ready Claude skills.

## Prerequisites

```bash
pip install skill-seekers
```

## Quick Start (One Command)

```bash
# Full automated workflow: scrape → enhance → package → upload
skill-seekers install --config react

# Or from a URL
skill-seekers install --url https://docs.example.com --name myapi
```

## Core Commands

### Scrape Documentation Website

```bash
# From URL
skill-seekers scrape --url https://react.dev --name react

# From preset config
skill-seekers scrape --config configs/react.json

# With AI enhancement (recommended)
skill-seekers scrape --url https://docs.stripe.com --name stripe --enhance-local

# Async mode for large docs (2-3x faster)
skill-seekers scrape --config configs/godot.json --async --workers 8
```

### Scrape GitHub Repository

```bash
# Basic repo scraping
skill-seekers github --repo facebook/react

# With issues and releases
skill-seekers github --repo django/django \
    --include-issues \
    --include-changelog \
    --include-releases

# Set GITHUB_TOKEN for higher rate limits
export GITHUB_TOKEN=ghp_your_token_here
```

### Extract from PDF

```bash
# Basic PDF
skill-seekers pdf --pdf docs/manual.pdf --name myskill

# With table extraction and parallel processing
skill-seekers pdf --pdf docs/manual.pdf --name myskill \
    --extract-tables \
    --parallel \
    --workers 8

# Scanned PDFs (requires pytesseract)
skill-seekers pdf --pdf docs/scanned.pdf --name myskill --ocr
```

### Unified Multi-Source (Docs + GitHub + PDF)

Combine multiple sources into one skill with automatic conflict detection:

```bash
skill-seekers unified --config configs/react_unified.json
```

Example unified config:
```json
{
  "name": "myframework",
  "sources": [
    {
      "type": "documentation",
      "base_url": "https://docs.myframework.com/"
    },
    {
      "type": "github",
      "repo": "owner/myframework"
    }
  ]
}
```

### Enhance SKILL.md

```bash
# AI-powered enhancement (uses Claude Code Max locally, no API cost)
skill-seekers enhance output/react/

# Transforms basic template into comprehensive guide with:
# - Real code examples (5-10 practical examples)
# - Domain-specific key concepts
# - Navigation guidance for different skill levels
```

### Package and Upload

```bash
# Package to .zip
skill-seekers package output/react/

# Package and auto-upload (requires ANTHROPIC_API_KEY)
skill-seekers package output/react/ --upload

# Or upload separately
skill-seekers upload output/react.zip
```

### Estimate Pages (Before Scraping)

```bash
# Know page count before committing to full scrape
skill-seekers estimate configs/godot.json
```

## Common Workflows

### Create Skill from Website Docs

```bash
skill-seekers scrape --url https://docs.stripe.com/api --name stripe-api --enhance-local
skill-seekers package output/stripe-api/
# Upload output/stripe-api.zip to Claude
```

### Create Skill from GitHub Repo

```bash
skill-seekers github --repo langchain-ai/langchain --include-issues
skill-seekers enhance output/langchain/
skill-seekers package output/langchain/
```

### Create Skill from PDF Manual

```bash
skill-seekers pdf --pdf ~/Downloads/api-reference.pdf --name custom-api --extract-tables
skill-seekers enhance output/custom-api/
skill-seekers package output/custom-api/
```

### Combined Docs + Code Analysis

```bash
# Create unified config
cat > configs/mylib_unified.json << 'EOF'
{
  "name": "mylib",
  "sources": [
    {"type": "documentation", "base_url": "https://mylib.dev/docs/"},
    {"type": "github", "repo": "org/mylib"}
  ]
}
EOF

skill-seekers unified --config configs/mylib_unified.json
skill-seekers package output/mylib/
```

## Output Structure

```
output/
├── myskill_data/           # Scraped raw data
│   ├── pages/              # JSON files (one per page)
│   └── summary.json        # Overview
│
└── myskill/                # The skill
    ├── SKILL.md            # Enhanced with real examples
    └── references/         # Categorized docs
        ├── index.md
        ├── getting_started.md
        ├── api.md
        └── ...
```

## Notes

- **Local markdown files** are not supported. For creating skills from local markdown, use the `skill-creator` skill instead.

## Tips

1. **Test small first** - Set `max_pages: 20` in config to validate before full scrape
2. **Always enhance** - Use `--enhance-local` for much better SKILL.md quality (3/10 → 9/10)
3. **Reuse scraped data** - Use `--skip-scrape` to rebuild without re-scraping
4. **Large docs** - Use `--async --workers 8` for 2-3x faster scraping
5. **Check llms.txt** - Many sites have llms.txt for 10x faster scraping (auto-detected)

## Available Presets

```bash
ls configs/  # In skill-seekers repo
# godot.json, react.json, vue.json, django.json, fastapi.json, etc.
```

## Multi-Platform Export

```bash
# Claude (default)
skill-seekers package output/react/

# Google Gemini
skill-seekers package output/react/ --target gemini

# OpenAI ChatGPT
skill-seekers package output/react/ --target openai

# Generic Markdown
skill-seekers package output/react/ --target markdown
```
