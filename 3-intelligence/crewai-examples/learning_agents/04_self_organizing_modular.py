"""
Pattern 22: Self-Organizing Modular Agent (CrewAI Implementation)
An agent system that dynamically creates, removes, and reorganizes sub-agents based on workload and requirements.

Business Use Case: Cloud Service Auto-Scaling Support System
- Monitors incoming support tickets
- Automatically spawns specialist agents for different issue types
- Scales agent count based on load
- Removes idle agents to save costs

Key Concepts:
1. Dynamic agent creation/destruction
2. Load-based module scaling
3. Automatic capability detection
4. Self-optimization of agent structure

Mermaid Diagram Reference: See diagrams/22_self_organizing_modular.mermaid
"""

import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool


# ========================================
# MODULE DEFINITION
# ========================================

@dataclass
class AgentModule:
    """Represents a dynamically created agent module."""
    module_id: str
    specialty: str
    agent: Agent
    created_at: datetime
    tasks_handled: int = 0
    last_active: datetime = field(default_factory=datetime.now)
    avg_response_time: float = 0.0
    success_rate: float = 1.0

    def update_metrics(self, response_time: float, success: bool):
        """Update module performance metrics."""
        self.tasks_handled += 1
        self.last_active = datetime.now()

        # Update average response time
        self.avg_response_time = (
            (self.avg_response_time * (self.tasks_handled - 1) + response_time)
            / self.tasks_handled
        )

        # Update success rate
        if success:
            self.success_rate = (
                (self.success_rate * (self.tasks_handled - 1) + 1.0)
                / self.tasks_handled
            )
        else:
            self.success_rate = (
                (self.success_rate * (self.tasks_handled - 1))
                / self.tasks_handled
            )


# ========================================
# WORKLOAD TRACKER
# ========================================

@dataclass
class WorkloadMetrics:
    """Tracks system workload for scaling decisions."""
    pending_tasks: Dict[str, int] = field(default_factory=dict)  # specialty -> count
    active_modules: Dict[str, int] = field(default_factory=dict)  # specialty -> count

    def should_scale_up(self, specialty: str, threshold: int = 3) -> bool:
        """Determine if we need more agents for a specialty."""
        pending = self.pending_tasks.get(specialty, 0)
        active = self.active_modules.get(specialty, 0)

        if active == 0:
            return pending > 0
        return pending > (threshold * active)

    def should_scale_down(self, specialty: str, module: AgentModule, idle_threshold: int = 60) -> bool:
        """Determine if we can remove idle agents."""
        idle_time = (datetime.now() - module.last_active).total_seconds()
        return idle_time > idle_threshold and module.tasks_handled == 0


# ========================================
# SELF-ORGANIZING SYSTEM
# ========================================

class SelfOrganizingModularSystem:
    """
    Main coordinator that manages dynamic agent modules.

    Capabilities:
    - Creates specialist agents on-demand
    - Monitors load and scales agent count
    - Removes idle/underperforming agents
    - Redistributes work based on agent performance
    """

    def __init__(self):
        self.modules: Dict[str, List[AgentModule]] = {}  # specialty -> list of modules
        self.workload = WorkloadMetrics()
        self.module_counter = 0

        # Track supported specialties
        self.specialties = {
            "authentication": "Expert in login, password, and authentication issues",
            "billing": "Expert in billing, payments, and subscription issues",
            "technical": "Expert in API, integration, and technical issues",
            "general": "Handles general inquiries and information requests"
        }

    def _create_agent_module(self, specialty: str) -> AgentModule:
        """Dynamically create a new agent module for a specialty."""
        self.module_counter += 1
        module_id = f"{specialty}_module_{self.module_counter}"

        print(f"\n[SYSTEM] Creating new {specialty} agent module: {module_id}")

        # Create specialized agent
        agent = Agent(
            role=f"{specialty.title()} Specialist",
            goal=f"Handle {specialty} related support tickets efficiently",
            backstory=self.specialties[specialty],
            verbose=True,
            allow_delegation=False
        )

        module = AgentModule(
            module_id=module_id,
            specialty=specialty,
            agent=agent,
            created_at=datetime.now()
        )

        # Add to modules list
        if specialty not in self.modules:
            self.modules[specialty] = []
        self.modules[specialty].append(module)

        # Update workload metrics
        self.workload.active_modules[specialty] = len(self.modules[specialty])

        return module

    def _remove_agent_module(self, module: AgentModule):
        """Remove an idle or underperforming agent module."""
        print(f"\n[SYSTEM] Removing idle module: {module.module_id}")

        if module.specialty in self.modules:
            self.modules[module.specialty].remove(module)
            self.workload.active_modules[module.specialty] = len(self.modules[module.specialty])

    def _detect_specialty(self, ticket: Dict[str, Any]) -> str:
        """Detect which specialty should handle this ticket."""
        content = ticket["content"].lower()

        if any(word in content for word in ["login", "password", "auth", "access"]):
            return "authentication"
        elif any(word in content for word in ["billing", "payment", "invoice", "charge"]):
            return "billing"
        elif any(word in content for word in ["api", "integration", "error", "bug"]):
            return "technical"
        else:
            return "general"

    def _scale_system(self):
        """Check if system needs to scale up or down."""
        print(f"\n[SYSTEM] Checking scaling requirements...")

        # Check each specialty
        for specialty, pending_count in self.workload.pending_tasks.items():
            # Scale up if needed
            if self.workload.should_scale_up(specialty):
                print(f"[SYSTEM] Scaling UP {specialty} agents (pending: {pending_count})")
                self._create_agent_module(specialty)

        # Scale down - remove idle modules
        for specialty, modules in list(self.modules.items()):
            for module in list(modules):
                if self.workload.should_scale_down(specialty, module, idle_threshold=30):
                    self._remove_agent_module(module)

    def _select_best_module(self, specialty: str) -> Optional[AgentModule]:
        """Select the best performing module for a specialty."""
        if specialty not in self.modules or not self.modules[specialty]:
            return None

        # Sort by success rate and response time
        modules = self.modules[specialty]
        best_module = max(modules, key=lambda m: m.success_rate)

        return best_module

    def process_ticket(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """Process a support ticket using the self-organizing system."""

        ticket_id = ticket["id"]
        print(f"\n{'='*80}")
        print(f"Processing Ticket: {ticket_id}")
        print(f"Content: {ticket['content']}")
        print(f"{'='*80}")

        # Step 1: Detect specialty
        specialty = self._detect_specialty(ticket)
        print(f"[SYSTEM] Detected specialty: {specialty}")

        # Step 2: Update workload
        self.workload.pending_tasks[specialty] = self.workload.pending_tasks.get(specialty, 0) + 1

        # Step 3: Check if scaling is needed
        self._scale_system()

        # Step 4: Select or create module
        module = self._select_best_module(specialty)
        if not module:
            print(f"[SYSTEM] No {specialty} module available, creating one...")
            module = self._create_agent_module(specialty)

        # Step 5: Process ticket
        print(f"[SYSTEM] Assigning to: {module.module_id}")

        start_time = time.time()

        # Create task for the module
        task = Task(
            description=f"""Handle this support ticket:

Ticket ID: {ticket_id}
Content: {ticket['content']}

Provide a helpful resolution.""",
            agent=module.agent,
            expected_output="Resolution for the support ticket"
        )

        # Create minimal crew to execute
        crew = Crew(
            agents=[module.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )

        try:
            result = crew.kickoff()
            response_time = time.time() - start_time
            success = True

            # Update module metrics
            module.update_metrics(response_time, success)

            print(f"[SYSTEM] ✓ Ticket resolved in {response_time:.2f}s")

        except Exception as e:
            response_time = time.time() - start_time
            success = False
            result = f"Error: {str(e)}"

            module.update_metrics(response_time, success)

            print(f"[SYSTEM] ✗ Ticket failed: {str(e)}")

        # Step 6: Update workload
        self.workload.pending_tasks[specialty] = max(0, self.workload.pending_tasks[specialty] - 1)

        return {
            "ticket_id": ticket_id,
            "specialty": specialty,
            "handled_by": module.module_id,
            "response_time": response_time,
            "success": success,
            "result": str(result)
        }

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        total_modules = sum(len(modules) for modules in self.modules.values())
        total_tasks = sum(
            module.tasks_handled
            for modules in self.modules.values()
            for module in modules
        )

        module_stats = {}
        for specialty, modules in self.modules.items():
            module_stats[specialty] = {
                "count": len(modules),
                "total_tasks": sum(m.tasks_handled for m in modules),
                "avg_success_rate": sum(m.success_rate for m in modules) / len(modules) if modules else 0
            }

        return {
            "total_modules": total_modules,
            "total_tasks_handled": total_tasks,
            "modules_by_specialty": module_stats,
            "pending_tasks": dict(self.workload.pending_tasks),
            "timestamp": datetime.now().isoformat()
        }


# ========================================
# DEMO
# ========================================

def main():
    """Demonstrate self-organizing modular system."""

    print("="*80)
    print("SELF-ORGANIZING MODULAR AGENT SYSTEM")
    print("="*80)

    # Create system
    system = SelfOrganizingModularSystem()

    # Simulate incoming support tickets
    tickets = [
        {"id": "T001", "content": "I can't log into my account, password reset not working"},
        {"id": "T002", "content": "I was charged twice for my subscription this month"},
        {"id": "T003", "content": "Getting 500 error when calling the API endpoint"},
        {"id": "T004", "content": "How do I reset my password?"},
        {"id": "T005", "content": "Need help with billing invoice"},
        {"id": "T006", "content": "API authentication is failing"},
        {"id": "T007", "content": "What are your pricing plans?"},
        {"id": "T008", "content": "Login button not working"},
    ]

    # Process tickets
    results = []
    for ticket in tickets:
        result = system.process_ticket(ticket)
        results.append(result)

    # Show system statistics
    print(f"\n{'='*80}")
    print("SYSTEM STATISTICS")
    print(f"{'='*80}")

    stats = system.get_system_stats()
    print(json.dumps(stats, indent=2))

    print(f"\n{'='*80}")
    print("MODULE DETAILS")
    print(f"{'='*80}")

    for specialty, modules in system.modules.items():
        print(f"\n{specialty.upper()} Modules ({len(modules)}):")
        for module in modules:
            print(f"  - {module.module_id}")
            print(f"    Tasks: {module.tasks_handled}")
            print(f"    Success Rate: {module.success_rate*100:.1f}%")
            print(f"    Avg Response: {module.avg_response_time:.2f}s")

    print(f"\n{'='*80}")
    print("DEMO COMPLETE")
    print(f"{'='*80}")
    print("\nKey Features Demonstrated:")
    print("✓ Dynamic agent creation based on workload")
    print("✓ Automatic specialty detection")
    print("✓ Load-based scaling decisions")
    print("✓ Performance tracking per module")
    print("✓ Idle module cleanup")


if __name__ == "__main__":
    main()
