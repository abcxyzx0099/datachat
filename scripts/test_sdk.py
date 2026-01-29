import asyncio
from pathlib import Path
from datetime import datetime
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

async def test_sdk_basic():
    """Test basic SDK functionality."""
    print("=== Test 1: Basic SDK Query ===")

    options = ClaudeAgentOptions(
        cwd=str(PROJECT_ROOT),  # Set working directory
        permission_mode="acceptEdits",
        setting_sources=["project"],  # Load project settings (skills)
    )

    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query("Say 'SDK is working' and nothing else.")

            response_received = False
            async for message in client.receive_messages():
                print(f"Message type: {type(message).__name__}")

                if hasattr(message, 'subtype'):
                    print(f"  Subtype: {message.subtype}")
                    if message.subtype == 'success':
                        print(f"  Result: {message.result}")
                        response_received = True
                        break
                    elif message.subtype == 'error':
                        print(f"  Error: {message.result}")
                        return False
                else:
                    # Regular content message
                    if hasattr(message, 'content'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                print(f"  Text: {block.text[:100]}")

            if response_received:
                print("✅ Test 1 PASSED: SDK basic query works\n")
                return True
            else:
                print("❌ Test 1 FAILED: No response received\n")
                return False

    except Exception as e:
        print(f"❌ Test 1 FAILED: {type(e).__name__}: {e}\n")
        return False


async def test_sdk_with_task_coordination():
    """Test SDK with task-coordination skill."""
    print("=== Test 2: SDK with task-coordination skill ===")

    # Create a simple test task
    test_task_content = """# Task: Simple SDK test

**Created**: 2026-01-29 04:00:00
**Status**: pending

---

## Task
Create a file named sdk-test-output.txt with "SDK test successful" message.

## Requirements
1. Create sdk-test-output.txt in project root
2. Add message and timestamp

## Success Criteria
1. File exists
"""

    options = ClaudeAgentOptions(
        cwd=str(PROJECT_ROOT),  # Set working directory
        agents={
            "test-executor": AgentDefinition(
                description="Test executor that uses task-coordination skill",
                prompt="""You are a test executor. When given a task:

1. Use the Skill tool to invoke task-coordination
2. Pass the task document content
3. Return the result

IMPORTANT: Always delegate to task-coordination skill.""",
                tools=["Skill", "Read", "Write", "Edit", "Bash"],
                model="sonnet",
            )
        },
        permission_mode="acceptEdits",
        allowed_tools=["Skill", "Read", "Write", "Edit", "Bash"],
        setting_sources=["project"],  # Load project settings (skills)
    )

    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query(test_task_content)

            response_received = False
            async for message in client.receive_messages():
                print(f"Message type: {type(message).__name__}")

                if hasattr(message, 'subtype'):
                    print(f"  Subtype: {message.subtype}")
                    if message.subtype == 'success':
                        print(f"  Result: {message.result[:200] if message.result else 'None'}")
                        response_received = True
                        break
                    elif message.subtype == 'error':
                        print(f"  Error: {message.result}")
                        return False
                else:
                    if hasattr(message, 'content'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                text = block.text
                                print(f"  Text preview: {text[:100]}...")

            if response_received:
                print("✅ Test 2 PASSED: SDK with skill works\n")
                return True
            else:
                print("❌ Test 2 FAILED: No success response\n")
                return False

    except Exception as e:
        print(f"❌ Test 2 FAILED: {type(e).__name__}: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_sdk_with_file_path():
    """Test SDK passing a file path (like the monitor does)."""
    print("=== Test 3: SDK with file path (monitor workflow) ===")

    # Create test task file
    test_file = Path("tasks/sdk-test-001.md")
    test_file.write_text("""# Task: SDK path test

**Created**: 2026-01-29 04:05:00
**Status**: pending

---

## Task
Create sdk-path-test.txt file.

## Requirements
1. Create file with message

## Success Criteria
1. File exists
""")

    print(f"Created test file: {test_file}")

    options = ClaudeAgentOptions(
        cwd=str(PROJECT_ROOT),  # Set working directory
        agents={
            "task-executor": AgentDefinition(
                description="Executes tasks by delegating to task-coordination",
                prompt="""You are a task executor. When given a task document:

1. Read the task document to understand requirements
2. Use the Skill tool to invoke task-coordination skill
3. Pass the task document content or path to the skill
4. Return the final result

IMPORTANT: Always delegate to task-coordination skill, do NOT implement yourself.""",
                tools=["Skill", "Read", "Write", "Edit", "Bash", "Task"],
                model="sonnet",
            )
        },
        permission_mode="acceptEdits",
        allowed_tools=["Skill", "Read", "Write", "Edit", "Bash", "Task"],
        setting_sources=["project"],  # Load project settings (skills)
    )

    try:
        async with ClaudeSDKClient(options=options) as client:
            # Pass the task content (like monitor_daemon does)
            task_content = test_file.read_text()
            await client.query(f"Execute this task:\n\n{task_content}")

            response_received = False
            async for message in client.receive_messages():
                print(f"Message type: {type(message).__name__}")

                if hasattr(message, 'subtype'):
                    print(f"  Subtype: {message.subtype}")
                    if message.subtype == 'success':
                        print(f"  Result received")
                        response_received = True
                        break
                    elif message.subtype == 'error':
                        print(f"  Error: {message.result}")
                        return False
                else:
                    if hasattr(message, 'content'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                print(f"  Progress: {block.text[:80]}...")

            if response_received:
                print("✅ Test 3 PASSED: SDK file path workflow works\n")
                return True
            else:
                print("❌ Test 3 FAILED: No success response\n")
                return False

    except Exception as e:
        print(f"❌ Test 3 FAILED: {type(e).__name__}: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup test file
        if test_file.exists():
            test_file.unlink()


async def main():
    print("\n" + "="*60)
    print("Claude Agent SDK Integration Test")
    print("="*60 + "\n")

    results = {}

    # Run tests
    results['test1'] = await test_sdk_basic()
    results['test2'] = await test_sdk_with_task_coordination()
    results['test3'] = await test_sdk_with_file_path()

    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    total_passed = sum(results.values())
    total_tests = len(results)
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
