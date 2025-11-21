# Shared Tools & Utilities

This directory contains reusable tools, utilities, and helpers used across the orchestration patterns.

## Directory Structure

```
shared-tools/
├── adk_tools/              # Google ADK-specific tools
│   ├── __init__.py
│   ├── mock_tools.py       # Simulated tools for examples
│   ├── state_helpers.py    # State management utilities
│   └── mcp_servers.py      # MCP protocol implementations
├── crewai_tools/           # CrewAI-specific tools
│   ├── __init__.py
│   ├── custom_tools.py     # Custom tool implementations
│   └── shared_memory.py    # Memory and knowledge utilities
├── common/                 # Framework-agnostic utilities
│   ├── __init__.py
│   ├── blackboard.py       # Blackboard pattern implementation
│   ├── validators.py       # JSON validators and schemas
│   ├── risk_calculator.py  # Risk assessment utilities
│   └── context_transfer.py # Context preservation helpers
└── test_data/              # Sample data for examples
    ├── __init__.py
    ├── customer_orders.py
    ├── risk_profiles.py
    └── support_tickets.py
```

## Tools Overview

### ADK Tools (`adk_tools/`)

#### `mock_tools.py`
Mock implementations of common tools for educational examples:
- `MockGoogleSearch` - Simulated Google Search
- `MockDatabaseTool` - Simulated database operations
- `MockEmailTool` - Simulated email sending
- `MockPaymentGateway` - Simulated payment processing

#### `state_helpers.py`
State management utilities:
- `StateManager` - Session state management
- `OutputKeyHelper` - Helper for output_key patterns
- `ContextBuilder` - Build context from state

#### `mcp_servers.py`
MCP protocol implementations:
- `CustomMCPServer` - Base MCP server
- `DatabaseMCPServer` - Database access via MCP
- `APIMCPServer` - External API access via MCP

### CrewAI Tools (`crewai_tools/`)

#### `custom_tools.py`
Custom CrewAI tool implementations:
- `RiskAnalysisTool` - Risk assessment tool
- `DataExtractionTool` - Data parsing tool
- `ValidationTool` - Data validation tool
- `BlackboardAccessTool` - Blackboard read/write

#### `shared_memory.py`
Memory and knowledge management:
- `SharedKnowledgeBase` - Shared knowledge store
- `ContextMemory` - Context preservation
- `VectorStoreHelper` - Vector DB integration

### Common Utilities (`common/`)

#### `blackboard.py`
Blackboard pattern implementation:
- `Blackboard` - In-memory shared workspace
- `BlackboardEntry` - Structured entries
- `BlackboardMonitor` - Change tracking

#### `validators.py`
Pydantic validators and schemas:
- `OrderSchema` - Order data validation
- `RiskAssessmentSchema` - Risk assessment structure
- `InvoiceSchema` - Invoice validation
- `SupportTicketSchema` - Support ticket structure

#### `risk_calculator.py`
Risk assessment utilities:
- `calculate_credit_risk()` - Credit risk scoring
- `calculate_market_risk()` - Market risk scoring
- `calculate_regulatory_risk()` - Regulatory risk scoring
- `aggregate_risk_scores()` - Combine multiple scores

#### `context_transfer.py`
Context preservation for handoff patterns:
- `ContextPackage` - Structured context transfer
- `preserve_context()` - Context serialization
- `restore_context()` - Context deserialization

### Test Data (`test_data/`)

#### `customer_orders.py`
Sample customer orders for testing:
- `SAMPLE_ORDER_SIMPLE` - Basic order
- `SAMPLE_ORDER_LARGE` - Large order (>$5000)
- `SAMPLE_ORDER_VIP` - VIP customer order

#### `risk_profiles.py`
Sample risk assessment data:
- `LOW_RISK_PROFILE` - Low-risk customer
- `MEDIUM_RISK_PROFILE` - Medium-risk customer
- `HIGH_RISK_PROFILE` - High-risk customer

#### `support_tickets.py`
Sample support tickets:
- `FINANCIAL_TICKET` - Financial issue
- `LEGAL_TICKET` - Legal compliance issue
- `TECHNICAL_TICKET` - Technical support issue

## Usage Examples

### Using Mock Tools (ADK)

```python
from article_2_orchestration.shared_tools.adk_tools.mock_tools import MockGoogleSearch
from google.genai.agents import LlmAgent

search_tool = MockGoogleSearch()

agent = LlmAgent(
    name="researcher",
    model="gemini-2.5-flash",
    tools=[search_tool]
)
```

### Using Blackboard Pattern

```python
from article_2_orchestration.shared_tools.common.blackboard import Blackboard

# Create shared workspace
blackboard = Blackboard(name="ProductDesign")

# Agent 1 writes
blackboard.write("design_specs", {
    "dimensions": "10x5x3 cm",
    "material": "aluminum"
})

# Agent 2 reads
specs = blackboard.read("design_specs")
```

### Using Risk Calculator

```python
from article_2_orchestration.shared_tools.common.risk_calculator import (
    calculate_credit_risk,
    aggregate_risk_scores
)

credit_score = calculate_credit_risk(
    credit_rating=720,
    payment_history="excellent",
    debt_ratio=0.15
)
```

### Using Test Data

```python
from article_2_orchestration.shared_tools.test_data.customer_orders import SAMPLE_ORDER_SIMPLE

# Use in your examples
result = process_order(SAMPLE_ORDER_SIMPLE)
```

## Installation

No additional dependencies needed beyond the main project requirements:

```bash
# ADK tools
uv add google-genai

# CrewAI tools
uv add crewai crewai-tools

# Common utilities
uv add pydantic
```

## Contributing

When adding new shared tools:
1. Follow the existing structure
2. Add comprehensive docstrings
3. Include usage examples
4. Update this README
5. Add unit tests in `../tests/shared_tools/`
