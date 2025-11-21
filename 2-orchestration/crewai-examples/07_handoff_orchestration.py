"""
Pattern 15: Handoff Orchestration (Delegation)
Dynamic task transfer between agents based on expertise and complexity.
Includes context preservation during handoffs.

Business Example: Complex Loan Origination - RegionalBank
- Simple loans: Basic agent (70% of volume)
- Complex cases: Specialist agent with underwriting logic
- Edge cases: Senior credit officer agent

Results:
- Application to approval: 3 days → 6 hours
- Approval accuracy: 94% → 97%
- Compliance violations: -89%
- Revenue per loan officer: +220%

This example demonstrates CrewAI's delegation pattern with dynamic handoffs.

Mermaid Diagram Reference: See diagrams/15_handoff_orchestration.mermaid
"""

from crewai import Agent, Task, Crew, Process
from typing import Dict


def create_loan_handoff_crew() -> Crew:
    """
    Create a 3-tier loan processing crew with dynamic handoff capability.

    Returns:
        Configured Crew with handoff orchestration
    """

    # ========================================
    # TIER 1: Level-1 Basic Agent
    # ========================================

    level_1_agent = Agent(
        role="Level-1 Loan Processing Agent",
        goal="Process simple loan applications efficiently (70% of volume) and escalate complex cases",
        backstory="""You are the first-line loan processor at RegionalBank.
        You handle straightforward personal loans quickly and accurately.

        Your expertise covers:
        - Personal loans under $50,000
        - Applicants with credit scores above 700
        - Standard W2 employment verification
        - Clean credit history (no bankruptcies or foreclosures)
        - Debt-to-income ratios under 40%

        You process these applications in ~2 hours with high accuracy.

        You ESCALATE applications that have:
        - Credit score below 700
        - Loan amount over $50,000
        - Self-employed applicants
        - Recent credit issues
        - Non-standard documentation
        - DTI ratio above 40%

        You preserve ALL application context when escalating to ensure
        the specialist doesn't have to re-gather information.""",
        verbose=True,
        allow_delegation=True  # Can hand off to specialist
    )

    # ========================================
    # TIER 2: Specialist Underwriter
    # ========================================

    specialist_agent = Agent(
        role="Specialist Underwriter Agent",
        goal="Handle complex loan applications requiring advanced underwriting analysis",
        backstory="""You are a specialist underwriter with advanced training
        in complex loan analysis. You receive escalations from Level-1 agents.

        Your expertise:
        - Credit scores 650-699 (deeper analysis required)
        - Loan amounts $50,000-$250,000
        - Self-employed applicants (business income verification)
        - Recent credit issues (context and recovery analysis)
        - Non-standard documentation (compensating factors)
        - DTI ratios 40-50% (overall financial picture evaluation)

        Advanced capabilities:
        - Evaluate compensating factors
        - Analyze income stability trends
        - Assess collateral quality
        - Risk-adjusted pricing

        You process complex cases in ~4 hours.

        You ESCALATE to Senior Credit Officer if:
        - Credit score below 650
        - Loan amount over $250,000
        - Recent bankruptcy or foreclosure
        - DTI over 50%
        - Unusual high-risk circumstances

        You receive complete context from Level-1 and add your specialist analysis.""",
        verbose=True,
        allow_delegation=True  # Can escalate to expert
    )

    # ========================================
    # TIER 3: Senior Credit Officer (Expert)
    # ========================================

    expert_agent = Agent(
        role="Senior Credit Officer - Expert Agent",
        goal="Make final decisions on edge cases and high-risk/high-value loans",
        backstory="""You are the Senior Credit Officer - the highest lending authority.
        You handle only the most complex edge cases escalated from specialists.

        Your authority covers:
        - Credit scores below 650 (deep risk analysis)
        - Loan amounts over $250,000 (portfolio impact)
        - Recent bankruptcies/foreclosures (rehabilitation assessment)
        - DTI over 50% (exceptional circumstances)
        - Unusual situations requiring senior judgment

        Expert capabilities:
        - Complete risk analysis with portfolio considerations
        - Strategic value assessment (customer lifetime value)
        - Creative loan structuring for viable non-standard cases
        - Final authority - no further escalation

        You review complete history from Level-1 and Specialist before
        making final decisions. Processing time: ~6 hours for thorough analysis.

        Your decisions are FINAL. You consider strategic relationships,
        portfolio impact, and long-term customer value.""",
        verbose=True,
        allow_delegation=False  # Expert is final - no further escalation
    )

    # ========================================
    # HANDOFF TASKS
    # ========================================

    # Level-1 Initial Processing
    level_1_task = Task(
        description="""
        Process loan application: {loan_application}

        Analyze:
        1. Credit score and credit history
        2. Loan amount requested
        3. Employment type and income verification
        4. Debt-to-income ratio
        5. Overall risk profile

        Make decision:
        - APPROVE: If meets all simple loan criteria
        - DENY: If clearly does not qualify
        - DELEGATE: If complexity exceeds Level-1 capability

        If delegating, provide:
        - Complete application context (preserve ALL information)
        - Specific escalation reason
        - Initial risk assessment
        - Recommended next tier (Specialist or Expert)

        Processing target: 2 hours
        """,
        expected_output="""Level-1 decision (APPROVE/DENY/DELEGATE) with:
        - Complete analysis
        - Preserved application context
        - Escalation reason if delegating
        - Processing time estimate""",
        agent=level_1_agent
    )

    # Specialist Processing (receives Level-1 context)
    specialist_task = Task(
        description="""
        Review escalated loan application from Level-1.

        You receive:
        - Complete application details
        - Level-1 initial analysis
        - Escalation reason

        Perform advanced underwriting:
        1. Review Level-1 findings
        2. Conduct deeper credit analysis
        3. Evaluate compensating factors
        4. Analyze income stability and trends
        5. Assess collateral if applicable
        6. Calculate risk-adjusted pricing

        Make decision:
        - APPROVE: With appropriate terms and conditions
        - DENY: With detailed rationale
        - DELEGATE: To Senior Credit Officer if exceeds specialist capability

        If delegating to Expert:
        - Preserve Level-1 AND Specialist analysis
        - Explain why senior judgment needed
        - Provide comprehensive risk assessment

        Processing target: 4 hours total
        """,
        expected_output="""Specialist decision (APPROVE/DENY/DELEGATE) with:
        - Advanced underwriting analysis
        - Complete context from Level-1 and Specialist tiers
        - Risk-adjusted terms if approved
        - Escalation justification if delegating""",
        agent=specialist_agent,
        context=[level_1_task]  # Receives Level-1 context
    )

    # Expert Final Decision (receives full history)
    expert_task = Task(
        description="""
        Make final decision on loan application escalated from Specialist.

        You have complete history:
        - Original application
        - Level-1 initial analysis
        - Specialist underwriting assessment
        - Full escalation chain and reasons

        Apply senior judgment:
        1. Review entire escalation history
        2. Conduct comprehensive risk analysis
        3. Consider portfolio and strategic factors
        4. Evaluate customer lifetime value
        5. Design creative structure if needed

        Make FINAL decision:
        - APPROVE: With custom structure and terms
        - DENY: With comprehensive rationale

        NO FURTHER ESCALATION AVAILABLE.

        Provide:
        - Complete decision rationale
        - Approved terms and special structure
        - Risk mitigation plan
        - Strategic considerations
        - Summary of full escalation chain

        Processing target: 6 hours total
        """,
        expected_output="""Expert FINAL decision (APPROVE/DENY) with:
        - Comprehensive senior officer analysis
        - Complete review of escalation history
        - Approved terms or denial rationale
        - Strategic and portfolio considerations
        - Risk mitigation plan""",
        agent=expert_agent,
        context=[level_1_task, specialist_task]  # Full history
    )

    # ========================================
    # CREATE HANDOFF CREW
    # ========================================

    crew = Crew(
        agents=[level_1_agent, specialist_agent, expert_agent],
        tasks=[level_1_task, specialist_task, expert_task],
        process=Process.sequential,  # Tasks execute in order, enabling handoffs
        verbose=True
    )

    return crew


def run_loan_processing(loan_application: str) -> Dict:
    """
    Process loan application with dynamic handoff escalation.

    Args:
        loan_application: Loan application details

    Returns:
        Final decision with handoff history
    """
    crew = create_loan_handoff_crew()

    print(f"\n{'='*80}")
    print("3-Tier Handoff Architecture:")
    print(f"{'='*80}")
    print("Tier 1: Level-1 Agent (70% of loans, 2 hours)")
    print("Tier 2: Specialist Agent (25% of loans, 4 hours)")
    print("Tier 3: Expert Agent (5% of loans, 6 hours)")
    print("\nContext Preservation: Complete handoff history maintained")
    print(f"{'='*80}\n")

    result = crew.kickoff(inputs={"loan_application": loan_application})

    return {
        "status": "completed",
        "result": result,
        "business_metrics": {
            "processing_time": "3 days → 6 hours",
            "accuracy": "94% → 97%",
            "compliance_violations": "-89%",
            "revenue_per_officer": "+220%"
        }
    }


def main():
    """Main execution demonstrating handoff orchestration."""

    print(f"\n{'='*80}")
    print("Pattern 15: Handoff Orchestration - CrewAI")
    print("Business Case: RegionalBank - Loan Origination")
    print(f"{'='*80}\n")

    # Example 1: Simple Loan (Level-1 only, no handoff)
    print("\nExample 1: Simple Personal Loan - Level-1 Handles")
    print("-" * 80)

    simple_loan = """
    Loan Application ID: APP_12345

    Applicant: John Smith
    Loan Amount: $25,000
    Purpose: Debt consolidation
    Credit Score: 750
    Employment: W2 employee, Software Engineer, 5 years
    Annual Income: $95,000
    Debt-to-Income Ratio: 28%
    Credit History: Clean, no late payments
    Collateral: None required

    Expected: Level-1 approval, no escalation needed
    """

    result1 = run_loan_processing(simple_loan)
    print(f"\nResult:\n{result1['result']}")

    # Example 2: Complex Case (Handoff to Specialist)
    print(f"\n\n{'='*80}")
    print("Example 2: Complex Loan - Specialist Required")
    print(f"{'='*80}\n")

    complex_loan = """
    Loan Application ID: APP_67890

    Applicant: Sarah Johnson
    Loan Amount: $125,000
    Purpose: Business expansion loan
    Credit Score: 680
    Employment: Self-employed business owner, 3 years
    Business Income: $180,000 (verified via tax returns)
    Debt-to-Income Ratio: 42%
    Credit History: One 30-day late payment 18 months ago
    Collateral: Business equipment valued at $150,000

    Complexity: Self-employed, DTI >40%, requires specialist underwriting
    Expected: Level-1 escalates to Specialist
    """

    result2 = run_loan_processing(complex_loan)
    print(f"\nResult:\n{result2['result']}")

    # Example 3: Edge Case (Full escalation chain)
    print(f"\n\n{'='*80}")
    print("Example 3: Edge Case - Senior Credit Officer Decision")
    print(f"{'='*80}\n")

    edge_case = """
    Loan Application ID: APP_99999

    Applicant: Michael Chen
    Loan Amount: $350,000
    Purpose: Real estate investment
    Credit Score: 625
    Employment: Self-employed, Real Estate Developer, 8 years
    Income: $250,000 (variable)
    Debt-to-Income Ratio: 52%
    Credit History: Chapter 7 bankruptcy 3 years ago (medical emergency)

    Compensating Factors:
    - High net worth: $1.2M in liquid assets
    - Significant investment property portfolio ($2.5M equity)
    - Post-bankruptcy: Perfect payment history (36 months)
    - Strong business track record
    - Strategic relationship: Has referred 15 customers

    Complexity: Credit score <650, DTI >50%, recent bankruptcy, high amount
    Expected: Level-1 → Specialist → Senior Credit Officer (full chain)
    """

    result3 = run_loan_processing(edge_case)
    print(f"\nResult:\n{result3['result']}")

    print(f"\n\n{'='*80}")
    print("Business Impact - RegionalBank:")
    print(f"{'='*80}")
    for metric, value in result1['business_metrics'].items():
        print(f"  {metric}: {value}")

    print(f"\n{'='*80}")
    print("Pattern Demonstrated: Handoff Orchestration")
    print(f"{'='*80}")
    print("""
Key Observations:
1. Dynamic Escalation Based on Complexity:
   - Simple loans (70%): Level-1 only, 2 hours
   - Complex loans (25%): Level-1 → Specialist, 4 hours
   - Edge cases (5%): Level-1 → Specialist → Expert, 6 hours
   - Right expertise for right complexity

2. Context Preservation:
   - Complete application context preserved across handoffs
   - No "please repeat your information" frustration
   - Each tier builds on previous analysis
   - Full audit trail maintained

3. Expertise Matching:
   - Level-1: Standard criteria, fast processing
   - Specialist: Advanced underwriting, compensating factors
   - Expert: Senior judgment, strategic considerations
   - Cost optimization: Use least expensive resource capable of decision

4. CrewAI Implementation:
   - allow_delegation=True enables handoffs
   - context parameter preserves analysis across tiers
   - Sequential process ensures proper escalation flow
   - Tasks can trigger delegation to more capable agents

5. Business Impact (RegionalBank):
   - Processing time: 3 days → 6 hours (-88%)
   - Accuracy: 94% → 97% (better expertise matching)
   - Compliance violations: -89% (proper tier review)
   - Revenue per officer: +220% (efficiency gains)

6. When to Use:
   - Variable complexity in requests
   - Tiered expertise available
   - Cost optimization important (use cheapest capable resource)
   - Quality improves with specialist attention
   - Context preservation critical for user experience

7. Advantages:
   - Optimizes resource allocation (70% handled by Level-1)
   - Improves accuracy (complex cases get expert attention)
   - Reduces processing time (no waiting for experts on simple cases)
   - Better compliance (appropriate review level)
   - Superior customer experience (context preservation)

8. Implementation Best Practices:
   - Clear escalation criteria for each tier
   - Complete context preservation (no information loss)
   - Defined processing time targets per tier
   - Audit trail of escalation decisions
   - Feedback loop to improve tier capabilities

9. Real-World Applications:
   - Loan origination (RegionalBank case)
   - Customer support (L1 → L2 → L3 support)
   - Technical debugging (Junior → Senior → Architect)
   - Medical diagnosis (Nurse → Doctor → Specialist)
   - Legal review (Paralegal → Attorney → Partner)
    """)


if __name__ == "__main__":
    # Set up API keys before running:
    # export OPENAI_API_KEY="your-openai-key"

    main()
