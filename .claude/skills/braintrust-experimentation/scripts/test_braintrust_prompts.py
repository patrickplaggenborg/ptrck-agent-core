#!/usr/bin/env python3
"""Tests for braintrust_prompts.py - verifies update_prompt preserves existing data."""

import json
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the module under test
import braintrust_prompts


def test_update_prompt_preserves_existing_data():
    """Test that updating tools doesn't wipe system message/model config."""

    # Simulate existing prompt with full configuration
    existing_prompt = {
        "id": "test-prompt-123",
        "name": "My Prompt",
        "slug": "my-prompt",
        "project_id": "proj-456",
        "description": "A test prompt",
        "tags": ["production", "v1"],
        "prompt_data": {
            "prompt": {
                "type": "chat",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."}
                ]
            },
            "options": {
                "model": "claude-3-5-sonnet-20241022",
                "temperature": 0.7
            },
            "tools": [
                {"type": "function", "function": {"name": "old_tool"}}
            ]
        }
    }

    # New tools to update
    new_tools = [
        {"type": "function", "function": {"name": "new_tool", "description": "A new tool"}}
    ]

    # Track what gets sent to PUT
    put_request_data = {}

    def mock_make_request(method, endpoint, data=None, params=None):
        if method == "GET":
            return existing_prompt
        elif method == "PUT":
            put_request_data.update(data or {})
            return {"id": "test-prompt-123", "log_id": "new-version"}
        return {}

    # Create temp tools file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(new_tools, f)
        tools_file = f.name

    try:
        with patch.object(braintrust_prompts, 'make_request', side_effect=mock_make_request):
            with patch('builtins.print'):  # Suppress output
                braintrust_prompts.update_prompt(
                    prompt_id="test-prompt-123",
                    tools_file=tools_file
                )

        # Verify the PUT request preserves existing data
        assert put_request_data.get("name") == "My Prompt", "Name should be preserved"
        assert put_request_data.get("slug") == "my-prompt", "Slug should be preserved"
        assert put_request_data.get("project_id") == "proj-456", "Project ID should be preserved"
        assert put_request_data.get("description") == "A test prompt", "Description should be preserved"
        assert put_request_data.get("tags") == ["production", "v1"], "Tags should be preserved"

        # Verify prompt_data structure
        prompt_data = put_request_data.get("prompt_data", {})
        assert "prompt" in prompt_data, "System message (prompt) should be preserved"
        assert prompt_data["prompt"]["messages"][0]["content"] == "You are a helpful assistant.", \
            "System message content should be preserved"

        assert "options" in prompt_data, "Options should be preserved"
        assert prompt_data["options"]["model"] == "claude-3-5-sonnet-20241022", \
            "Model should be preserved"
        assert prompt_data["options"]["temperature"] == 0.7, \
            "Temperature should be preserved"

        # Verify tools were updated
        assert prompt_data["tools"] == new_tools, "Tools should be updated to new value"

        print("PASSED: update_prompt preserves existing data when updating tools")

    finally:
        Path(tools_file).unlink()


def test_update_prompt_full_prompt_data_replaces():
    """Test that --prompt-data replaces the entire prompt_data (intentional)."""

    existing_prompt = {
        "id": "test-prompt-123",
        "name": "My Prompt",
        "slug": "my-prompt",
        "project_id": "proj-456",
        "prompt_data": {
            "prompt": {"type": "chat", "messages": [{"role": "system", "content": "Old message"}]},
            "options": {"model": "old-model"},
            "tools": [{"type": "function", "function": {"name": "old_tool"}}]
        }
    }

    new_prompt_data = {
        "prompt": {"type": "chat", "messages": [{"role": "system", "content": "New message"}]},
        "options": {"model": "new-model"}
    }

    put_request_data = {}

    def mock_make_request(method, endpoint, data=None, params=None):
        if method == "GET":
            return existing_prompt
        elif method == "PUT":
            put_request_data.update(data or {})
            return {"id": "test-prompt-123"}
        return {}

    with patch.object(braintrust_prompts, 'make_request', side_effect=mock_make_request):
        with patch('builtins.print'):
            braintrust_prompts.update_prompt(
                prompt_id="test-prompt-123",
                prompt_data=json.dumps(new_prompt_data)
            )

    # When --prompt-data is provided, it should fully replace prompt_data
    assert put_request_data["prompt_data"] == new_prompt_data, \
        "--prompt-data should replace entire prompt_data"

    print("PASSED: --prompt-data replaces entire prompt_data (intentional behavior)")


def test_update_prompt_updates_only_specified_fields():
    """Test that only specified fields are updated."""

    existing_prompt = {
        "id": "test-prompt-123",
        "name": "Original Name",
        "slug": "original-slug",
        "project_id": "proj-456",
        "description": "Original description",
        "tags": ["original"],
        "prompt_data": {"prompt": "Original prompt"}
    }

    put_request_data = {}

    def mock_make_request(method, endpoint, data=None, params=None):
        if method == "GET":
            return existing_prompt
        elif method == "PUT":
            put_request_data.update(data or {})
            return {"id": "test-prompt-123"}
        return {}

    with patch.object(braintrust_prompts, 'make_request', side_effect=mock_make_request):
        with patch('builtins.print'):
            braintrust_prompts.update_prompt(
                prompt_id="test-prompt-123",
                name="New Name"  # Only update name
            )

    assert put_request_data["name"] == "New Name", "Name should be updated"
    assert put_request_data["description"] == "Original description", "Description should be preserved"
    assert put_request_data["tags"] == ["original"], "Tags should be preserved"
    assert put_request_data["prompt_data"] == {"prompt": "Original prompt"}, "Prompt data should be preserved"

    print("PASSED: Only specified fields are updated")


if __name__ == "__main__":
    print("Running tests for braintrust_prompts.py update fix...\n")

    test_update_prompt_preserves_existing_data()
    test_update_prompt_full_prompt_data_replaces()
    test_update_prompt_updates_only_specified_fields()

    print("\nAll tests passed!")
