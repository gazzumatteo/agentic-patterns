"""
A2A (Agent-to-Agent) Protocol with CrewAI
Article 2: Orchestration & Collaboration Patterns

A2A enables agents to communicate directly with each other, request services,
and coordinate complex workflows across agent boundaries.

Key Concepts:
- Direct agent-to-agent messaging
- Service discovery and invocation
- Protocol negotiation
- Cross-system coordination

Use Case: E-Commerce Order Processing
- Order Agent requests inventory check from Inventory Agent
- Inventory Agent coordinates with Warehouse Agent
- Payment Agent processes payment independently
- Shipping Agent receives notification from Order Agent

Business Value:
- Decoupled agent systems
- Service reusability
- Scalable multi-agent architectures
- Cross-platform agent collaboration
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool


# ========================================
# A2A MESSAGE PROTOCOL
# ========================================

class A2AMessage:
    """Standard message format for agent-to-agent communication."""

    def __init__(
        self,
        sender: str,
        receiver: str,
        message_type: str,
        payload: Dict[str, Any],
        request_id: Optional[str] = None
    ):
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.payload = payload
        self.request_id = request_id or f"req_{datetime.now().timestamp()}"
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type,
            "payload": self.payload,
            "request_id": self.request_id,
            "timestamp": self.timestamp
        }


class A2AMessageBus:
    """Message bus for routing A2A messages between agents."""

    def __init__(self):
        self.messages: List[A2AMessage] = []
        self.agents: Dict[str, Any] = {}

    def register_agent(self, agent_id: str, agent: Any):
        """Register an agent with the message bus."""
        self.agents[agent_id] = agent
        print(f"[A2A] Registered agent: {agent_id}")

    def send_message(self, message: A2AMessage) -> Dict[str, Any]:
        """Send a message from one agent to another."""
        print(f"\n[A2A] Message: {message.sender} -> {message.receiver}")
        print(f"      Type: {message.message_type}")
        print(f"      Payload: {json.dumps(message.payload, indent=2)}")

        self.messages.append(message)

        # In a real system, this would invoke the receiving agent
        # For demo, we'll simulate responses
        return self._simulate_response(message)

    def _simulate_response(self, message: A2AMessage) -> Dict[str, Any]:
        """Simulate agent response based on message type."""
        receiver = message.receiver
        msg_type = message.message_type

        if receiver == "inventory_agent":
            if msg_type == "check_stock":
                product_id = message.payload.get("product_id")
                quantity = message.payload.get("quantity", 1)

                # Simulate inventory check
                available = quantity <= 10  # Mock logic

                return {
                    "status": "available" if available else "insufficient",
                    "product_id": product_id,
                    "requested": quantity,
                    "in_stock": 10 if available else 5,
                    "warehouse_id": "WH_001"
                }

        elif receiver == "payment_agent":
            if msg_type == "process_payment":
                amount = message.payload.get("amount")
                method = message.payload.get("method", "credit_card")

                # Simulate payment processing
                return {
                    "status": "success",
                    "transaction_id": f"txn_{datetime.now().timestamp()}",
                    "amount": amount,
                    "method": method
                }

        elif receiver == "shipping_agent":
            if msg_type == "create_shipment":
                order_id = message.payload.get("order_id")
                address = message.payload.get("address")

                return {
                    "status": "created",
                    "tracking_number": f"TRACK{order_id}",
                    "estimated_delivery": "2024-11-25",
                    "carrier": "UPS"
                }

        return {"status": "unknown_request"}


# Global message bus
message_bus = A2AMessageBus()


# ========================================
# A2A TOOLS FOR AGENTS
# ========================================

@tool("Send A2A Message")
def send_a2a_message(receiver: str, message_type: str, payload: str) -> str:
    """Send a message to another agent using A2A protocol."""
    payload_dict = json.loads(payload)

    message = A2AMessage(
        sender="order_agent",  # Would be dynamic in real implementation
        receiver=receiver,
        message_type=message_type,
        payload=payload_dict
    )

    response = message_bus.send_message(message)
    return json.dumps(response, indent=2)


@tool("Query Inventory")
def query_inventory(product_id: str, quantity: str) -> str:
    """Query inventory agent for stock availability."""
    message = A2AMessage(
        sender="order_agent",
        receiver="inventory_agent",
        message_type="check_stock",
        payload={"product_id": product_id, "quantity": int(quantity)}
    )

    response = message_bus.send_message(message)
    return json.dumps(response, indent=2)


@tool("Process Payment")
def process_payment(amount: str, method: str = "credit_card") -> str:
    """Request payment agent to process payment."""
    message = A2AMessage(
        sender="order_agent",
        receiver="payment_agent",
        message_type="process_payment",
        payload={"amount": float(amount), "method": method}
    )

    response = message_bus.send_message(message)
    return json.dumps(response, indent=2)


@tool("Create Shipment")
def create_shipment(order_id: str, address: str) -> str:
    """Request shipping agent to create shipment."""
    message = A2AMessage(
        sender="order_agent",
        receiver="shipping_agent",
        message_type="create_shipment",
        payload={"order_id": order_id, "address": address}
    )

    response = message_bus.send_message(message)
    return json.dumps(response, indent=2)


# ========================================
# AGENTS
# ========================================

# Order Coordinator Agent
order_agent = Agent(
    role="Order Coordinator",
    goal="Coordinate order processing by communicating with inventory, payment, and shipping agents",
    backstory="""You are the main order coordinator. You use A2A protocol to communicate
    with other specialized agents (inventory, payment, shipping) to fulfill customer orders.
    You never process these tasks yourself - you always delegate to the appropriate agents.""",
    verbose=True,
    allow_delegation=False,
    tools=[query_inventory, process_payment, create_shipment]
)


# ========================================
# DEMO
# ========================================

def process_order_with_a2a(order: Dict[str, Any]):
    """Process an order using A2A protocol for agent coordination."""

    print("="*80)
    print("A2A PROTOCOL DEMONSTRATION")
    print("Order Processing with Agent-to-Agent Communication")
    print("="*80)

    print(f"\nOrder Details:")
    print(json.dumps(order, indent=2))

    # Create task for order agent
    task = Task(
        description=f"""Process this customer order using A2A protocol:

Order ID: {order['order_id']}
Product ID: {order['product_id']}
Quantity: {order['quantity']}
Amount: ${order['amount']}
Shipping Address: {order['address']}

Steps to complete:
1. Use query_inventory to check stock with inventory_agent
2. If stock available, use process_payment to charge customer via payment_agent
3. If payment successful, use create_shipment to create shipment via shipping_agent
4. Return order status summary

IMPORTANT: Use A2A tools to communicate with other agents. Do NOT process inventory,
payment, or shipping yourself.""",
        agent=order_agent,
        expected_output="Complete order processing status with results from all agents"
    )

    # Execute
    crew = Crew(
        agents=[order_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()

    print(f"\n{'='*80}")
    print("ORDER PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"\nResult:\n{result}")

    # Show A2A message log
    print(f"\n{'='*80}")
    print("A2A MESSAGE LOG")
    print(f"{'='*80}")
    print(f"Total Messages: {len(message_bus.messages)}")

    for i, msg in enumerate(message_bus.messages, 1):
        print(f"\n{i}. {msg.sender} -> {msg.receiver}")
        print(f"   Type: {msg.message_type}")
        print(f"   Request ID: {msg.request_id}")

    return result


# ========================================
# MAIN
# ========================================

def main():
    """Demonstrate A2A protocol."""

    # Sample order
    order = {
        "order_id": "ORD-12345",
        "product_id": "PROD-789",
        "quantity": 2,
        "amount": 99.99,
        "address": "123 Main St, San Francisco, CA 94105"
    }

    # Register agents with message bus
    message_bus.register_agent("order_agent", order_agent)
    message_bus.register_agent("inventory_agent", "InventoryAgent")
    message_bus.register_agent("payment_agent", "PaymentAgent")
    message_bus.register_agent("shipping_agent", "ShippingAgent")

    # Process order
    result = process_order_with_a2a(order)

    print(f"\n{'='*80}")
    print("KEY BENEFITS OF A2A PROTOCOL")
    print(f"{'='*80}")
    print("✓ Decoupled agent systems")
    print("✓ Standardized communication protocol")
    print("✓ Easy to add new agents")
    print("✓ Message traceability")
    print("✓ Cross-platform agent collaboration")


if __name__ == "__main__":
    main()
