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

Chain-of-Thought prompting encourages the model to break down complex reasoning
into transparent, verifiable steps - critical for audit trails and compliance.

Mermaid Diagram Reference: See diagrams/08_chain_of_thought.mermaid
"""

import asyncio
from typing import Dict, List
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Load environment variables
load_dotenv()


# ========================================
# CHAIN-OF-THOUGHT AGENT DEFINITION
# ========================================

audit_agent = LlmAgent(
    name="ExpenseAuditAgent",
    model="gemini-2.5-flash",
    instruction="""
    You are a financial audit agent specializing in expense report validation.

    You MUST use Chain-of-Thought reasoning for every audit. Follow this format:

    AUDIT REPORT FOR: [Expense Item]

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

    Key Company Policies:
    - Meals: $75/day limit, $50/meal limit, requires itemized receipt
    - Transportation: Reasonable rates, original receipts required
    - Lodging: Up to $200/night for standard cities, $350 for high-cost cities
    - Equipment: Pre-approval required for items >$500
    - Entertainment: Must have business purpose, attendee list required
    - Personal expenses: Strictly prohibited

    Red Flags:
    - Round numbers (suggests estimation)
    - Duplicate expenses
    - Weekend charges without business justification
    - Missing or altered receipts
    - Expenses outside employee's territory/role
    - Amounts just under approval thresholds

    Be thorough, fair, and transparent in your reasoning.
    """,
    description="Chain-of-Thought based expense auditor"
)


# ========================================
# USAGE EXAMPLES
# ========================================

async def audit_expense(expense: Dict) -> str:
    """Audit an expense report using Chain-of-Thought reasoning."""

    # Create runner
    runner = InMemoryRunner(
        agent=audit_agent,
        app_name="expense_auditor"
    )

    # Create session
    session = await runner.session_service.create_session(
        app_name="expense_auditor",
        user_id="auditor"
    )

    # Format expense for audit
    expense_details = f"""
    Please audit the following expense claim:

    Expense ID: {expense['id']}
    Employee: {expense['employee']}
    Role: {expense['role']}
    Date: {expense['date']}
    Category: {expense['category']}
    Amount: ${expense['amount']}
    Description: {expense['description']}
    Receipt Provided: {expense['receipt_provided']}
    Receipt Details: {expense.get('receipt_details', 'N/A')}
    Business Purpose: {expense.get('business_purpose', 'Not specified')}
    """

    # Prepare message
    content = types.Content(
        role='user',
        parts=[types.Part(text=expense_details)]
    )

    # Run agent
    events = runner.run_async(
        user_id="auditor",
        session_id=session.id,
        new_message=content
    )

    # Collect response
    async for event in events:
        if event.is_final_response() and event.content:
            audit_result = event.content.parts[0].text
            return audit_result

    return None


async def main():
    """Main execution demonstrating the Chain-of-Thought pattern."""

    print(f"\n{'='*80}")
    print("Pattern 8: Chain-of-Thought (CoT)")
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

        result = await audit_expense(expense)
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
    """)


if __name__ == "__main__":
    asyncio.run(main())
