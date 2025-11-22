"""
Pattern 22: Self-Organizing Modular Agent
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

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.tools import Tool


# ========================================
# MODULE DEFINITION
# ========================================

@dataclass
class AgentModule:
    """Represents a dynamically created agent module"""
    module_id: str
    specialty: str
    agent: LlmAgent
    created_at: datetime
    tasks_handled: int = 0
    last_active: datetime = field(default_factory=datetime.now)
    avg_response_time: float = 0.0
    success_rate: float = 1.0

    def update_metrics(self, response_time: float, success: bool):
        """Update module performance metrics"""
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
    """Tracks system workload for scaling decisions"""
    pending_tasks: Dict[str, int] = field(default_factory=dict)  # specialty -> count
    active_modules: Dict[str, int] = field(default_factory=dict)  # specialty -> count
    avg_wait_time: Dict[str, float] = field(default_factory=dict)
    last_scaling_decision: datetime = field(default_factory=datetime.now)

    def should_scale_up(self, specialty: str, threshold: int = 3) -> bool:
        """Determine if we need more agents for a specialty"""
        pending = self.pending_tasks.get(specialty, 0)
        active = self.active_modules.get(specialty, 0)

        # Scale up if: pending tasks > threshold * active modules
        if active == 0:
            return pending > 0
        return pending > (threshold * active)

    def should_scale_down(self, specialty: str, idle_threshold: int = 60) -> bool:
        """Determine if we can remove idle agents"""
        # Check if any modules have been idle for too long
        return True  # Simplified for demo


# ========================================
# SELF-ORGANIZING SYSTEM
# ========================================

class SelfOrganizingAgentSystem:
    """
    Main orchestrator that manages dynamic agent modules
    """

    def __init__(self):
        self.modules: Dict[str, AgentModule] = {}
        self.workload = WorkloadMetrics()
        self.session_service = InMemorySessionService()

        # Specialty definitions
        self.specialty_configs = {
            "networking": "Network connectivity, DNS, firewall, routing issues",
            "authentication": "Login, SSO, password, OAuth, identity issues",
            "database": "Database performance, queries, migrations, replication",
            "api": "API errors, rate limits, endpoints, integration issues",
            "billing": "Billing questions, invoices, credits, pricing",
            "general": "General support and triage"
        }

        # Create a coordinator agent
        self.coordinator = LlmAgent(
            name="coordinator",
            model="gemini-2.5-flash",
            instruction="""
            You are a support ticket coordinator.
            Analyze incoming support tickets and categorize them into:
            - networking
            - authentication
            - database
            - api
            - billing
            - general

            Return ONLY the category name in lowercase.
            """,
            description="Coordinates ticket routing"
        )

    async def create_module(self, specialty: str) -> AgentModule:
        """
        Dynamically create a new agent module for a specialty
        """
        module_id = f"{specialty}_{datetime.now().timestamp()}"

        agent = LlmAgent(
            name=f"specialist_{module_id}",
            model="gemini-2.5-flash",
            instruction=f"""
            You are a specialized support agent focused on: {self.specialty_configs[specialty]}

            Your role:
            1. Analyze the support ticket
            2. Provide detailed solution steps
            3. Identify if escalation is needed
            4. Suggest preventive measures

            Be concise but thorough. Use bullet points for clarity.
            """,
            description=f"Specialist for {specialty}",
            output_key="solution"
        )

        module = AgentModule(
            module_id=module_id,
            specialty=specialty,
            agent=agent,
            created_at=datetime.now()
        )

        self.modules[module_id] = module

        # Update workload tracking
        self.workload.active_modules[specialty] = \
            self.workload.active_modules.get(specialty, 0) + 1

        print(f"✅ Created new {specialty} module: {module_id}")
        print(f"   Total {specialty} modules: {self.workload.active_modules[specialty]}")

        return module

    async def remove_module(self, module_id: str):
        """
        Remove an idle agent module to save resources
        """
        if module_id in self.modules:
            module = self.modules[module_id]
            specialty = module.specialty

            del self.modules[module_id]

            self.workload.active_modules[specialty] = \
                max(0, self.workload.active_modules.get(specialty, 1) - 1)

            print(f"🗑️  Removed idle {specialty} module: {module_id}")
            print(f"   Remaining {specialty} modules: {self.workload.active_modules[specialty]}")

    async def find_best_module(self, specialty: str) -> Optional[AgentModule]:
        """
        Find the best available module for a specialty
        Based on: lowest current load, best performance metrics
        """
        available_modules = [
            m for m in self.modules.values()
            if m.specialty == specialty
        ]

        if not available_modules:
            return None

        # Simple strategy: pick module with highest success rate and lowest avg response time
        best_module = min(
            available_modules,
            key=lambda m: (1 - m.success_rate, m.avg_response_time)
        )

        return best_module

    async def auto_scale(self):
        """
        Analyze workload and make scaling decisions
        """
        print("\n🔄 Running auto-scaling analysis...")

        for specialty in self.specialty_configs.keys():
            # Scale up if needed
            if self.workload.should_scale_up(specialty):
                print(f"📈 Scaling up {specialty} capacity")
                await self.create_module(specialty)

        # Scale down idle modules (check every module)
        current_time = datetime.now()
        idle_threshold = timedelta(seconds=30)  # Short for demo

        modules_to_remove = []
        for module_id, module in self.modules.items():
            if (current_time - module.last_active) > idle_threshold and module.tasks_handled == 0:
                modules_to_remove.append(module_id)

        for module_id in modules_to_remove:
            await self.remove_module(module_id)

        self.workload.last_scaling_decision = datetime.now()

    async def process_ticket(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a support ticket using the self-organizing system
        """
        ticket_id = ticket.get("id", "unknown")
        description = ticket.get("description", "")

        print(f"\n{'=' * 60}")
        print(f"📨 Processing Ticket #{ticket_id}")
        print(f"{'=' * 60}")

        # Step 1: Categorize the ticket
        categorization = await self.coordinator.run(
            state={"description": description},
            session_service=self.session_service,
            session_id=f"ticket_{ticket_id}"
        )

        specialty = categorization.get("output", "general").strip().lower()
        print(f"📂 Category: {specialty}")

        # Track pending work
        self.workload.pending_tasks[specialty] = \
            self.workload.pending_tasks.get(specialty, 0) + 1

        # Step 2: Check if we need to scale
        await self.auto_scale()

        # Step 3: Find or create appropriate module
        module = await self.find_best_module(specialty)

        if not module:
            print(f"🆕 No {specialty} module available, creating one...")
            module = await self.create_module(specialty)

        # Step 4: Process with specialist
        start_time = datetime.now()

        result = await module.agent.run(
            state={"ticket": ticket, "description": description},
            session_service=self.session_service,
            session_id=f"ticket_{ticket_id}_{module.module_id}"
        )

        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()

        # Update metrics
        success = "solution" in result
        module.update_metrics(response_time, success)

        # Remove from pending
        self.workload.pending_tasks[specialty] = \
            max(0, self.workload.pending_tasks.get(specialty, 1) - 1)

        print(f"\n✅ Ticket resolved by module: {module.module_id}")
        print(f"   Response time: {response_time:.2f}s")
        print(f"   Module metrics: {module.tasks_handled} tasks, "
              f"{module.success_rate:.1%} success rate")

        return {
            "ticket_id": ticket_id,
            "specialty": specialty,
            "module_id": module.module_id,
            "solution": result.get("solution"),
            "response_time": response_time,
            "module_metrics": {
                "tasks_handled": module.tasks_handled,
                "success_rate": module.success_rate,
                "avg_response_time": module.avg_response_time
            }
        }

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status and metrics
        """
        return {
            "total_modules": len(self.modules),
            "modules_by_specialty": {
                specialty: len([m for m in self.modules.values() if m.specialty == specialty])
                for specialty in self.specialty_configs.keys()
            },
            "pending_tasks": dict(self.workload.pending_tasks),
            "module_details": [
                {
                    "id": m.module_id,
                    "specialty": m.specialty,
                    "tasks_handled": m.tasks_handled,
                    "success_rate": f"{m.success_rate:.1%}",
                    "avg_response_time": f"{m.avg_response_time:.2f}s",
                    "age": (datetime.now() - m.created_at).seconds
                }
                for m in self.modules.values()
            ]
        }


# ========================================
# DEMO EXECUTION
# ========================================

async def main():
    """
    Demonstrate self-organizing modular agent system
    """
    system = SelfOrganizingAgentSystem()

    # Simulate various support tickets coming in
    tickets = [
        {"id": 1, "description": "Cannot connect to database, getting timeout errors"},
        {"id": 2, "description": "User unable to login via SSO, getting 401 error"},
        {"id": 3, "description": "API rate limit exceeded on /users endpoint"},
        {"id": 4, "description": "Network connectivity issues in us-west-2 region"},
        {"id": 5, "description": "Invoice shows incorrect amount for October"},
        {"id": 6, "description": "Database query performance is very slow"},
        {"id": 7, "description": "OAuth token refresh not working"},
        {"id": 8, "description": "Need help understanding pricing tiers"},
    ]

    print("=" * 80)
    print("SELF-ORGANIZING MODULAR AGENT SYSTEM - DEMO")
    print("=" * 80)
    print("\nSimulating support ticket processing with dynamic agent scaling...\n")

    # Process tickets with some delays to show scaling
    for i, ticket in enumerate(tickets):
        result = await system.process_ticket(ticket)

        # Every few tickets, show system status
        if (i + 1) % 3 == 0:
            print("\n" + "=" * 60)
            print("📊 SYSTEM STATUS")
            print("=" * 60)
            status = system.get_system_status()
            print(f"Total Active Modules: {status['total_modules']}")
            print(f"Modules by Specialty: {status['modules_by_specialty']}")
            print(f"Pending Tasks: {status['pending_tasks']}")
            print()

        # Small delay between tickets
        if i < len(tickets) - 1:
            await asyncio.sleep(0.5)

    # Final status
    print("\n" + "=" * 80)
    print("📈 FINAL SYSTEM STATUS")
    print("=" * 80)
    status = system.get_system_status()
    print(f"\nTotal Modules Created: {status['total_modules']}")
    print(f"\nModule Distribution:")
    for specialty, count in status['modules_by_specialty'].items():
        print(f"  {specialty}: {count} modules")

    print(f"\nDetailed Module Metrics:")
    for module in status['module_details']:
        print(f"\n  Module: {module['id']}")
        print(f"    Specialty: {module['specialty']}")
        print(f"    Tasks: {module['tasks_handled']}")
        print(f"    Success Rate: {module['success_rate']}")
        print(f"    Avg Response: {module['avg_response_time']}")
        print(f"    Age: {module['age']}s")


if __name__ == "__main__":
    asyncio.run(main())
