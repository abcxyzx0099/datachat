"""
Example usage of the LangGraph survey analysis workflow.

This script demonstrates how to:
1. Create initial state
2. Build the workflow graph
3. Run the workflow
4. Handle human-in-the-loop interactions
"""

from workflow import create_initial_state, create_workflow


def example_auto_approval_workflow():
    """
    Example: Run workflow with auto-approval enabled.

    This bypasses human review steps for quick testing.
    """
    # Create initial state
    state = create_initial_state(
        spss_file_path="data/survey.sav",
        config={
            "output_dir": "output",
            "auto_approve_recoding": True,  # Skip human review
            "auto_approve_indicators": True,
            "auto_approve_table_specs": True,
            "max_iterations": 3
        }
    )

    # Add mock metadata (normally from Step 1-3)
    state["filtered_metadata"] = [
        {
            "name": "age",
            "label": "Respondent Age",
            "variable_type": "numeric",
            "min_value": 18,
            "max_value": 99
        },
        {
            "name": "gender",
            "label": "Gender",
            "variable_type": "numeric",
            "min_value": 1,
            "max_value": 2,
            "value_labels": {1: "Male", 2: "Female"}
        }
    ]

    state["variable_centered_metadata"] = state["filtered_metadata"]

    # Create workflow
    app = create_workflow()

    # Run workflow (auto-approves everything)
    print("Running workflow with auto-approval...")

    # For Step 4: Recoding Rules
    print("\n=== Step 4: Generate Recoding Rules ===")
    result = app.invoke(state)
    print(f"Recoding rules approved: {result['recoding_rules_approved']}")
    if result.get("recoding_rules"):
        print(f"Generated {len(result['recoding_rules'].get('recoding_rules', []))} rules")

    # For Step 8: Indicators (would normally connect after recoding completes)
    print("\n=== Step 8: Generate Indicators ===")
    # In full workflow, these would be connected
    # result = app.invoke(state, from_step="indicators")

    # For Step 9: Table Specifications
    print("\n=== Step 9: Generate Table Specifications ===")
    # In full workflow, these would be connected
    # result = app.invoke(state, from_step="table_specs")

    print("\n✅ Workflow completed!")

    return result


def example_human_in_the_loop_workflow():
    """
    Example: Run workflow with human review steps.

    This demonstrates the interrupt mechanism for human approval.
    """
    # Create initial state with human review enabled
    state = create_initial_state(
        spss_file_path="data/survey.sav",
        config={
            "output_dir": "output",
            "auto_approve_recoding": False,  # Require human review
            "auto_approve_indicators": False,
            "auto_approve_table_specs": False,
            "max_iterations": 3
        }
    )

    # Add mock metadata
    state["filtered_metadata"] = [
        {
            "name": "age",
            "label": "Respondent Age",
            "variable_type": "numeric",
            "min_value": 18,
            "max_value": 99
        }
    ]

    state["variable_centered_metadata"] = state["filtered_metadata"]

    # Create workflow
    app = create_workflow()

    print("Running workflow with human-in-the-loop...")

    # Run workflow - this will pause at each review step
    # In a real application, you would handle interrupts like this:

    """
    for event in app.stream(state):
        # Check if workflow is waiting for human input
        if "__interrupt__" in event:
            # Get the interrupt data
            interrupt_data = event["__interrupt__"]

            print(f"\n📋 Review Required: {interrupt_data['task']}")
            print(f"\n{interrupt_data['report']}")

            # Get human decision (in real app, this would be from CLI/web)
            decision = input("Approve, reject, or modify? (approve/reject/modify): ")

            if decision == "approve":
                response = {"decision": "approve", "comments": "Looks good!"}
            elif decision == "reject":
                comments = input("Please provide feedback: ")
                response = {"decision": "reject", "comments": comments}
            elif decision == "modify":
                # Would allow editing JSON
                response = {"decision": "modify", "comments": "Modified", "modified_rules": {...}}

            # Resume workflow with human decision
            state = app.resume(state, response)
    """

    print("\n⚠️  Human-in-the-loop requires interrupt handling")
    print("See the LangGraph documentation for handling interrupts in your application")

    return state


def example_validation_retry_workflow():
    """
    Example: Demonstrate validation retry logic.

    This shows how the workflow automatically retries when validation fails.
    """
    state = create_initial_state(
        spss_file_path="data/survey.sav",
        config={
            "auto_approve_recoding": True,
            "max_iterations": 3
        }
    )

    # Add metadata
    state["filtered_metadata"] = [
        {
            "name": "age",
            "label": "Age",
            "variable_type": "numeric",
            "min_value": 18,
            "max_value": 99
        }
    ]

    # Create workflow
    app = create_workflow()

    print("\n=== Example: Validation Retry Logic ===")
    print("\nWhen validation fails:")
    print("1. Validator returns errors")
    print("2. Workflow routes back to generate node")
    print("3. New prompt includes validation errors")
    print("4. LLM generates improved output")
    print("5. Process repeats until valid or max_iterations reached")

    print("\nMax iterations: 3")
    print("If validation still fails after 3 iterations,")
    print("workflow proceeds to review with warnings")

    return state


def print_workflow_structure():
    """Print the workflow structure for reference."""
    from workflow.graph import get_workflow_structure

    print("\n" + "=" * 70)
    print("LANGGRAPH WORKFLOW STRUCTURE")
    print("=" * 70)
    print(get_workflow_structure())
    print("=" * 70)


if __name__ == "__main__":
    import sys

    print("\n🚀 Survey Analysis LangGraph Workflow - Examples\n")

    # Print workflow structure
    print_workflow_structure()

    # Run examples
    if len(sys.argv) > 1:
        example_type = sys.argv[1]

        if example_type == "auto":
            example_auto_approval_workflow()
        elif example_type == "human":
            example_human_in_the_loop_workflow()
        elif example_type == "retry":
            example_validation_retry_workflow()
        else:
            print(f"\n❌ Unknown example type: {example_type}")
            print("Usage: python example.py [auto|human|retry]")
    else:
        print("\nUsage: python example.py [auto|human|retry]")
        print("\nExamples:")
        print("  python example.py auto    - Run with auto-approval")
        print("  python example.py human   - Run with human review")
        print("  python example.py retry   - Show validation retry logic")
