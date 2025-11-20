"""
Pattern 2: Memory-Augmented Agent
An agent with persistent memory to maintain context across interactions.

Business Example: Personalized Sales Assistant
- Company: RetailFlow (E-commerce, $50M revenue)
- Challenge: Sales team unable to track customer preferences across conversations
- Solution: Memory-augmented agent maintains conversation history per client
- Details: Remembers product preferences, budget constraints, past issues
- Results: 34% increase in upsell, 28% reduction in churn

This example demonstrates memory-augmented agents using CrewAI's memory features.

Mermaid Diagram Reference: See diagrams/02_memory_augmented_agent.mermaid
"""

from datetime import datetime
from typing import Dict, List, Optional
from crewai import Agent, Task, Crew
from crewai.memory import EntityMemory, LongTermMemory, ShortTermMemory


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

sales_agent = Agent(
    role="Personalized Sales Assistant",
    goal="Provide personalized product recommendations based on customer history and preferences",
    backstory="""
    You are an experienced sales assistant at RetailFlow, an e-commerce platform.
    You excel at building long-term customer relationships by remembering their
    preferences, past purchases, and budget constraints. You provide personalized
    recommendations that truly match each customer's needs.
    """,
    verbose=False,
    allow_delegation=False,
    # Enable memory features (CrewAI automatically manages context)
    memory=True
)


# ========================================
# HELPER FUNCTIONS
# ========================================

def record_preference(customer_id: str, preference_type: str, value: any):
    """Record a customer preference in memory."""
    customer_memory.add_interaction(
        customer_id,
        {
            'type': 'preference',
            'content': f"{preference_type}: {value}",
            'data': {preference_type: value}
        }
    )


def record_purchase(customer_id: str, product: str, amount: float):
    """Record a customer purchase in memory."""
    customer_memory.add_interaction(
        customer_id,
        {
            'type': 'purchase',
            'content': f"Purchased {product} for ${amount}",
            'data': {'product': product, 'amount': amount}
        }
    )


# ========================================
# USAGE EXAMPLES
# ========================================

def chat_with_customer(
    customer_id: str,
    message: str,
    customer_preferences: Optional[Dict] = None
) -> str:
    """Handle customer interaction with memory context."""

    # Retrieve customer context from memory
    context = customer_memory.get_customer_context(customer_id)
    preferences = customer_memory.get_preferences(customer_id) or customer_preferences or {}

    # Create task with context
    task = Task(
        description=f"""
        You are assisting customer {customer_id}.

        {context}

        Customer Preferences:
        {preferences if preferences else 'None specified yet'}

        Current Customer Message:
        {message}

        Provide a helpful, personalized response that:
        1. Acknowledges their history if they're a returning customer
        2. References relevant past interactions or purchases
        3. Respects their stated preferences and budget
        4. Offers relevant recommendations
        5. Maintains a friendly, professional tone
        """,
        agent=sales_agent,
        expected_output="Personalized response to customer inquiry"
    )

    # Create crew with memory enabled
    crew = Crew(
        agents=[sales_agent],
        tasks=[task],
        verbose=False,
        memory=True  # Enable crew-level memory
    )

    result = crew.kickoff()
    response_text = result.raw if hasattr(result, 'raw') else str(result)

    # Store interaction in memory
    customer_memory.add_interaction(
        customer_id,
        {
            'type': 'conversation',
            'content': f"Customer: {message}\nAssistant: {response_text}"
        }
    )

    return response_text


def main():
    """Main execution demonstrating the memory-augmented agent pattern."""

    print(f"\n{'='*80}")
    print("Pattern 2: Memory-Augmented Agent - CrewAI")
    print(f"{'='*80}\n")

    # Scenario: Multi-session customer interaction
    customer_id = "CUST_12345"

    # ========== SESSION 1: Initial Interaction ==========
    print("="*80)
    print("SESSION 1: Initial Customer Contact")
    print("="*80)

    response = chat_with_customer(
        customer_id,
        "Hi, I'm looking for a laptop for software development. My budget is around $1500."
    )
    print(f"\nAssistant: {response}\n")

    # Record preferences
    record_preference(customer_id, "budget", 1500)
    record_preference(customer_id, "category", "laptops")
    record_preference(customer_id, "use_case", "software_development")

    # ========== SESSION 2: Follow-up ==========
    print("="*80)
    print("SESSION 2: Customer Returns (Same Day)")
    print("="*80)

    response = chat_with_customer(
        customer_id,
        "I'm back. I forgot to mention I need at least 16GB RAM and good battery life."
    )
    print(f"\nAssistant: {response}\n")

    record_preference(customer_id, "ram", "16GB+")
    record_preference(customer_id, "battery", "long_life")

    # Simulate purchase
    record_purchase(customer_id, "Dell XPS 15 Developer Edition", 1499.99)

    # ========== SESSION 3: Future Interaction ==========
    print("="*80)
    print("SESSION 3: Customer Returns (Two Weeks Later)")
    print("="*80)

    response = chat_with_customer(
        customer_id,
        "Hi again! I need a wireless mouse to go with my new laptop. Any recommendations?"
    )
    print(f"\nAssistant: {response}\n")

    # ========== SESSION 4: Upsell Opportunity ==========
    print("="*80)
    print("SESSION 4: Proactive Recommendation")
    print("="*80)

    response = chat_with_customer(
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
    main()
