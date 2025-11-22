"""
Pattern 21: Tool Use with MCP - CrewAI Implementation

Model Context Protocol standardizes enterprise tool integration. Secure, observable,
and auditable access to critical systems.

Business Example: GlobalManufacturing (Fortune 500)
- Integration time: 6 months → 2 weeks per system
- Security incidents: 0 in production
- API calls: 2M daily with 99.99% success
- Cost savings: $3.4M annually

Mermaid Diagram Reference: diagrams/pattern-21-mcp-tools.mmd
Medium Article: Part 3 - Governance and Reliability Patterns
"""

import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()


@dataclass
class ToolExecutionLog:
    """Audit log for tool execution."""
    timestamp: datetime
    tool_name: str
    action: str
    success: bool
    duration_ms: float


class AuditLogger:
    """Centralized audit logging."""

    def __init__(self):
        self.logs: List[ToolExecutionLog] = []

    def log(self, log: ToolExecutionLog):
        self.logs.append(log)
        status = "[green]✓[/green]" if log.success else "[red]✗[/red]"
        console.print(f"{status} {log.tool_name}: {log.action} ({log.duration_ms:.0f}ms)")


class SAPInventoryTool(BaseTool):
    """MCP tool for SAP inventory checks."""
    name: str = "sap_inventory_check"
    description: str = "Check product inventory levels in SAP ERP system"

    def __init__(self, audit_logger: AuditLogger):
        super().__init__()
        object.__setattr__(self, 'audit_logger', audit_logger)
        object.__setattr__(self, 'inventory', {
            "WIDGET-A": {"quantity": 1500, "unit": "pcs", "location": "WH-01"},
            "WIDGET-B": {"quantity": 750, "unit": "pcs", "location": "WH-02"},
            "COMPONENT-X": {"quantity": 5000, "unit": "pcs", "location": "WH-01"}
        })

    def _run(self, product_code: str) -> str:
        """Check inventory for a product."""
        start = datetime.now()

        if product_code in self.inventory:
            result = self.inventory[product_code]
            success = True
            output = f"Product {product_code}: {result['quantity']} {result['unit']} in {result['location']}"
        else:
            success = False
            output = f"Product {product_code} not found in SAP inventory"

        duration = (datetime.now() - start).total_seconds() * 1000
        self.audit_logger.log(ToolExecutionLog(
            timestamp=datetime.now(),
            tool_name="SAP_Inventory",
            action=f"check({product_code})",
            success=success,
            duration_ms=duration
        ))

        return output


class OracleBudgetTool(BaseTool):
    """MCP tool for Oracle Financials budget checks."""
    name: str = "oracle_budget_check"
    description: str = "Check department budget in Oracle Financials system"

    def __init__(self, audit_logger: AuditLogger):
        super().__init__()
        object.__setattr__(self, 'audit_logger', audit_logger)
        object.__setattr__(self, 'budgets', {
            "DEPT-001": {"budget": 500000, "spent": 342000, "remaining": 158000},
            "DEPT-002": {"budget": 750000, "spent": 680000, "remaining": 70000}
        })

    def _run(self, department_code: str) -> str:
        """Check budget for a department."""
        start = datetime.now()

        if department_code in self.budgets:
            data = self.budgets[department_code]
            success = True
            output = f"Department {department_code}: ${data['remaining']:,} remaining of ${data['budget']:,} budget ({data['spent']/data['budget']*100:.1f}% spent)"
        else:
            success = False
            output = f"Department {department_code} not found in Oracle Financials"

        duration = (datetime.now() - start).total_seconds() * 1000
        self.audit_logger.log(ToolExecutionLog(
            timestamp=datetime.now(),
            tool_name="Oracle_Financials",
            action=f"check({department_code})",
            success=success,
            duration_ms=duration
        ))

        return output


class SalesforceOpportunityTool(BaseTool):
    """MCP tool for Salesforce CRM."""
    name: str = "salesforce_opportunity"
    description: str = "Get sales opportunity details from Salesforce CRM"

    def __init__(self, audit_logger: AuditLogger):
        super().__init__()
        object.__setattr__(self, 'audit_logger', audit_logger)
        object.__setattr__(self, 'opportunities', {
            "OPP-12345": {
                "name": "Enterprise Widget Deal",
                "amount": 250000,
                "stage": "Negotiation",
                "probability": 75,
                "close_date": "2024-12-15"
            }
        })

    def _run(self, opportunity_id: str) -> str:
        """Get opportunity details."""
        start = datetime.now()

        if opportunity_id in self.opportunities:
            opp = self.opportunities[opportunity_id]
            success = True
            output = f"Opportunity {opportunity_id} ({opp['name']}): ${opp['amount']:,} at {opp['probability']}% probability, stage: {opp['stage']}, closes: {opp['close_date']}"
        else:
            success = False
            output = f"Opportunity {opportunity_id} not found in Salesforce"

        duration = (datetime.now() - start).total_seconds() * 1000
        self.audit_logger.log(ToolExecutionLog(
            timestamp=datetime.now(),
            tool_name="Salesforce_CRM",
            action=f"get({opportunity_id})",
            success=success,
            duration_ms=duration
        ))

        return output


class MCPIntegrationCrew:
    """Crew with MCP enterprise tool integrations."""

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger

        # Initialize MCP tools
        self.sap_tool = SAPInventoryTool(audit_logger)
        self.oracle_tool = OracleBudgetTool(audit_logger)
        self.salesforce_tool = SalesforceOpportunityTool(audit_logger)

        # Create integration agent
        self.integration_agent = Agent(
            role="Enterprise Systems Integrator",
            goal="Access enterprise systems to retrieve business-critical information",
            backstory="""You are an enterprise integration specialist with secure
            access to SAP, Oracle Financials, and Salesforce. You use these systems
            to provide accurate, real-time business information.""",
            tools=[self.sap_tool, self.oracle_tool, self.salesforce_tool],
            verbose=True,
            allow_delegation=False
        )

        console.print("[green]✓[/green] MCP Integration Crew initialized")

    def process_query(self, query: str) -> str:
        """Process query using MCP tools."""
        console.print(f"\n[cyan]Query:[/cyan] {query}")

        task = Task(
            description=f"""Process this enterprise data request: {query}

            Use the appropriate enterprise system tools (SAP, Oracle, Salesforce)
            to retrieve the requested information. Provide a clear, concise response.""",
            agent=self.integration_agent,
            expected_output="Accurate enterprise data response"
        )

        crew = Crew(
            agents=[self.integration_agent],
            tasks=[task],
            verbose=True
        )

        result = crew.kickoff()
        return str(result)


def demonstrate_mcp_pattern():
    """Demonstrate MCP tool integration."""
    console.print("\n[bold blue]═══ Pattern 21: MCP Tools - CrewAI ═══[/bold blue]")
    console.print("[bold]Business: GlobalManufacturing - ERP Integration[/bold]\n")

    # Initialize
    audit_logger = AuditLogger()
    crew = MCPIntegrationCrew(audit_logger)

    # Test queries
    queries = [
        "What is the inventory level for WIDGET-A?",
        "Check budget status for DEPT-001",
        "Get details on opportunity OPP-12345"
    ]

    for query in queries:
        result = crew.process_query(query)
        console.print(f"[green]Response:[/green] {result}\n")

    # Display audit trail
    display_audit_trail(audit_logger)

    # Display metrics
    display_business_metrics()


def display_audit_trail(audit_logger: AuditLogger):
    """Display audit trail."""
    table = Table(title="MCP Tool Execution Audit Trail")
    table.add_column("Time", style="cyan")
    table.add_column("Tool", style="green")
    table.add_column("Action", style="yellow")
    table.add_column("Duration", style="magenta")
    table.add_column("Status", style="white")

    for log in audit_logger.logs:
        table.add_row(
            log.timestamp.strftime('%H:%M:%S'),
            log.tool_name,
            log.action,
            f"{log.duration_ms:.0f}ms",
            "✓" if log.success else "✗"
        )

    console.print(table)


def display_business_metrics():
    """Display business impact."""
    console.print("\n[bold cyan]═══ Business Impact: GlobalManufacturing ═══[/bold cyan]")

    metrics = Table(title="Enterprise Integration Metrics")
    metrics.add_column("Metric", style="cyan")
    metrics.add_column("Before MCP", style="red")
    metrics.add_column("After MCP", style="green")
    metrics.add_column("Impact", style="yellow")

    metrics.add_row("Integration Time", "6 months", "2 weeks", "92% reduction")
    metrics.add_row("Security Incidents", "Multiple/year", "0", "100% improvement")
    metrics.add_row("Daily API Calls", "N/A", "2M @ 99.99%", "Reliable")
    metrics.add_row("Annual Savings", "Baseline", "$3.4M", "Cost efficiency")

    console.print(metrics)


if __name__ == "__main__":
    demonstrate_mcp_pattern()
