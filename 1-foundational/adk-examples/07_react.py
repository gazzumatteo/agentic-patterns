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

The ReAct pattern combines reasoning traces with task-specific actions, enabling
the agent to dynamically plan, execute, and adjust its approach based on observations.

Mermaid Diagram Reference: See diagrams/07_react.mermaid
"""

import asyncio
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Load environment variables
load_dotenv()


# ========================================
# SIMULATED HEALTHCARE TOOLS
# ========================================

class HealthcareTools:
    """Simulated healthcare information systems."""

    @staticmethod
    def query_ehr(patient_id: str, query_type: str) -> Dict:
        """Query Electronic Health Record system."""
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

        patient_data = ehr_data.get(patient_id, {})
        if query_type in patient_data:
            return {"success": True, "data": patient_data[query_type]}
        return {"success": True, "data": patient_data}

    @staticmethod
    def order_test(patient_id: str, test_type: str) -> Dict:
        """Order diagnostic test."""
        test_results = {
            "ECG": {
                "status": "ordered",
                "findings": "ST-segment elevation in leads II, III, aVF",
                "interpretation": "Suggestive of inferior wall MI"
            },
            "Troponin": {
                "status": "ordered",
                "value": "0.8 ng/mL",
                "reference": "<0.04 ng/mL",
                "interpretation": "Elevated - consistent with myocardial injury"
            },
            "CXR": {
                "status": "ordered",
                "findings": "No acute cardiopulmonary process",
                "interpretation": "Normal chest X-ray"
            }
        }

        result = test_results.get(test_type, {"status": "ordered", "result": "pending"})
        return {"success": True, "test": test_type, "result": result}

    @staticmethod
    def check_protocol(condition: str) -> Dict:
        """Retrieve clinical protocol for condition."""
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
        return {"success": True, "protocol": protocol}


# ========================================
# REACT AGENT DEFINITION
# ========================================

diagnostic_agent = LlmAgent(
    name="DiagnosticAssistant",
    model="gemini-2.5-flash",
    instruction="""
    You are a healthcare diagnostic assistant using the ReAct (Reason and Act) pattern.

    For each patient case, you must follow this exact cycle:

    1. THOUGHT: Reason about what you know and what you need to find out
    2. ACTION: Decide which tool to use and with what parameters
    3. OBSERVATION: Analyze the results from the action
    4. Repeat until you have enough information for a recommendation

    Available Tools:
    - query_ehr(patient_id, query_type): Query patient's electronic health record
      Query types: medical_history, current_medications, allergies, vital_signs_latest, or omit for all
    - order_test(patient_id, test_type): Order diagnostic tests
      Test types: ECG, Troponin, CXR, CBC, BMP
    - check_protocol(condition): Look up clinical protocols
      Conditions: MI, chest_pain, stroke, sepsis

    Format your response EXACTLY as follows:

    THOUGHT: [Your reasoning about the current situation]
    ACTION: [tool_name(patient_id, parameters)]
    ---WAIT FOR OBSERVATION---

    After receiving an observation, continue:
    OBSERVATION: [Analysis of the results]
    THOUGHT: [Updated reasoning based on observation]
    ACTION: [Next action] OR FINAL RECOMMENDATION: [Your clinical recommendation]

    Continue this cycle until you reach a FINAL RECOMMENDATION.

    CRITICAL: Follow clinical best practices and emergency protocols.
    """,
    description="ReAct-based diagnostic assistant"
)


# ========================================
# REACT EXECUTION ENGINE
# ========================================

async def execute_react_cycle(patient_id: str, presenting_complaint: str) -> List[Dict]:
    """Execute ReAct reasoning and action cycles."""

    tools = HealthcareTools()
    react_history = []

    # Initialize
    runner = InMemoryRunner(
        agent=diagnostic_agent,
        app_name="diagnostic_assistant"
    )

    session = await runner.session_service.create_session(
        app_name="diagnostic_assistant",
        user_id="clinician"
    )

    # Start with initial complaint
    initial_prompt = f"""
    Patient ID: {patient_id}
    Presenting Complaint: {presenting_complaint}

    Begin your ReAct cycle to diagnose and recommend appropriate action.
    """

    content = types.Content(
        role='user',
        parts=[types.Part(text=initial_prompt)]
    )

    max_cycles = 10
    cycle_count = 0

    while cycle_count < max_cycles:
        cycle_count += 1

        # Get agent's thought and action
        events = runner.run_async(
            user_id="clinician",
            session_id=session.id,
            new_message=content
        )

        agent_response = None
        async for event in events:
            if event.is_final_response() and event.content:
                agent_response = event.content.parts[0].text
                break

        if not agent_response:
            break

        react_history.append({
            "cycle": cycle_count,
            "type": "reasoning",
            "content": agent_response
        })

        print(f"\n{'='*80}")
        print(f"CYCLE {cycle_count}")
        print(f"{'='*80}")
        print(agent_response)

        # Check if we've reached a final recommendation
        if "FINAL RECOMMENDATION" in agent_response.upper():
            break

        # Parse and execute action
        observation = await execute_action(agent_response, tools, patient_id)

        if observation:
            react_history.append({
                "cycle": cycle_count,
                "type": "observation",
                "content": observation
            })

            print(f"\n{'-'*80}")
            print("OBSERVATION:")
            print(f"{'-'*80}")
            print(observation)

            # Provide observation to agent
            content = types.Content(
                role='user',
                parts=[types.Part(text=f"OBSERVATION: {observation}\n\nContinue your ReAct cycle.")]
            )
        else:
            break

    return react_history


async def execute_action(response: str, tools: HealthcareTools, patient_id: str) -> Optional[str]:
    """Parse and execute the action from agent's response."""

    # Simple parser for ACTION: line
    for line in response.split('\n'):
        if line.strip().startswith('ACTION:'):
            action_str = line.replace('ACTION:', '').strip()

            # Parse tool calls
            if 'query_ehr' in action_str:
                if 'medical_history' in action_str:
                    result = tools.query_ehr(patient_id, 'medical_history')
                elif 'current_medications' in action_str:
                    result = tools.query_ehr(patient_id, 'current_medications')
                else:
                    result = tools.query_ehr(patient_id, 'all')
                return json.dumps(result, indent=2)

            elif 'order_test' in action_str:
                if 'ECG' in action_str:
                    result = tools.order_test(patient_id, 'ECG')
                elif 'Troponin' in action_str:
                    result = tools.order_test(patient_id, 'Troponin')
                elif 'CXR' in action_str:
                    result = tools.order_test(patient_id, 'CXR')
                else:
                    return "ERROR: Test type not specified"
                return json.dumps(result, indent=2)

            elif 'check_protocol' in action_str:
                if 'MI' in action_str or 'myocardial' in action_str.lower():
                    result = tools.check_protocol('MI')
                elif 'chest_pain' in action_str.lower():
                    result = tools.check_protocol('chest_pain')
                else:
                    return "ERROR: Condition not specified"
                return json.dumps(result, indent=2)

    return None


# ========================================
# USAGE EXAMPLES
# ========================================

async def main():
    """Main execution demonstrating the ReAct pattern."""

    print(f"\n{'='*80}")
    print("Pattern 7: ReAct (Reason and Act)")
    print(f"{'='*80}\n")

    print("""
SCENARIO: Emergency Department
Patient presents with acute chest pain
The diagnostic agent will use ReAct to systematically evaluate the patient
    """)

    # Execute ReAct diagnostic process
    history = await execute_react_cycle(
        patient_id="PT_001",
        presenting_complaint="62-year-old male presenting with acute chest pain radiating to left arm, "
                           "onset 45 minutes ago, associated with diaphoresis and nausea"
    )

    # Summary
    print(f"\n\n{'='*80}")
    print("REACT CYCLE SUMMARY")
    print(f"{'='*80}")
    print(f"Total cycles: {len([h for h in history if h['type'] == 'reasoning'])}")
    print(f"Total observations: {len([h for h in history if h['type'] == 'observation'])}")

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
- Parsing thought/action/observation format
- Tool execution and error handling
- Cycle limit to prevent infinite loops
- Context management across cycles
- Integration with existing clinical systems
- Compliance with healthcare regulations (HIPAA)

Clinical Impact (Hospital Network):
- Faster time to treatment for STEMI cases
- Reduced door-to-balloon times
- Improved adherence to clinical protocols
- Better resource utilization in ED
- Enhanced clinical decision support
    """)


if __name__ == "__main__":
    asyncio.run(main())
