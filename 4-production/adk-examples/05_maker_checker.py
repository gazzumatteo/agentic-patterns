"""
Pattern 34: Maker-Checker Loop
Formal verification pattern with strict turn-based creation and validation.
Essential for high-stakes domains requiring accuracy.

Business Example: Regulatory Compliance Automation (Investment Bank)
- Maker agent generates trading algorithms
- Checker agent validates against regulations
- Iterative refinement until compliance achieved
- Every algorithm has audit trail

This example demonstrates Google ADK's LoopAgent for maker-checker validation.

Mermaid Diagram Reference: See diagrams/34_maker_checker.mermaid
"""

import asyncio
import json
from typing import Dict, Any, List
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.sessions import InMemorySessionService
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools import exit_loop


# Maker Agent
maker_agent = LlmAgent(
    name="AlgorithmMaker",
    model="gemini-2.5-flash",
    instruction="""
    You are a trading algorithm designer.

    Your role is to CREATE trading algorithms based on requirements.
    If you receive checker feedback, REFINE your algorithm accordingly.

    Requirements for your algorithm:
    - Clear entry/exit rules
    - Risk management parameters
    - Position sizing rules
    - Stop loss mechanisms

    Output your algorithm as structured JSON with these components.
    If this is a refinement, explain what you changed based on feedback.
    """,
    description="Creates and refines trading algorithms",
    output_key="algorithm_design"
)

# Checker Agent
checker_agent = LlmAgent(
    name="ComplianceChecker",
    model="gemini-2.5-flash",
    instruction="""
    You are a regulatory compliance validator.

    Your role is to VALIDATE trading algorithms against regulations:

    Compliance Rules:
    1. Position size must not exceed 10% of portfolio
    2. Stop loss must be present and <= 5%
    3. No leverage > 2x
    4. Must have circuit breaker for unusual volatility
    5. Must log all trades for audit

    Review the algorithm from state['algorithm_design'].

    Output JSON with:
    - approved: true/false
    - violations: list of compliance issues (if any)
    - warnings: list of concerns (if any)
    - feedback: specific guidance for fixes

    If all rules pass, set approved=true and call exit_loop.
    If violations exist, set approved=false with detailed feedback.
    """,
    description="Validates algorithm compliance",
    output_key="compliance_check",
    tools=[exit_loop]
)

# Create Maker-Checker Loop
maker_checker_loop = LoopAgent(
    name="MakerCheckerLoop",
    sub_agents=[maker_agent, checker_agent],
    max_iterations=5,
    description="Iterative algorithm creation and compliance validation"
)


async def create_compliant_algorithm(
    requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create algorithm with maker-checker validation loop.

    Args:
        requirements: Algorithm requirements

    Returns:
        Final approved algorithm with audit trail
    """
    session_service = InMemorySessionService()
    session_id = "maker_checker_001"
    app_name = "maker_checker_agent"
    user_id = "system"
    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
    session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)

    session.state["requirements"] = json.dumps(requirements)
    session.state["iteration"] = 0

    audit_trail = []

    # Custom event handling for maker-checker
    ctx = InvocationContext(
        session=session,
        request=f"Create trading algorithm with requirements: {json.dumps(requirements)}"
    )

    print(f"\n{'='*80}")
    print("MAKER-CHECKER LOOP STARTED")
    print(f"{'='*80}")

    iteration = 0
    async for event in maker_checker_loop.run(ctx):
        iteration += 1

        # Track each iteration
        algorithm = session.state.get("algorithm_design")
        compliance = session.state.get("compliance_check")

        if algorithm:
            print(f"\n--- Iteration {iteration}: MAKER ---")
            print(f"   Algorithm Created/Refined")

        if compliance:
            compliance_data = json.loads(compliance) if isinstance(compliance, str) else compliance
            approved = compliance_data.get("approved", False)

            print(f"\n--- Iteration {iteration}: CHECKER ---")
            print(f"   Status: {'✓ APPROVED' if approved else '✗ REJECTED'}")

            if not approved:
                violations = compliance_data.get("violations", [])
                print(f"   Violations: {len(violations)}")
                for v in violations:
                    print(f"      - {v}")

            audit_trail.append({
                "iteration": iteration,
                "algorithm": algorithm,
                "compliance_check": compliance_data,
                "approved": approved
            })

            if approved:
                print(f"\n✓ Algorithm APPROVED after {iteration} iterations")
                break

    return {
        "final_algorithm": session.state.get("algorithm_design"),
        "final_compliance": session.state.get("compliance_check"),
        "iterations": iteration,
        "audit_trail": audit_trail,
        "approved": audit_trail[-1]["approved"] if audit_trail else False
    }


async def main():
    """Main execution demonstrating maker-checker pattern."""

    print("=" * 80)
    print("Pattern 34: Maker-Checker Loop")
    print("Regulatory Compliance with Iterative Validation")
    print("=" * 80)

    # Test scenarios
    scenarios = [
        {
            "name": "Momentum Strategy",
            "requirements": {
                "strategy_type": "momentum",
                "target_return": "15% annual",
                "risk_tolerance": "medium",
                "asset_class": "equities"
            }
        },
        {
            "name": "Mean Reversion Strategy",
            "requirements": {
                "strategy_type": "mean_reversion",
                "target_return": "12% annual",
                "risk_tolerance": "low",
                "asset_class": "bonds"
            }
        }
    ]

    results = []

    for scenario in scenarios:
        print(f"\n\n{'='*80}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"{'='*80}")

        result = await create_compliant_algorithm(scenario["requirements"])
        results.append(result)

        print(f"\n📊 Results:")
        print(f"   Iterations: {result['iterations']}")
        print(f"   Status: {'✓ APPROVED' if result['approved'] else '✗ FAILED'}")
        print(f"   Audit Trail: {len(result['audit_trail'])} entries")

    # Summary
    print("\n\n" + "=" * 80)
    print("MAKER-CHECKER SUMMARY")
    print("=" * 80)

    total_iterations = sum(r['iterations'] for r in results)
    approved_count = sum(1 for r in results if r['approved'])

    print(f"\n📊 Overall Performance:")
    print(f"   Scenarios Processed: {len(results)}")
    print(f"   Approved: {approved_count}/{len(results)}")
    print(f"   Total Iterations: {total_iterations}")
    print(f"   Avg Iterations: {total_iterations/len(results):.1f}")

    print("\n" + "=" * 80)
    print("Pattern Demonstrated: Maker-Checker Loop")
    print("=" * 80)
    print("""
    Key Observations:
    1. Turn-Based Validation: Strict maker then checker sequence
    2. Iterative Refinement: Feedback drives improvements
    3. Formal Approval: Explicit approval/rejection decision
    4. Audit Trail: Complete history of iterations
    5. Exit Condition: Loop exits on approval or max iterations

    ADK Implementation:
    - LoopAgent for iterative cycles
    - exit_loop tool for completion signaling
    - State management for refinement context
    - max_iterations prevents infinite loops
    - Session tracks complete audit trail

    Business Impact (from article):
    - Regulatory violations: -97%
    - Deployment time: 2 weeks → 2 days
    - Audit success rate: 100%
    - Saved $25M in potential fines

    Applications:
    - Regulatory compliance automation
    - Code review processes
    - Financial algorithm validation
    - Medical protocol verification
    - Legal document review
    """)


if __name__ == "__main__":
    asyncio.run(main())
