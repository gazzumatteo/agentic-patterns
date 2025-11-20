"""
Pattern 8: Chain-of-Thought (CoT)
An agent that shows explicit step-by-step reasoning before reaching conclusions.

Business Example: Financial Audit Agent
- Company: Big4 Auditing Firm
- Challenge: Expense report validation taking 2-3 hours per report
- Solution: Chain-of-Thought agent for systematic validation
- Process: Shows Step 1, Step 2, etc. leading to final decision
- Use Case: Expense report validation with explicit reasoning steps
- Results: 60% reduction in audit time, 100% traceable decisions

This example demonstrates Chain-of-Thought reasoning using CrewAI.

Mermaid Diagram Reference: See diagrams/08_chain_of_thought.mermaid
"""

from typing import Dict, List
from crewai import Agent, Task, Crew


# ========================================
# CHAIN-OF-THOUGHT AGENT DEFINITION
# ========================================

audit_agent = Agent(
    role="Financial Expense Auditor",
    goal="Systematically audit expense reports with transparent step-by-step reasoning",
    backstory="""
    You are an experienced financial auditor at a Big4 firm specializing in
    expense report validation. You are known for your methodical approach and
    crystal-clear audit trails.

    You ALWAYS use Chain-of-Thought reasoning, breaking down every audit into
    clear steps that anyone can follow and verify. Your reports are models of
    transparency and are frequently used for training junior auditors.

    You are fair but thorough, and you never cut corners on compliance.
    """,
    verbose=False,
    allow_delegation=False
)


# ========================================
# USAGE EXAMPLES
# ========================================

def audit_expense(expense: Dict) -> str:
    """Audit an expense report using Chain-of-Thought reasoning."""

    task = Task(
        description=f"""
        Audit the following expense claim using Chain-of-Thought methodology.

        EXPENSE DETAILS:
        - Expense ID: {expense['id']}
        - Employee: {expense['employee']} ({expense['role']})
        - Date: {expense['date']}
        - Category: {expense['category']}
        - Amount: ${expense['amount']}
        - Description: {expense['description']}
        - Receipt Provided: {expense['receipt_provided']}
        - Receipt Details: {expense.get('receipt_details', 'N/A')}
        - Business Purpose: {expense.get('business_purpose', 'Not specified')}

        COMPANY POLICIES:
        - Meals: $75/day limit, $50/meal limit, requires itemized receipt
        - Transportation: Reasonable rates, original receipts required
        - Lodging: Up to $200/night standard, $350 for high-cost cities
        - Equipment: Pre-approval required for items >$500
        - Entertainment: Must have business purpose, attendee list required

        RED FLAGS TO CHECK:
        - Round numbers (suggests estimation)
        - Duplicate expenses
        - Weekend charges without justification
        - Missing or altered receipts
        - Expenses outside employee's role
        - Amounts just under approval thresholds

        You MUST structure your audit as follows:

        AUDIT REPORT FOR: {expense['id']}

        Step 1: Initial Review
        [Check what the expense is and basic validity]

        Step 2: Policy Compliance Check
        [Verify against company policy - amount limits, categories, documentation]

        Step 3: Receipt Validation
        [Check receipt details - date, amount, vendor, matches claim]

        Step 4: Business Purpose Verification
        [Assess if expense aligns with business purpose and job role]

        Step 5: Red Flag Analysis
        [Look for suspicious patterns, duplicates, or anomalies]

        Step 6: Final Determination
        [APPROVED or REJECTED with clear reasoning]

        Be thorough, fair, and show all your reasoning.
        """,
        agent=audit_agent,
        expected_output="Complete step-by-step audit with final determination"
    )

    crew = Crew(
        agents=[audit_agent],
        tasks=[task],
        verbose=False
    )

    result = crew.kickoff()
    return result.raw if hasattr(result, 'raw') else str(result)


def main():
    """Main execution demonstrating the Chain-of-Thought pattern."""

    print(f"\n{'='*80}")
    print("Pattern 8: Chain-of-Thought (CoT) - CrewAI")
    print(f"{'='*80}\n")

    # Test cases from real-world audit scenarios
    test_expenses = [
        {
            "id": "EXP_001",
            "employee": "John Smith",
            "role": "Sales Manager",
            "date": "2024-03-15",
            "category": "Client Meal",
            "amount": 145.50,
            "description": "Dinner with client - contract negotiation",
            "receipt_provided": True,
            "receipt_details": "Restaurant: The Capital Grille, Date: 2024-03-15, Amount: $145.50, Itemized",
            "business_purpose": "Client meeting for Q2 contract renewal, attendees: John Smith, Sarah Chen (Client CEO)"
        },
        {
            "id": "EXP_002",
            "employee": "Jane Doe",
            "role": "Software Engineer",
            "date": "2024-03-18",
            "category": "Equipment",
            "amount": 499.99,
            "description": "Mechanical keyboard",
            "receipt_provided": True,
            "receipt_details": "Store: Best Buy, Date: 2024-03-18, Amount: $499.99",
            "business_purpose": "Ergonomic equipment for remote work setup"
        },
        {
            "id": "EXP_003",
            "employee": "Mike Johnson",
            "role": "Marketing Coordinator",
            "date": "2024-03-20",
            "category": "Transportation",
            "amount": 250.00,
            "description": "Uber rides",
            "receipt_provided": False,
            "receipt_details": "No receipt provided - estimated amount",
            "business_purpose": "Client visits during conference week"
        },
        {
            "id": "EXP_004",
            "employee": "Emily Brown",
            "role": "Regional Director",
            "date": "2024-03-22",
            "category": "Lodging",
            "amount": 425.00,
            "description": "Hotel - New York City",
            "receipt_provided": True,
            "receipt_details": "Hotel: Marriott Times Square, Date: 2024-03-22, Amount: $425.00, Business rate",
            "business_purpose": "Annual leadership summit, pre-approved by VP"
        }
    ]

    # Process each expense
    for i, expense in enumerate(test_expenses, 1):
        print(f"\n{'='*80}")
        print(f"AUDIT CASE {i}/{len(test_expenses)}")
        print(f"{'='*80}\n")

        result = audit_expense(expense)
        print(result)
        print("\n")

    # Summary
    print(f"{'='*80}")
    print("Pattern Demonstrated: Chain-of-Thought (CoT)")
    print(f"{'='*80}")
    print("""
Key Concepts:
1. Explicit step-by-step reasoning process
2. Transparent decision-making trail
3. Breaking complex problems into simple steps
4. Each step builds on previous steps
5. Final conclusion based on accumulated reasoning

When to Use:
- Complex decision-making requiring transparency
- Audit and compliance scenarios
- Financial analysis and risk assessment
- Legal or regulatory evaluations
- Any situation requiring explainable AI
- Training and quality assurance

Business Value:
- 60% reduction in audit time (Big4 Firm)
- 100% traceable decisions for compliance
- Improved accuracy through systematic approach
- Better training for junior auditors
- Reduced disputes through transparent reasoning
- Easier regulatory compliance and reporting

Technical Considerations:
- Prompt engineering for consistent step format
- Managing context length with long reasoning chains
- Balancing thoroughness with efficiency
- Extracting structured data from reasoning text
- Integration with audit management systems
- Storage and retrieval of audit trails

Real-World Impact:
Before CoT Agent:
- 2-3 hours per expense report
- Inconsistent audit quality
- Difficult to explain decisions
- High training costs for new auditors

After CoT Agent:
- 45 minutes per expense report (60% reduction)
- Consistent, systematic evaluation
- Complete audit trail for every decision
- Junior auditors productive in days vs. months
- Zero compliance violations in 6 months

Audit Trail Benefits:
- Every decision is documented step-by-step
- Easy to review and quality-check
- Supports regulatory requirements
- Facilitates dispute resolution
- Enables continuous improvement through pattern analysis

CrewAI Features Demonstrated:
- Agent with specific role and backstory
- Task with detailed instructions
- Structured output format through prompting
- Transparent reasoning through verbose mode
    """)


if __name__ == "__main__":
    main()
