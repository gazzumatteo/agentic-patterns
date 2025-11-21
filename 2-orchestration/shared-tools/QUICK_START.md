# Shared Tools Quick Start Guide

## 🚀 Quick Examples

### Example 1: Use Sample Order Data

```python
from test_data.customer_orders import SAMPLE_ORDER_SIMPLE

# Use in your pattern
result = process_order(SAMPLE_ORDER_SIMPLE)
```

### Example 2: Calculate Risk Scores

```python
from common.risk_calculator import calculate_credit_risk, aggregate_risk_scores

# Calculate credit risk
risk = calculate_credit_risk(
    credit_rating=720,
    payment_history="excellent",
    debt_ratio=0.15
)

print(f"Risk Score: {risk.score}/100")
print(f"Recommendation: {risk.recommendation}")
```

### Example 3: Validate Data with Pydantic

```python
from common.validators import OrderSchema

order_data = {
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "order_items": [
        {"product": "Laptop", "quantity": 1, "unit_price": 1299.00}
    ],
    "shipping_address": "123 Main St"
}

# Validate
order = OrderSchema(**order_data)
print(f"Total: ${order.total_amount}")
```

### Example 4: Use Blackboard for Collaboration

```python
from common.blackboard import Blackboard

blackboard = Blackboard("ProductDesign")

# Agent 1 writes
blackboard.write("specs", {"material": "aluminum"}, author="DesignAgent")

# Agent 2 reads and writes
specs = blackboard.read("specs")
blackboard.write("cost", {"total": 165.00}, author="CostAgent")

# Check summary
print(blackboard.get_summary())
```

## 📦 Available Test Data

- **Customer Orders**: `SAMPLE_ORDER_SIMPLE`, `SAMPLE_ORDER_LARGE`, `SAMPLE_ORDER_VIP`, `SAMPLE_ORDER_INTERNATIONAL`
- **Risk Profiles**: `LOW_RISK_PROFILE`, `MEDIUM_RISK_PROFILE`, `HIGH_RISK_PROFILE`, `CRITICAL_RISK_PROFILE`
- **Support Tickets**: `FINANCIAL_TICKET`, `LEGAL_TICKET`, `TECHNICAL_TICKET`, `VIP_TICKET`, `GENERAL_TICKET`

## 🛠️ Available Utilities

- **Risk Calculators**: Credit, Market, Regulatory risk scoring
- **Validators**: Order, Risk, Invoice, Ticket schemas
- **Context Transfer**: Handoff context preservation
- **Blackboard**: Shared workspace for multi-agent collaboration

See `README.md` for complete documentation.
