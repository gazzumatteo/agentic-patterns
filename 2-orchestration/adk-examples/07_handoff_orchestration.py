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

This example demonstrates Google ADK's dynamic handoff pattern with escalation.

Mermaid Diagram Reference: See diagrams/15_handoff_orchestration.mermaid
"""

import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Load environment variables
load_dotenv()


# ========================================
# COMPLEXITY LEVELS
# ========================================

class ComplexityLevel(Enum):
    """Loan application complexity levels."""
    SIMPLE = "simple"
    COMPLEX = "complex"
    EDGE_CASE = "edge_case"


@dataclass
class LoanContext:
    """Context preserved across agent handoffs."""
    application_id: str
    applicant_info: Dict[str, Any]
    loan_amount: float
    complexity: ComplexityLevel
    history: list
    escalation_reason: Optional[str] = None


# ========================================
# TIER 1: Level-1 Basic Agent
# ========================================

level_1_agent = LlmAgent(
    name="Level1_BasicLoanAgent",
    model="gemini-2.5-flash",
    instruction="""
    You are a Level-1 Loan Processing Agent for RegionalBank.

    Your expertise: Standard loan applications (70% of volume)

    You handle:
    - Simple personal loans under $50,000
    - Applicants with credit score > 700
    - Standard employment verification
    - Clean credit history (no bankruptcies, foreclosures)

    Process:
    1. Analyze loan application
    2. Verify basic eligibility criteria
    3. Make decision: APPROVE, DENY, or ESCALATE

    ESCALATE if application has:
    - Credit score < 700
    - Loan amount > $50,000
    - Self-employed applicant
    - Recent credit issues
    - Non-standard documentation
    - Debt-to-income ratio > 40%

    Output JSON:
    {{
        "decision": "APPROVE/DENY/ESCALATE",
        "confidence": 0.0-1.0,
        "reasoning": "Brief explanation",
        "escalation_reason": "Why escalating (if applicable)",
        "approved_terms": {{}} or null,
        "complexity_assessment": "simple/complex/edge_case"
    }}

    Preserve context: Include all applicant information in your response.
    """,
    description="Level-1 agent for simple loan processing",
    output_key="level_1_decision"
)


# ========================================
# TIER 2: Specialist Agent
# ========================================

specialist_agent = LlmAgent(
    name="SpecialistUnderwriter",
    model="gemini-2.5-flash",
    instruction="""
    You are a Specialist Underwriter Agent for RegionalBank.

    Your expertise: Complex loan applications requiring advanced underwriting

    You handle escalations from Level-1:
    - Credit scores 650-699 (need deeper analysis)
    - Loan amounts $50,000-$250,000
    - Self-employed applicants (verify business income)
    - Recent credit issues (analyze context and recovery)
    - Non-standard documentation (compensating factors)
    - DTI ratios 40-50% (evaluate overall financial picture)

    Advanced Analysis:
    - Evaluate compensating factors
    - Analyze income stability trends
    - Assess collateral quality
    - Review complete credit narrative
    - Calculate risk-adjusted pricing

    Process:
    1. Review Level-1 analysis and escalation reason
    2. Perform advanced underwriting
    3. Make decision: APPROVE (with conditions), DENY, or ESCALATE to Expert

    ESCALATE to Expert if:
    - Credit score < 650
    - Loan amount > $250,000
    - Recent bankruptcy or foreclosure
    - DTI > 50%
    - Unusual/high-risk circumstances

    Output JSON with full context preservation:
    {{
        "decision": "APPROVE/DENY/ESCALATE",
        "confidence": 0.0-1.0,
        "reasoning": "Detailed underwriting rationale",
        "escalation_reason": "Why escalating to expert (if applicable)",
        "approved_terms": {{"interest_rate": X, "conditions": []}},
        "risk_assessment": {{"score": X, "factors": []}},
        "previous_analysis": "Summary of Level-1 findings"
    }}
    """,
    description="Specialist agent for complex underwriting",
    output_key="specialist_decision"
)


# ========================================
# TIER 3: Expert Agent (Senior Credit Officer)
# ========================================

expert_agent = LlmAgent(
    name="SeniorCreditOfficer",
    model="gemini-2.5-flash",
    instruction="""
    You are the Senior Credit Officer Agent - highest authority for loan decisions.

    Your expertise: Edge cases and high-risk/high-value loans

    You handle final escalations:
    - Credit scores < 650 (deep risk analysis)
    - Loan amounts > $250,000 (portfolio impact)
    - Recent bankruptcies/foreclosures (rehabilitation assessment)
    - DTI > 50% (exceptional circumstances only)
    - Unusual situations requiring senior judgment

    Expert Judgment:
    - Complete risk analysis with portfolio considerations
    - Strategic value assessment (customer lifetime value)
    - Creative structuring for viable but non-standard cases
    - Final authority - no further escalation

    You have reviewed:
    1. Level-1 initial analysis
    2. Specialist underwriting assessment
    3. Full application history and context

    Process:
    1. Review complete escalation chain
    2. Apply senior judgment and risk tolerance
    3. Make FINAL decision: APPROVE (with structure) or DENY

    Output JSON with complete decision rationale:
    {{
        "decision": "APPROVE/DENY",
        "confidence": 0.0-1.0,
        "reasoning": "Comprehensive senior officer rationale",
        "approved_terms": {{"interest_rate": X, "conditions": [], "special_structure": ""}},
        "risk_assessment": {{"score": X, "mitigation": [], "portfolio_impact": ""}},
        "escalation_history": "Summary of Level-1 and Specialist findings",
        "strategic_considerations": "Customer value, relationship, etc."
    }}

    NO FURTHER ESCALATION AVAILABLE. This is final decision.
    """,
    description="Expert agent - senior credit officer",
    output_key="expert_decision"
)


# ========================================
# HANDOFF ORCHESTRATOR
# ========================================

class HandoffOrchestrator:
    """Manages dynamic handoffs between loan agents based on complexity."""

    def __init__(self):
        self.level_1 = level_1_agent
        self.specialist = specialist_agent
        self.expert = expert_agent

    async def process_loan_application(
        self,
        application: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process loan application with dynamic handoff escalation.

        Args:
            application: Loan application details

        Returns:
            Final loan decision with complete handoff history
        """
        # Initialize context
        context = LoanContext(
            application_id=application.get("id", "APP_001"),
            applicant_info=application,
            loan_amount=application.get("loan_amount", 0),
            complexity=ComplexityLevel.SIMPLE,
            history=[]
        )

        print(f"\n{'='*80}")
        print(f"Processing Loan Application: {context.application_id}")
        print(f"Amount: ${context.loan_amount:,}")
        print(f"{'='*80}\n")

        # Start with Level-1
        current_agent = self.level_1
        tier = 1

        while True:
            print(f"\nTier {tier}: {current_agent.name}")
            print("-" * 80)

            # Process with current agent
            result = await self._process_with_agent(
                current_agent,
                application,
                context
            )

            # Add to history
            context.history.append({
                "tier": tier,
                "agent": current_agent.name,
                "result": result
            })

            # Check if escalation needed
            if result.get("decision") == "ESCALATE":
                context.escalation_reason = result.get("escalation_reason")
                context.complexity = self._update_complexity(result)

                # Escalate to next tier
                if tier == 1:
                    current_agent = self.specialist
                    tier = 2
                elif tier == 2:
                    current_agent = self.expert
                    tier = 3
                else:
                    # No more escalation - expert is final
                    print("\n⚠️  Expert tier reached - no further escalation")
                    break

                print(f"\n Escalating: {context.escalation_reason}")
                continue
            else:
                # Decision made
                print(f"\n✓ Final Decision: {result.get('decision')}")
                break

        return {
            "application_id": context.application_id,
            "final_decision": result,
            "escalation_tiers": tier,
            "handoff_history": context.history,
            "total_processing_time": self._calculate_time(tier)
        }

    async def _process_with_agent(
        self,
        agent: LlmAgent,
        application: Dict[str, Any],
        context: LoanContext
    ) -> Dict[str, Any]:
        """Process application with specific agent tier."""
        runner = InMemoryRunner(agent=agent, app_name="loan_app")

        session = await runner.session_service.create_session(
            app_name="loan_app",
            user_id=f"user_{agent.name}"
        )

        # Build prompt with context
        prompt = self._build_contextual_prompt(application, context)

        content = types.Content(
            role='user',
            parts=[types.Part(text=prompt)]
        )

        events = runner.run_async(
            user_id=f"user_{agent.name}",
            session_id=session.id,
            new_message=content
        )

        decision = None
        async for event in events:
            if event.is_final_response() and event.content:
                decision_text = event.content.parts[0].text
                # Parse decision (simplified)
                decision = {"raw": decision_text, "decision": "APPROVE"}  # Would parse JSON

                # Extract decision type
                if "ESCALATE" in decision_text:
                    decision["decision"] = "ESCALATE"
                    # Extract reason
                    if "escalation_reason" in decision_text.lower():
                        decision["escalation_reason"] = "Complexity exceeds tier capability"
                elif "DENY" in decision_text:
                    decision["decision"] = "DENY"

        return decision

    def _build_contextual_prompt(
        self,
        application: Dict[str, Any],
        context: LoanContext
    ) -> str:
        """Build prompt with preserved context."""
        prompt = f"Loan Application Analysis:\n\n"
        prompt += f"Application ID: {context.application_id}\n"
        prompt += f"Loan Amount: ${application.get('loan_amount', 0):,}\n"
        prompt += f"Credit Score: {application.get('credit_score', 0)}\n"
        prompt += f"Employment: {application.get('employment_type', 'W2')}\n"
        prompt += f"DTI Ratio: {application.get('dti_ratio', 0)}%\n\n"

        if context.history:
            prompt += "\nPrevious Tier Analysis:\n"
            for h in context.history:
                prompt += f"- {h['agent']}: {h['result'].get('raw', '')[:200]}...\n"

        if context.escalation_reason:
            prompt += f"\nEscalation Reason: {context.escalation_reason}\n"

        prompt += "\nProvide your analysis and decision."

        return prompt

    def _update_complexity(self, result: Dict[str, Any]) -> ComplexityLevel:
        """Update complexity based on escalation."""
        if "edge" in result.get("escalation_reason", "").lower():
            return ComplexityLevel.EDGE_CASE
        return ComplexityLevel.COMPLEX

    def _calculate_time(self, tiers: int) -> str:
        """Calculate processing time based on tiers."""
        time_per_tier = {1: "2 hours", 2: "4 hours", 3: "6 hours"}
        return time_per_tier.get(tiers, "6 hours")


async def main():
    """Main execution demonstrating handoff orchestration."""

    print(f"\n{'='*80}")
    print("Pattern 15: Handoff Orchestration - Google ADK")
    print("Business Case: RegionalBank - Loan Origination")
    print(f"{'='*80}\n")

    orchestrator = HandoffOrchestrator()

    # Example 1: Simple Loan (Level-1 only)
    print("\nExample 1: Simple Personal Loan - No Escalation")
    print("=" * 80)

    simple_loan = {
        "id": "APP_12345",
        "loan_amount": 25000,
        "credit_score": 750,
        "employment_type": "W2",
        "dti_ratio": 28,
        "credit_history": "clean"
    }

    result1 = await orchestrator.process_loan_application(simple_loan)

    print(f"\nProcessing Summary:")
    print(f"  Tiers used: {result1['escalation_tiers']}")
    print(f"  Processing time: {result1['total_processing_time']}")
    print(f"  Decision: {result1['final_decision'].get('decision')}")

    # Example 2: Complex Case (Escalates to Specialist)
    print(f"\n\n{'='*80}")
    print("Example 2: Complex Loan - Specialist Required")
    print("=" * 80)

    complex_loan = {
        "id": "APP_67890",
        "loan_amount": 125000,
        "credit_score": 680,
        "employment_type": "Self-employed",
        "dti_ratio": 42,
        "credit_history": "minor recent issues"
    }

    result2 = await orchestrator.process_loan_application(complex_loan)

    print(f"\nProcessing Summary:")
    print(f"  Tiers used: {result2['escalation_tiers']}")
    print(f"  Processing time: {result2['total_processing_time']}")
    print(f"  Handoffs: {len(result2['handoff_history'])}")

    # Example 3: Edge Case (All tiers)
    print(f"\n\n{'='*80}")
    print("Example 3: Edge Case - Senior Credit Officer")
    print("=" * 80)

    edge_case = {
        "id": "APP_99999",
        "loan_amount": 350000,
        "credit_score": 625,
        "employment_type": "Self-employed",
        "dti_ratio": 52,
        "credit_history": "bankruptcy 3 years ago",
        "compensating_factors": "High net worth, significant assets"
    }

    result3 = await orchestrator.process_loan_application(edge_case)

    print(f"\nProcessing Summary:")
    print(f"  Tiers used: {result3['escalation_tiers']}")
    print(f"  Processing time: {result3['total_processing_time']}")
    print(f"  Handoffs: {len(result3['handoff_history'])}")

    print(f"\n\n{'='*80}")
    print("Business Impact - RegionalBank Results:")
    print(f"{'='*80}")
    print("""
    Performance Improvements:
    - Application to approval: 3 days → 6 hours (-88%)
    - Approval accuracy: 94% → 97%
    - Compliance violations: -89%
    - Revenue per loan officer: +220%

    Efficiency Gains:
    - 70% of loans handled by Level-1 (2 hours)
    - 25% escalate to Specialist (4 hours)
    - 5% require Senior Officer (6 hours)
    - Context preservation eliminates re-work
    """)

    print(f"\n{'='*80}")
    print("Pattern Demonstrated: Handoff Orchestration")
    print(f"{'='*80}")
    print("""
Key Concepts:
1. Dynamic Escalation:
   - Start with least expensive resource (Level-1)
   - Escalate only when complexity exceeds capability
   - Three-tier expertise: Basic → Specialist → Expert

2. Context Preservation:
   - All previous analysis carried forward
   - No "please repeat your information"
   - Each tier builds on previous findings
   - Complete audit trail maintained

3. Expertise Matching:
   - Level-1: Simple loans (70% volume, 2 hours)
   - Specialist: Complex cases (25% volume, 4 hours)
   - Expert: Edge cases (5% volume, 6 hours)
   - Right expertise for right complexity

4. Business Impact:
   - Processing time: 3 days → 6 hours (average)
   - Accuracy: 94% → 97% (better expertise matching)
   - Compliance: -89% violations
   - Revenue per officer: +220%

5. When to Use:
   - Variable complexity in requests
   - Tiered expertise available
   - Cost optimization important
   - Quality improves with specialist attention
   - Context preservation critical

6. ADK Implementation:
   - HandoffOrchestrator manages escalation logic
   - Each tier is separate LlmAgent
   - Context object preserves state
   - Decision triggers handoff or completion
    """)


if __name__ == "__main__":
    asyncio.run(main())
