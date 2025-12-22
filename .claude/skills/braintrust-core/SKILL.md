---
name: braintrust-core
description: Manage Braintrust projects and workspace setup. Use this skill when creating new Braintrust projects, listing available projects, or performing project-level administration tasks.
---

# Braintrust Core - Project Management

Manage Braintrust projects with full CRUD operations for workspace setup and administration.

## When to Use This Skill

Use this skill when the user wants to:
- Create a new Braintrust project
- List all available projects in the organization
- Get details about a specific project
- Update project settings or metadata
- Delete a project
- Perform initial Braintrust workspace setup

**Note**: This skill is typically used during initial setup or administrative tasks. For day-to-day experimentation work, use the `braintrust-experimentation` skill instead.

## Prerequisites

Before using this skill, ensure:

1. **Braintrust SDK is installed**:
   ```bash
   pip install braintrust
   ```

2. **API key is configured**:
   - Set in `.env` file: `BRAINTRUST_API_KEY=your_api_key_here` (automatically loaded)
   - Or export manually: `export BRAINTRUST_API_KEY=your_api_key_here`
   - Verify: `echo $BRAINTRUST_API_KEY`

   To get your API key:
   - Visit [Braintrust Settings](https://www.braintrust.dev/app/settings)
   - Copy your API key
   - Add to `.env` file or export as environment variable

**Note**: All scripts automatically load environment variables from a `.env` file in the current directory if it exists.

## Tags Support

Projects support tags for organization. Tags format:
- **JSON array**: `'["tag1", "tag2"]'` - multiple tags
- **Single string**: `"production"` - converted to `["production"]`
- **Empty array**: `'[]'` - clears all tags

When updating, `--tags` replaces all existing tags (not a merge).

## Project Management Tool

The project management tool is located at `.claude/skills/braintrust-core/scripts/braintrust_projects.py`. Execute it using `python3` with appropriate commands.

### Available Commands

- **`list`** - List all projects in the organization
- **`get`** - Get details of a specific project by ID
- **`create`** - Create a new project (requires `--name` and `--org-name`)
- **`update`** - Update project properties (requires project ID)
- **`delete`** - Delete a project (requires project ID)

### Common Usage Patterns

#### List All Projects
To see all available projects in the organization:
```bash
python3 .claude/skills/braintrust-core/scripts/braintrust_projects.py list
```

This returns JSON with all projects including their IDs, names, and metadata. Save project IDs for use in other Braintrust skills.

#### Create a New Project
To create a new project for organizing experiments, prompts, and datasets:
```bash
python3 .claude/skills/braintrust-core/scripts/braintrust_projects.py create --name "My Project" --org-name "My Org"
```

Create project with tags:
```bash
python3 .claude/skills/braintrust-core/scripts/braintrust_projects.py create \
  --name "Production Project" \
  --org-name "My Org" \
  --tags '["production", "v2"]'
```

**Important**: Save the returned `project_id` from the response. This ID is required for creating prompts, datasets, and experiments in the `braintrust-experimentation` skill.

#### Get Project Details
To retrieve detailed information about a specific project:
```bash
python3 .claude/skills/braintrust-core/scripts/braintrust_projects.py get PROJECT_ID
```

#### Update Project
To update project name, description, or other metadata:
```bash
python3 .claude/skills/braintrust-core/scripts/braintrust_projects.py update PROJECT_ID --name "Updated Name"
```

Update project tags:
```bash
python3 .claude/skills/braintrust-core/scripts/braintrust_projects.py update PROJECT_ID --tags '["deprecated"]'
```

#### Delete Project
To permanently delete a project and all its associated resources:
```bash
python3 .claude/skills/braintrust-core/scripts/braintrust_projects.py delete PROJECT_ID
```

**Warning**: Deletion is permanent and will remove all prompts, datasets, experiments, and logs associated with the project.

## Typical Workflow

### Initial Setup
1. List existing projects to see what's available
2. Either select an existing project ID or create a new project
3. Save the project ID for use with other Braintrust skills

### Project Administration
1. List projects to get current state
2. Update project metadata as needed
3. Delete obsolete projects when no longer needed

## Output Format

All commands return JSON output for easy parsing:
```json
{
  "id": "project_id_here",
  "name": "Project Name",
  "org_name": "Organization Name",
  "created_at": "2025-01-15T10:30:00Z",
  "metadata": {}
}
```

## Error Handling

The tool provides detailed error messages for:
- Missing or invalid API key
- Network connectivity issues
- Invalid project IDs
- Permission errors
- Missing required parameters

When errors occur, check:
1. API key is set: `echo $BRAINTRUST_API_KEY`
2. Network connectivity to `api.braintrust.dev`
3. Project ID is valid (from list command)
4. Organization name is correct

## Integration with Other Skills

After creating or selecting a project:
- Use **`braintrust-experimentation`** skill for prompts, datasets, and experiments
- Use **`braintrust-logs`** skill for production log management
- Use **`braintrust-evaluation`** skill for running evaluations

## Reference Documentation

For additional information:
- Braintrust API: https://www.braintrust.dev/docs/reference/api
- Python SDK: https://github.com/braintrustdata/braintrust-api-py
