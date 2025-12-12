---
name: braintrust-logs
description: Manage Braintrust production logs with insertion, fetching, and feedback operations. Use this skill when monitoring production AI systems, analyzing user interactions, adding feedback to logs, or debugging production issues.
---

# Braintrust Production Logs

Manage production logs for AI systems including insertion, fetching, filtering, and feedback collection.

## When to Use This Skill

Use this skill when the user wants to:
- Insert production logs from AI applications
- Fetch and analyze recent production logs
- Filter logs by metadata or other criteria
- Add user feedback to specific log entries
- Monitor production system behavior
- Debug production issues
- Analyze real-world usage patterns

This skill is for production monitoring and observability, separate from experimentation workflows.

## Prerequisites

Before using this skill:

1. **Braintrust SDK installed**: `pip install braintrust`
2. **API key configured**: `export BRAINTRUST_API_KEY=your_api_key_here`
3. **Project ID available**: Use `braintrust-core` skill to get project ID

## Log Management Tool

The log management tool is located at `scripts/braintrust_logs.py`. It provides three main commands for production log workflows.

### Command: `insert`

Insert log events into a project from a JSON file.

**Usage:**
```bash
python3 scripts/braintrust_logs.py insert --project-id PROJECT_ID --file logs.json
```

**Log Event Format:**
JSON array with objects containing `input`, `output`, and optional `metadata`:
```json
[
  {
    "input": "User query or prompt",
    "output": "Model response or result",
    "metadata": {
      "user_id": "user_123",
      "session_id": "session_abc",
      "timestamp": "2025-01-15T10:30:00Z",
      "model": "gpt-4",
      "latency_ms": 1234,
      "cost": 0.002
    }
  },
  {
    "input": "Another query",
    "output": "Another response",
    "metadata": {
      "user_id": "user_456",
      "session_id": "session_def",
      "error": false
    }
  }
]
```

**Metadata Best Practices:**
Include relevant context for filtering and analysis:
- `user_id`: Track per-user patterns
- `session_id`: Group related interactions
- `timestamp`: Time-based analysis
- `model`: Compare different models
- `latency_ms`: Performance monitoring
- `cost`: Budget tracking
- `error`: Error detection
- Custom fields: Any domain-specific metadata

### Command: `fetch`

Fetch logs from a project with filtering and pagination support.

**Basic Usage:**
```bash
# Fetch recent logs
python3 scripts/braintrust_logs.py fetch --project-id PROJECT_ID --limit 100

# Fetch with filters
python3 scripts/braintrust_logs.py fetch \
  --project-id PROJECT_ID \
  --limit 50 \
  --filters '{"metadata.user_id": "user_123"}'

# Fetch next page using cursor
python3 scripts/braintrust_logs.py fetch \
  --project-id PROJECT_ID \
  --limit 100 \
  --cursor CURSOR_FROM_PREVIOUS_RESPONSE
```

**Available Options:**

- `--project-id`: (Required) Project ID to fetch logs from
- `--limit`: Maximum number of logs to return (default: 100)
- `--cursor`: Pagination cursor from previous response
- `--filters`: JSON string with filter criteria (e.g., `'{"metadata.error": true}'`)

**Filter Examples:**
```bash
# Fetch only errors
--filters '{"metadata.error": true}'

# Fetch specific user
--filters '{"metadata.user_id": "user_123"}'

# Fetch high-latency requests
--filters '{"metadata.latency_ms": {"$gt": 2000}}'

# Fetch specific model
--filters '{"metadata.model": "gpt-4"}'
```

**Pagination:**
When fetching large log sets:
1. First call returns logs + cursor in response
2. Use cursor in next call to fetch more results
3. Repeat until no cursor is returned (end of results)

### Command: `feedback`

Add user feedback to a specific log entry.

**Usage:**
```bash
python3 scripts/braintrust_logs.py feedback \
  --project-id PROJECT_ID \
  --log-id LOG_ID \
  --file feedback.json
```

**Feedback Format:**
JSON object with rating, comment, and optional metadata:
```json
{
  "rating": 5,
  "comment": "Very helpful and accurate response",
  "metadata": {
    "helpful": true,
    "accurate": true,
    "user_id": "user_123",
    "feedback_type": "positive"
  }
}
```

**Rating Scale:**
Typically 1-5, but can use any numeric scale appropriate for your use case.

## Common Workflows

### Real-time Production Monitoring

To monitor production systems in real-time:

1. Application logs interactions using `insert` (can be batched)
2. Periodically fetch recent logs: `python3 scripts/braintrust_logs.py fetch --project-id PROJECT_ID --limit 50`
3. Check for errors: `--filters '{"metadata.error": true}'`
4. Analyze latency: Filter for high latency logs
5. Review user feedback collected via `feedback` command

### Error Investigation

To investigate production errors:

1. Fetch error logs: `python3 scripts/braintrust_logs.py fetch --project-id PROJECT_ID --filters '{"metadata.error": true}'`
2. Review error patterns in output
3. Filter by specific error types or time ranges
4. Identify common failure modes
5. Use log IDs to add notes via feedback mechanism

### User Feedback Collection

To collect and analyze user feedback:

1. Application calls feedback endpoint when user provides rating/comment
2. Add feedback: `python3 scripts/braintrust_logs.py feedback --project-id PROJECT_ID --log-id LOG_ID --file feedback.json`
3. Fetch logs with feedback to analyze patterns
4. Identify low-rated interactions for improvement
5. Track feedback trends over time

### Performance Analysis

To analyze system performance:

1. Insert logs with latency metadata
2. Fetch logs: `python3 scripts/braintrust_logs.py fetch --project-id PROJECT_ID --limit 1000`
3. Parse JSON output to extract latency statistics
4. Filter high-latency requests: `--filters '{"metadata.latency_ms": {"$gt": 2000}}'`
5. Identify performance bottlenecks
6. Track performance improvements over time

### User Behavior Analysis

To understand user patterns:

1. Insert logs with user_id and session_id metadata
2. Fetch specific user's interactions: `--filters '{"metadata.user_id": "user_123"}'`
3. Analyze query patterns and topics
4. Track user satisfaction via feedback
5. Identify power users vs. casual users
6. Inform product decisions based on usage data

## Integration with Application Code

### Python Integration Example

```python
import requests
import os
import json

def log_to_braintrust(project_id, input_text, output_text, metadata):
    """Log an interaction to Braintrust"""
    log_data = [{
        "input": input_text,
        "output": output_text,
        "metadata": metadata
    }]

    # Write to temp file
    with open('/tmp/braintrust_log.json', 'w') as f:
        json.dump(log_data, f)

    # Insert using tool
    os.system(f'python3 scripts/braintrust_logs.py insert --project-id {project_id} --file /tmp/braintrust_log.json')

# Usage in application
log_to_braintrust(
    project_id="proj_123",
    input_text="User's question",
    output_text="AI response",
    metadata={
        "user_id": "user_456",
        "session_id": "session_789",
        "latency_ms": 1234,
        "model": "gpt-4"
    }
)
```

## Output Format

All commands return JSON for easy parsing:

**Insert Response:**
```json
{
  "inserted": 10,
  "status": "success"
}
```

**Fetch Response:**
```json
{
  "logs": [...],
  "cursor": "next_page_cursor",
  "has_more": true
}
```

**Feedback Response:**
```json
{
  "status": "success",
  "log_id": "log_123"
}
```

## Best Practices

### Logging Strategy
- **Batch inserts**: Collect logs and insert in batches for efficiency
- **Include context**: Add rich metadata for filtering and analysis
- **Structured metadata**: Use consistent field names across logs
- **PII handling**: Be careful with sensitive user information

### Fetching Strategy
- **Use limits**: Don't fetch all logs at once, use pagination
- **Filter early**: Apply filters to reduce data transfer
- **Cache cursors**: Save cursors for resuming fetches
- **Regular polling**: Set up periodic fetching for monitoring

### Feedback Strategy
- **Capture immediately**: Log feedback when user provides it
- **Include context**: Add metadata about feedback source
- **Link to logs**: Use correct log_id to associate feedback
- **Track metrics**: Monitor feedback trends over time

## Error Handling

The tool provides detailed errors for:
- Missing or invalid API key
- Invalid project or log IDs
- JSON format validation errors
- Network connectivity issues
- Missing required parameters

When errors occur:
1. Verify API key: `echo $BRAINTRUST_API_KEY`
2. Check SDK installed: `pip list | grep braintrust`
3. Validate JSON files: `python3 -m json.tool < file.json`
4. Verify project and log IDs
5. Check network connectivity to `api.braintrust.dev`

## Integration with Other Skills

- **`braintrust-core`**: Get project IDs for log insertion
- **`braintrust-experimentation`**: Compare production logs with experiment results
- **`braintrust-evaluation`**: Use production logs to create better test datasets

## Reference Documentation

For additional information:
- Braintrust API: https://www.braintrust.dev/docs/reference/api
- Logging Guides: https://www.braintrust.dev/docs/guides/logging
- Python SDK: https://github.com/braintrustdata/braintrust-api-py
