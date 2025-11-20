"""
Pattern 2: Memory-Augmented Agent
An agent with persistent memory to maintain context across interactions.

Business Example: Personalized Sales Assistant
- Company: RetailFlow (E-commerce, $50M revenue)
- Challenge: Sales team unable to track customer preferences across conversations
- Solution: Memory-augmented agent maintains conversation history per client
- Details: Remembers product preferences, budget constraints, past issues
- Results: 34% increase in upsell, 28% reduction in churn

This pattern is crucial for creating personalized, context-aware interactions
that feel natural and maintain continuity across multiple sessions.

Mermaid Diagram Reference: See diagrams/02_memory_augmented_agent.mermaid
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Load environment variables
load_dotenv()


# ========================================
# MEMORY STORAGE
# ========================================

class CustomerMemory:
    """Simple in-memory storage for customer interactions."""

    def __init__(self):
        self.memories: Dict[str, List[Dict]] = {}

    def add_interaction(self, customer_id: str, interaction: Dict):
        """Add an interaction to customer's memory."""
        if customer_id not in self.memories:
            self.memories[customer_id] = []

        interaction['timestamp'] = datetime.now().isoformat()
        self.memories[customer_id].append(interaction)

    def get_customer_context(self, customer_id: str) -> str:
        """Retrieve formatted context for a customer."""
        if customer_id not in self.memories:
            return "New customer - no previous interactions"

        interactions = self.memories[customer_id]
        context_parts = [f"Previous interactions with {customer_id}:"]

        for i, interaction in enumerate(interactions[-5:], 1):  # Last 5 interactions
            context_parts.append(
                f"\n{i}. [{interaction['timestamp']}] "
                f"{interaction['type']}: {interaction['content']}"
            )

        return "\n".join(context_parts)

    def get_preferences(self, customer_id: str) -> Optional[Dict]:
        """Extract customer preferences from memory."""
        if customer_id not in self.memories:
            return None

        # Simple extraction - in production, use embedding search
        preferences = {}
        for interaction in self.memories[customer_id]:
            if interaction['type'] == 'preference':
                preferences.update(interaction.get('data', {}))

        return preferences if preferences else None


# Initialize global memory storage
customer_memory = CustomerMemory()


# ========================================
# MEMORY-AUGMENTED AGENT DEFINITION
# ========================================

sales_agent = LlmAgent(
    name="PersonalizedSalesAssistant",
    model="gemini-2.5-flash",
    instruction="""
    You are a personalized sales assistant for RetailFlow, an e-commerce platform.

    Your role:
    - Help customers find products that match their preferences
    - Remember and reference past interactions
    - Provide personalized recommendations
    - Track budget constraints and preferences
    - Build long-term customer relationships

    Guidelines:
    - Always acknowledge returning customers warmly
    - Reference their previous purchases or interests when relevant
    - Respect their stated budget and preferences
    - Be helpful, friendly, and professional
    - Ask clarifying questions to better understand their needs

    When you receive customer context, use it to personalize your responses.
    """,
    description="Sales assistant with customer memory"
)


# ========================================
# USAGE EXAMPLES
# ========================================

async def chat_with_customer(
    customer_id: str,
    message: str,
    customer_preferences: Optional[Dict] = None
) -> str:
    """Handle customer interaction with memory context."""

    # Retrieve customer context from memory
    context = customer_memory.get_customer_context(customer_id)
    preferences = customer_memory.get_preferences(customer_id) or customer_preferences or {}

    # Create runner
    runner = InMemoryRunner(
        agent=sales_agent,
        app_name="sales_assistant"
    )

    # Create session (in production, maintain session per customer)
    session = await runner.session_service.create_session(
        app_name="sales_assistant",
        user_id=customer_id
    )

    # Build context-aware message
    full_message = f"""
    Customer ID: {customer_id}

    {context}

    Customer Preferences:
    {preferences if preferences else 'None specified yet'}

    Current Message: {message}
    """

    # Prepare message
    content = types.Content(
        role='user',
        parts=[types.Part(text=full_message)]
    )

    # Run agent
    events = runner.run_async(
        user_id=customer_id,
        session_id=session.id,
        new_message=content
    )

    # Collect response
    response_text = None
    async for event in events:
        if event.is_final_response() and event.content:
            response_text = event.content.parts[0].text
            break

    # Store interaction in memory
    customer_memory.add_interaction(
        customer_id,
        {
            'type': 'conversation',
            'content': f"Customer: {message}\nAssistant: {response_text}"
        }
    )

    return response_text


async def record_preference(customer_id: str, preference_type: str, value: any):
    """Record a customer preference in memory."""
    customer_memory.add_interaction(
        customer_id,
        {
            'type': 'preference',
            'content': f"{preference_type}: {value}",
            'data': {preference_type: value}
        }
    )


async def record_purchase(customer_id: str, product: str, amount: float):
    """Record a customer purchase in memory."""
    customer_memory.add_interaction(
        customer_id,
        {
            'type': 'purchase',
            'content': f"Purchased {product} for ${amount}",
            'data': {'product': product, 'amount': amount}
        }
    )


async def main():
    """Main execution demonstrating the memory-augmented agent pattern."""

    print(f"\n{'='*80}")
    print("Pattern 2: Memory-Augmented Agent")
    print(f"{'='*80}\n")

    # Scenario: Multi-session customer interaction
    customer_id = "CUST_12345"

    # ========== SESSION 1: Initial Interaction ==========
    print("="*80)
    print("SESSION 1: Initial Customer Contact")
    print("="*80)

    response = await chat_with_customer(
        customer_id,
        "Hi, I'm looking for a laptop for software development. My budget is around $1500."
    )
    print(f"\nAssistant: {response}\n")

    # Record preferences
    await record_preference(customer_id, "budget", 1500)
    await record_preference(customer_id, "category", "laptops")
    await record_preference(customer_id, "use_case", "software_development")

    # ========== SESSION 2: Follow-up ==========
    print("="*80)
    print("SESSION 2: Customer Returns (Same Day)")
    print("="*80)

    response = await chat_with_customer(
        customer_id,
        "I'm back. I forgot to mention I need at least 16GB RAM and good battery life."
    )
    print(f"\nAssistant: {response}\n")

    await record_preference(customer_id, "ram", "16GB+")
    await record_preference(customer_id, "battery", "long_life")

    # Simulate purchase
    await record_purchase(customer_id, "Dell XPS 15 Developer Edition", 1499.99)

    # ========== SESSION 3: Future Interaction ==========
    print("="*80)
    print("SESSION 3: Customer Returns (Two Weeks Later)")
    print("="*80)

    response = await chat_with_customer(
        customer_id,
        "Hi again! I need a wireless mouse to go with my new laptop. Any recommendations?"
    )
    print(f"\nAssistant: {response}\n")

    # ========== SESSION 4: Upsell Opportunity ==========
    print("="*80)
    print("SESSION 4: Proactive Recommendation")
    print("="*80)

    response = await chat_with_customer(
        customer_id,
        "What accessories would complement my setup?"
    )
    print(f"\nAssistant: {response}\n")

    # Display memory summary
    print("="*80)
    print("CUSTOMER MEMORY SUMMARY")
    print("="*80)
    print(customer_memory.get_customer_context(customer_id))
    print(f"\nPreferences: {customer_memory.get_preferences(customer_id)}\n")

    print("="*80)
    print("Pattern Demonstrated: Memory-Augmented Agent")
    print("="*80)
    print("""
Key Concepts:
1. Persistent memory across multiple interactions
2. Context retrieval and injection into prompts
3. Preference tracking and personalization
4. Historical interaction reference
5. Long-term customer relationship building

When to Use:
- Customer service and sales scenarios
- Personalized recommendations
- Multi-session conversations
- Scenarios requiring context continuity
- Building long-term user relationships

Business Value:
- 34% increase in upsell opportunities (RetailFlow)
- 28% reduction in customer churn
- Improved customer satisfaction through personalization
- Better conversion rates with context-aware interactions
- Reduced need for customers to repeat information

Technical Considerations:
- Memory storage strategy (in-memory, database, vector store)
- Context window management (last N interactions)
- Privacy and data retention policies
- Memory search and retrieval efficiency
- Session management across multiple channels
    """)


if __name__ == "__main__":
    asyncio.run(main())
