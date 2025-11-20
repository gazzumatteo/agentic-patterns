"""
Pattern 7: ReAct (Reason and Act)
An agent that alternates between reasoning and action in iterative cycles.

Business Example: Healthcare Diagnostic Assistant
- Organization: Regional Hospital Network (12 facilities)
- Challenge: Critical cases requiring rapid information synthesis across multiple systems
- Solution: ReAct agent for diagnostic support
- Flow: Thought -> Action -> Observation -> Updated Thought
- Example: Patient with chest pain -> Query EHR -> Find cardiac history -> Order ECG
- Impact: 31% reduction in critical case response time

This example demonstrates the ReAct pattern using CrewAI with tool integration.

Mermaid Diagram Reference: See diagrams/07_react.mermaid
"""

import json
from typing import Dict
from crewai import Agent, Task, Crew
from crewai.tools import tool


# ========================================
# SIMULATED HEALTHCARE TOOLS
# ========================================

@tool("Query Electronic Health Record")
def query_ehr(patient_id: str) -> str:
    """
    Query patient's Electronic Health Record for medical history, medications, and vital signs.

    Args:
        patient_id: The patient's unique identifier

    Returns:
        JSON string containing patient medical information
    """
    # Simulated patient database
    ehr_data = {
        "PT_001": {
            "medical_history": [
                "Hypertension (diagnosed 2018)",
                "Type 2 Diabetes (diagnosed 2020)",
                "Previous MI (2019)"
            ],
            "current_medications": [
                "Metformin 1000mg BID",
                "Lisinopril 10mg QD",
                "Aspirin 81mg QD",
                "Atorvastatin 40mg QD"
            ],
            "allergies": ["Penicillin"],
            "vital_signs_latest": {
                "BP": "145/92",
                "HR": "88",
                "Temp": "98.6F",
                "SpO2": "96%"
            }
        }
    }

    patient_data = ehr_data.get(patient_id, {"error": "Patient not found"})
    return json.dumps(patient_data, indent=2)


@tool("Order Diagnostic Test")
def order_test(test_type: str) -> str:
    """
    Order a diagnostic test for the patient.

    Args:
        test_type: Type of test to order (ECG, Troponin, CXR, CBC, BMP)

    Returns:
        JSON string containing test results
    """
    test_results = {
        "ECG": {
            "status": "completed",
            "findings": "ST-segment elevation in leads II, III, aVF",
            "interpretation": "Suggestive of inferior wall MI"
        },
        "Troponin": {
            "status": "completed",
            "value": "0.8 ng/mL",
            "reference": "<0.04 ng/mL",
            "interpretation": "Elevated - consistent with myocardial injury"
        },
        "CXR": {
            "status": "completed",
            "findings": "No acute cardiopulmonary process",
            "interpretation": "Normal chest X-ray"
        }
    }

    result = test_results.get(test_type.upper(), {"status": "ordered", "result": "pending"})
    return json.dumps({"test": test_type, "result": result}, indent=2)


@tool("Check Clinical Protocol")
def check_protocol(condition: str) -> str:
    """
    Retrieve clinical protocol for a specific condition.

    Args:
        condition: Medical condition (MI, chest_pain, stroke, sepsis)

    Returns:
        JSON string containing protocol information
    """
    protocols = {
        "MI": {
            "protocol": "STEMI Protocol",
            "steps": [
                "1. Activate cath lab",
                "2. Aspirin 325mg PO",
                "3. Clopidogrel 600mg loading dose",
                "4. Heparin bolus + infusion",
                "5. Transfer to cath lab for PCI"
            ],
            "time_target": "Door-to-balloon < 90 minutes"
        },
        "chest_pain": {
            "protocol": "Chest Pain Evaluation",
            "steps": [
                "1. 12-lead ECG within 10 minutes",
                "2. Cardiac biomarkers (Troponin)",
                "3. Chest X-ray",
                "4. Continuous cardiac monitoring",
                "5. Risk stratification (HEART score)"
            ]
        }
    }

    protocol = protocols.get(condition, {"protocol": "Standard evaluation"})
    return json.dumps({"condition": condition, "protocol": protocol}, indent=2)


# ========================================
# REACT AGENT DEFINITION
# ========================================

diagnostic_agent = Agent(
    role="Healthcare Diagnostic Assistant",
    goal="Systematically diagnose patient conditions using ReAct methodology",
    backstory="""
    You are an experienced clinical decision support system trained in the
    ReAct (Reason and Act) methodology. You systematically approach each case by:

    1. THINKING about what you know and what you need to find out
    2. ACTING by using available diagnostic tools
    3. OBSERVING the results
    4. Updating your THINKING based on observations
    5. Repeating until reaching a clinical recommendation

    You have access to electronic health records, can order diagnostic tests,
    and can look up clinical protocols. You always follow evidence-based
    medicine and emergency protocols.
    """,
    tools=[query_ehr, order_test, check_protocol],
    verbose=True,
    allow_delegation=False
)


# ========================================
# USAGE EXAMPLES
# ========================================

def diagnose_patient(patient_id: str, presenting_complaint: str) -> str:
    """Execute ReAct diagnostic process for a patient."""

    task = Task(
        description=f"""
        Patient ID: {patient_id}
        Presenting Complaint: {presenting_complaint}

        Using the ReAct (Reason and Act) methodology, systematically evaluate this patient:

        1. THINK: What do I know? What do I need to find out?
        2. ACT: Use the appropriate tool (query_ehr, order_test, check_protocol)
        3. OBSERVE: Analyze the results
        4. REPEAT: Continue until you have enough information

        Your response should clearly show your reasoning at each step.

        Provide a FINAL RECOMMENDATION including:
        - Most likely diagnosis
        - Recommended immediate actions
        - Any relevant clinical protocols to follow
        - Time-sensitive considerations

        Be thorough but efficient - this is an emergency department setting.
        """,
        agent=diagnostic_agent,
        expected_output="Complete diagnostic assessment with reasoning and recommendation"
    )

    crew = Crew(
        agents=[diagnostic_agent],
        tasks=[task],
        verbose=True
    )

    result = crew.kickoff()
    return result.raw if hasattr(result, 'raw') else str(result)


def main():
    """Main execution demonstrating the ReAct pattern."""

    print(f"\n{'='*80}")
    print("Pattern 7: ReAct (Reason and Act) - CrewAI")
    print(f"{'='*80}\n")

    print("""
SCENARIO: Emergency Department
Patient presents with acute chest pain
The diagnostic agent will use ReAct to systematically evaluate the patient
    """)

    # Execute ReAct diagnostic process
    print(f"\n{'='*80}")
    print("REACT DIAGNOSTIC PROCESS")
    print(f"{'='*80}\n")

    result = diagnose_patient(
        patient_id="PT_001",
        presenting_complaint=(
            "62-year-old male presenting with acute chest pain radiating to left arm, "
            "onset 45 minutes ago, associated with diaphoresis and nausea"
        )
    )

    print(f"\n{'='*80}")
    print("FINAL DIAGNOSTIC REPORT")
    print(f"{'='*80}")
    print(result)

    print(f"\n{'='*80}")
    print("Pattern Demonstrated: ReAct (Reason and Act)")
    print(f"{'='*80}")
    print("""
Key Concepts:
1. Iterative cycle of Thought -> Action -> Observation
2. Explicit reasoning traces before each action
3. Dynamic planning based on observations
4. Tool use integrated with reasoning
5. Self-directed problem-solving approach

When to Use:
- Complex diagnostic or investigative tasks
- Multi-step problem-solving requiring tool use
- Situations needing dynamic planning
- Cases where reasoning transparency is important
- Tasks requiring evidence-based decision making

Business Value:
- 31% reduction in critical case response time
- Improved diagnostic accuracy through systematic approach
- Complete audit trail of reasoning process
- Better training tool for junior staff
- Reduced medical errors through structured methodology

Technical Considerations:
- Tool integration and error handling
- Reasoning transparency for clinical audit
- Integration with existing EHR systems
- Compliance with healthcare regulations (HIPAA)
- Performance in time-critical situations

Clinical Impact (Hospital Network):
- Faster time to treatment for STEMI cases
- Reduced door-to-balloon times
- Improved adherence to clinical protocols
- Better resource utilization in ED
- Enhanced clinical decision support

CrewAI Features Demonstrated:
- Tool decorator for function-based tools
- Agent with multiple tools
- Verbose mode showing reasoning process
- Integration of external systems (simulated EHR)
    """)


if __name__ == "__main__":
    main()
