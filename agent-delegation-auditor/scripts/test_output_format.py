#!/usr/bin/env python3
"""
Test script to check if the current model supports output_format parameter.

This creates a simple agent with output_format=json_schema and checks
whether the response is pure JSON or wrapped in markdown/text.
"""

import asyncio
import json
import os
from pathlib import Path

try:
    from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, AssistantMessage, TextBlock, ResultMessage
except ImportError:
    print("Error: claude_agent_sdk not installed. Install with: pip install claude-agent-sdk")
    exit(1)


# Simple JSON schema for testing
TEST_SCHEMA = {
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["PASS", "FAIL"]},
            "rating": {"type": "integer", "minimum": 1, "maximum": 10},
            "summary": {"type": "string"}
        },
        "required": ["verdict", "rating", "summary"]
    }
}

TEST_PROMPT = """You are a test agent. Your response must be a JSON object with:
- verdict: "PASS" or "FAIL"
- rating: a number from 1 to 10
- summary: a brief summary

Please respond with a JSON object that says this test passed with a rating of 8."""

MODEL = os.getenv("ANTHROPIC_MODEL", "default")


async def test_output_format():
    """Test if the current model supports output_format."""

    print(f"Testing model: {MODEL}")
    print(f"Schema: {json.dumps(TEST_SCHEMA, indent=2)}")
    print("-" * 60)

    options = ClaudeAgentOptions(
        system_prompt=TEST_PROMPT,
        output_format=TEST_SCHEMA,
        allowed_tools=[],
        permission_mode="bypassPermissions",
    )

    async with ClaudeSDKClient(options) as client:
        await client.query("Respond with a JSON object indicating this test passed.")

        content_parts = []
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                if msg.error:
                    print(f"Error: {msg.error}")
                    return

                for block in msg.content:
                    if isinstance(block, TextBlock):
                        content_parts.append(block.text)

            elif isinstance(msg, ResultMessage):
                break

        full_response = "\n".join(content_parts)

        print("RAW RESPONSE:")
        print("-" * 60)
        print(full_response)
        print("-" * 60)
        print()

        # Try to parse as JSON
        try:
            parsed = json.loads(full_response)
            print("JSON PARSING: SUCCESS")
            print(f"Parsed data: {json.dumps(parsed, indent=2)}")
            print()
            print("Model SUPPORTS output_format parameter")
        except json.JSONDecodeError as e:
            print(f"JSON PARSING: FAILED - {e}")
            print()
            print("Model does NOT support output_format parameter")
            print("(Response was not pure JSON)")


if __name__ == "__main__":
    asyncio.run(test_output_format())
