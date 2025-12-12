---
name: braintrust-evaluation
description: Run Braintrust evaluations locally and push code to Braintrust platform. Use this skill when executing evaluation scripts, running tests with watch mode, pushing functions to Braintrust, or integrating evaluations into CI/CD pipelines.
---

# Braintrust Evaluation Runner

Run Braintrust evaluations locally and push code to the Braintrust platform for serverless execution.

## When to Use This Skill

Use this skill when the user wants to:
- Run Braintrust evaluation scripts locally
- Execute evaluations with watch mode for rapid iteration
- Filter and run specific test cases
- Push Python functions to Braintrust for serverless execution
- Set up evaluation pipelines
- Run evaluations in development mode
- Integrate evaluations into CI/CD workflows

## Prerequisites

Before using this skill:

1. **Braintrust SDK and CLI installed**:
   ```bash
   pip install braintrust
   ```

2. **API key configured**:
   ```bash
   export BRAINTRUST_API_KEY=your_api_key_here
   ```

3. **Evaluation file exists**: Create a Python file with Braintrust `Eval` definitions

## Evaluation Runner Tool

The evaluation tool is located at `scripts/braintrust_eval.py`. It provides two main commands: `eval` for running evaluations and `push` for deploying code.

### Command: `eval`

Run Braintrust evaluations locally with various options for filtering, watching, and debugging.

**Basic Usage:**
```bash
# Run all evaluations in current directory
python3 scripts/braintrust_eval.py eval

# Run specific evaluation file
python3 scripts/braintrust_eval.py eval path/to/eval.py

# Run evaluations in a specific directory
python3 scripts/braintrust_eval.py eval path/to/eval_dir/
```

**Available Options:**

- `--watch` / `-w`: Auto-rerun evaluations when files change (for rapid iteration)
- `--filter FILTER`: Filter test cases using metadata expressions (e.g., `"metadata.priority='^P0$'"`)
- `--list`: List all available evaluators without running them
- `--no-send-logs`: Run evaluations without sending results to Braintrust (local only)
- `--dev`: Run in development mode with local server
- `--dev-port PORT`: Specify port for dev server (default: 8788)

**Examples:**

```bash
# Watch mode for rapid iteration
python3 scripts/braintrust_eval.py eval my_eval.py --watch

# Run only P0 priority tests
python3 scripts/braintrust_eval.py eval --filter "metadata.priority='^P0$'"

# List evaluators without running
python3 scripts/braintrust_eval.py eval --list

# Run locally without sending logs to Braintrust
python3 scripts/braintrust_eval.py eval my_eval.py --no-send-logs

# Development mode with custom port
python3 scripts/braintrust_eval.py eval --dev --dev-port 8300
```

### Command: `push`

Push Python functions to Braintrust for serverless execution.

**Basic Usage:**
```bash
# Push a function file
python3 scripts/braintrust_eval.py push my_function.py

# Push with replace strategy (overwrite if exists)
python3 scripts/braintrust_eval.py push my_function.py --if-exists replace

# Push with skip strategy (don't overwrite if exists)
python3 scripts/braintrust_eval.py push my_function.py --if-exists skip
```

**Available Options:**

- `--if-exists STRATEGY`: What to do if function already exists
  - `replace`: Overwrite existing function
  - `skip`: Skip if function exists
  - `error`: Raise error if function exists (default)

## Evaluation File Format

Create evaluation files using the Braintrust Python SDK:

```python
from braintrust import Eval

def is_equal(expected, output):
    """Scoring function"""
    return 1.0 if expected == output else 0.0

def is_relevant(expected, output):
    """Another scoring function"""
    # Custom logic here
    return 0.8

Eval(
    "My Evaluation Name",
    data=lambda: [
        {
            "input": "What is 2+2?",
            "expected": "4",
            "metadata": {"priority": "P0", "category": "math"}
        },
        {
            "input": "What is 3+3?",
            "expected": "6",
            "metadata": {"priority": "P1", "category": "math"}
        },
    ],
    task=lambda input: my_model(input),  # Your model function
    scores=[is_equal, is_relevant],  # Scoring functions
)
```

## Common Workflows

### Rapid Iteration During Development

To quickly iterate on prompts or models:

1. Create evaluation file with test cases
2. Run with watch mode: `python3 scripts/braintrust_eval.py eval my_eval.py --watch`
3. Edit model or prompt code
4. Watch automatically reruns and shows results
5. Iterate until satisfied

### Running Specific Test Subsets

To run only certain tests (e.g., high-priority):

1. Add metadata to test cases with priority/category tags
2. Run with filter: `python3 scripts/braintrust_eval.py eval --filter "metadata.priority='^P0$'"`
3. Analyze results for critical tests first
4. Run full suite when P0 tests pass

### Local Development Without Cloud

To test evaluations locally without sending data to Braintrust:

1. Create evaluation file
2. Run with `--no-send-logs`: `python3 scripts/braintrust_eval.py eval my_eval.py --no-send-logs`
3. Review local output
4. Remove flag when ready to log to Braintrust

### CI/CD Integration

To integrate evaluations into CI/CD pipelines:

1. Set `BRAINTRUST_API_KEY` in CI environment
2. Install Braintrust SDK in CI: `pip install braintrust`
3. Run evaluations: `python3 scripts/braintrust_eval.py eval`
4. Parse JSON output for pass/fail decisions
5. Fail build if evaluation scores below threshold

### Deploying Functions to Braintrust

To deploy functions for serverless execution:

1. Write Python function file
2. Push to Braintrust: `python3 scripts/braintrust_eval.py push my_function.py`
3. Use `--if-exists replace` to update existing functions
4. Function is now callable from Braintrust platform

## Watch Mode Best Practices

When using `--watch` mode:

- Keep evaluation files focused and fast for quick feedback
- Use smaller datasets during iteration
- Remove `--watch` flag for final full evaluation runs
- Watch mode monitors file changes and auto-reruns

## Filter Expressions

Filter expressions use metadata fields with regex patterns:

```bash
# Priority filters
--filter "metadata.priority='^P0$'"      # Only P0 tests
--filter "metadata.priority='^P[01]$'"   # P0 and P1 tests

# Category filters
--filter "metadata.category='math'"      # Only math tests
--filter "metadata.category='(math|science)'"  # Math or science

# Multiple conditions (AND logic)
--filter "metadata.priority='^P0$' and metadata.category='math'"
```

## Output Format

Evaluation runs output detailed JSON results including:
- Per-test-case scores
- Aggregate statistics
- Timing information
- Pass/fail status

Parse this output for automated decision-making in CI/CD.

## Error Handling

The tool provides detailed errors for:
- Missing API key
- Invalid evaluation files
- Python syntax errors in eval code
- Network connectivity issues
- Invalid filter expressions

When errors occur:
1. Check API key: `echo $BRAINTRUST_API_KEY`
2. Verify SDK installed: `pip list | grep braintrust`
3. Validate Python syntax in eval file
4. Check filter expression syntax
5. Ensure network connectivity

## Integration with Other Skills

- **`braintrust-experimentation`**: Create prompts and datasets, then evaluate with this skill
- **`braintrust-core`**: Projects created there are used in evaluation results
- **`braintrust-logs`**: Evaluation results can be viewed in production logs

## Reference Documentation

For detailed evaluation guides:
- Braintrust Evaluations: https://www.braintrust.dev/docs/guides/evals
- Braintrust Functions: https://www.braintrust.dev/docs/guides/functions
- Python SDK: https://github.com/braintrustdata/braintrust-sdk
- CLI Reference: https://www.braintrust.dev/docs/reference/cli
