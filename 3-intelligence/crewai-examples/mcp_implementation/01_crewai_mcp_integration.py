"""
MCP Implementation with CrewAI
Article 2: Orchestration & Collaboration Patterns

This example shows how CrewAI agents can connect to MCP servers
to access shared tools and resources.

Key Points:
- CrewAI tools can wrap MCP server calls
- Multiple agents can share the same MCP server
- Standardized protocol for cross-framework compatibility

Use Case: Customer Data Platform
- CRM MCP Server provides customer data access
- Multiple agents use the server to analyze customers
- Analytics, Support, and Sales agents collaborate
"""

import json
from typing import Any, Dict, List
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool


# ========================================
# MOCK CRM DATABASE
# ========================================

CRM_DATABASE = {
    "customers": [
        {
            "id": "C001",
            "name": "Acme Corp",
            "industry": "Manufacturing",
            "arr": 120000,
            "health_score": 85,
            "open_tickets": 2,
            "last_contact": "2024-11-15"
        },
        {
            "id": "C002",
            "name": "Tech Startup Inc",
            "industry": "Technology",
            "arr": 45000,
            "health_score": 92,
            "open_tickets": 0,
            "last_contact": "2024-11-18"
        },
        {
            "id": "C003",
            "name": "Finance Group",
            "industry": "Financial Services",
            "arr": 200000,
            "health_score": 65,
            "open_tickets": 5,
            "last_contact": "2024-11-10"
        }
    ],
    "interactions": [
        {"customer_id": "C001", "type": "support", "date": "2024-11-15", "sentiment": "neutral"},
        {"customer_id": "C002", "type": "sales", "date": "2024-11-18", "sentiment": "positive"},
        {"customer_id": "C003", "type": "support", "date": "2024-11-10", "sentiment": "negative"}
    ]
}


# ========================================
# MCP SERVER (Simple Implementation)
# ========================================

class CRMMCPServer:
    """Mock MCP server for CRM data."""

    @staticmethod
    def get_customer(customer_id: str) -> Dict[str, Any]:
        """Get customer by ID."""
        for customer in CRM_DATABASE["customers"]:
            if customer["id"] == customer_id:
                return customer
        return {}

    @staticmethod
    def list_customers(filter_by: str = None, value: Any = None) -> List[Dict[str, Any]]:
        """List customers with optional filtering."""
        customers = CRM_DATABASE["customers"]

        if filter_by and value:
            customers = [c for c in customers if c.get(filter_by) == value]

        return customers

    @staticmethod
    def get_customer_interactions(customer_id: str) -> List[Dict[str, Any]]:
        """Get interaction history for a customer."""
        return [
            i for i in CRM_DATABASE["interactions"]
            if i["customer_id"] == customer_id
        ]

    @staticmethod
    def get_at_risk_customers(threshold: int = 70) -> List[Dict[str, Any]]:
        """Get customers with health score below threshold."""
        return [
            c for c in CRM_DATABASE["customers"]
            if c["health_score"] < threshold
        ]


# ========================================
# MCP TOOLS FOR CREWAI
# ========================================

# Wrap MCP server methods as CrewAI tools
mcp_server = CRMMCPServer()


@tool("Get Customer")
def get_customer(customer_id: str) -> str:
    """Get customer information by ID from CRM MCP server."""
    result = mcp_server.get_customer(customer_id)
    return json.dumps(result, indent=2)


@tool("List Customers")
def list_customers(filter_by: str = None, value: str = None) -> str:
    """List all customers from CRM MCP server with optional filtering."""
    result = mcp_server.list_customers(filter_by, value)
    return json.dumps(result, indent=2)


@tool("Get Customer Interactions")
def get_customer_interactions(customer_id: str) -> str:
    """Get interaction history for a customer from CRM MCP server."""
    result = mcp_server.get_customer_interactions(customer_id)
    return json.dumps(result, indent=2)


@tool("Get At-Risk Customers")
def get_at_risk_customers(threshold: str = "70") -> str:
    """Get customers with health score below threshold from CRM MCP server."""
    result = mcp_server.get_at_risk_customers(int(threshold))
    return json.dumps(result, indent=2)


# ========================================
# AGENTS USING MCP TOOLS
# ========================================

# Analytics Agent
analytics_agent = Agent(
    role="Customer Analytics Specialist",
    goal="Analyze customer data to identify trends and opportunities",
    backstory="""You are a data analyst who uses the CRM MCP server to analyze
    customer health, identify at-risk accounts, and spot growth opportunities.""",
    verbose=True,
    allow_delegation=False,
    tools=[list_customers, get_at_risk_customers, get_customer_interactions]
)

# Support Agent
support_agent = Agent(
    role="Customer Success Manager",
    goal="Identify and help customers who need support",
    backstory="""You monitor customer health scores and interaction history to
    proactively reach out to customers who may need help.""",
    verbose=True,
    allow_delegation=False,
    tools=[get_customer, get_customer_interactions, get_at_risk_customers]
)

# Sales Agent
sales_agent = Agent(
    role="Account Executive",
    goal="Identify upsell opportunities and healthy customer relationships",
    backstory="""You use customer data to find accounts ready for expansion
    and maintain strong relationships with high-value customers.""",
    verbose=True,
    allow_delegation=False,
    tools=[list_customers, get_customer, get_customer_interactions]
)


# ========================================
# DEMO: MULTI-AGENT COLLABORATION VIA MCP
# ========================================

def run_customer_analysis():
    """Run customer analysis using multiple agents connected to MCP server."""

    print("="*80)
    print("MCP-POWERED CUSTOMER ANALYSIS")
    print("="*80)

    # Task 1: Analytics identifies at-risk customers
    analytics_task = Task(
        description="""Analyze customer health using the MCP server:

1. Use get_at_risk_customers with threshold 70
2. For each at-risk customer, get their interaction history
3. Identify patterns (e.g., high ticket volume, negative sentiment)
4. Provide a list of at-risk customers with reasons

Use the CRM MCP server tools.""",
        agent=analytics_agent,
        expected_output="List of at-risk customers with analysis of risk factors"
    )

    # Task 2: Support creates action plan
    support_task = Task(
        description="""Based on the at-risk analysis, create a support action plan:

1. Review each at-risk customer's details
2. Check their interaction history for context
3. Prioritize by ARR and health score
4. Create specific outreach recommendations

Use MCP tools to get customer details.""",
        agent=support_agent,
        expected_output="Prioritized action plan for supporting at-risk customers",
        context=[analytics_task]
    )

    # Task 3: Sales identifies expansion opportunities
    sales_task = Task(
        description="""Identify healthy customers for expansion:

1. Use list_customers to find customers with health_score >= 85
2. Get interaction history to confirm positive relationships
3. Prioritize by ARR for upsell potential
4. Create expansion recommendations

Use MCP tools for data access.""",
        agent=sales_agent,
        expected_output="List of expansion opportunities with recommendations",
        context=[analytics_task]
    )

    # Create crew
    crew = Crew(
        agents=[analytics_agent, support_agent, sales_agent],
        tasks=[analytics_task, support_task, sales_task],
        process=Process.sequential,
        verbose=True
    )

    # Execute
    result = crew.kickoff()

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nResults:\n{result}")

    return result


# ========================================
# MAIN
# ========================================

if __name__ == "__main__":
    run_customer_analysis()
