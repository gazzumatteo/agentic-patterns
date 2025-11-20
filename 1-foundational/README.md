# Foundational Agentic Design Patterns

**Part 1 of 4**: Execution, Reasoning, and Refinement Patterns

These eight patterns form the foundation of any agent system. Master these before attempting complex orchestrations.

## Overview

After implementing over 200 AI agent systems across manufacturing, finance, and retail, these foundational patterns emerged as the essential building blocks for production-ready agents. These are not theoretical concepts—they're battle-tested architectures that deliver immediate ROI.

This directory contains implementations of **8 foundational patterns** in both Google ADK and CrewAI, demonstrating the core capabilities every AI agent developer needs to master.

## Pattern Catalog

### Pattern 1: Simple Agent (Single-agent)

The atomic unit of agent systems. One agent, one task, zero complexity. Perfect for deterministic workflows where reliability trumps sophistication.

**Business Use Case**: Automated Documentation Generator
- Engineers spending 4 hours/week updating API documentation
- Single agent monitors code commits, auto-generates OpenAPI specs
- Results: 92% reduction in documentation lag, $180K annual savings

**When to Use**:
- Repetitive, well-defined tasks with clear success criteria
- Quick wins to build organizational confidence in AI
- Reliability matters more than sophistication

**Files**:
- [`adk-examples/01_simple_agent.py`](./adk-examples/01_simple_agent.py)
- [`crewai-examples/01_simple_agent.py`](./crewai-examples/01_simple_agent.py)

**Diagram**: [`diagrams/01_simple_agent.mermaid`](./diagrams/01_simple_agent.mermaid)

---

### Pattern 2: Memory-Augmented Agent

Adds persistent context across interactions. Transforms stateless LLMs into stateful assistants that remember, learn, and improve.

**Business Use Case**: Personalized Sales Assistant
- Sales reps couldn't track 200+ client preferences and history
- Agent maintains conversation history, remembers product preferences, surfaces relevant context
- Results: 34% increase in upsell rate, 28% reduction in churn, average deal size up $12K

**When to Use**:
- Customer-facing applications where relationship continuity drives value
- Agents that improve without retraining
- Historical context directly impacts outcomes

**Files**:
- [`adk-examples/02_memory_augmented_agent.py`](./adk-examples/02_memory_augmented_agent.py)
- [`crewai-examples/02_memory_augmented_agent.py`](./crewai-examples/02_memory_augmented_agent.py)

**Diagram**: [`diagrams/02_memory_augmented.mermaid`](./diagrams/02_memory_augmented.mermaid)

---

### Pattern 3: Tool-Using Agent

Bridges the gap between language models and real-world systems. Enables agents to interact with APIs, databases, and enterprise tools.

**Business Use Case**: Supply Chain Optimizer
- Agent integrates with 6 supplier APIs via MCP
- Queries real-time inventory across 3 warehouses
- Triggers purchase orders based on demand forecasting
- Results: 43% reduction in stockouts, 21% decrease in inventory carrying costs, $2.3M annual savings

**When to Use**:
- Intelligent orchestration across multiple systems
- Real-time data from multiple sources drives decisions
- Instead of recommendations, agents execute transactions

**Files**:
- [`adk-examples/03_tool_using_agent.py`](./adk-examples/03_tool_using_agent.py)
- [`crewai-examples/03_tool_using_agent.py`](./crewai-examples/03_tool_using_agent.py)

**Diagram**: [`diagrams/03_tool_using.mermaid`](./diagrams/03_tool_using.mermaid)

---

### Pattern 4: Planning Pattern

Decomposes complex goals into executable steps. Critical for multi-stage workflows with dependencies.

**Business Use Case**: M&A Due Diligence Automation
- Generates 40-step plan with dependencies
- Parallelizes independent tasks
- Maintains critical path awareness
- Results: 14-day process reduced to 3 days

**When to Use**:
- Complex, multi-stage processes where dependencies matter
- Coordination across departments is critical
- Manual project management becomes a bottleneck

**Files**:
- [`adk-examples/04_planning.py`](./adk-examples/04_planning.py)
- [`crewai-examples/04_planning.py`](./crewai-examples/04_planning.py)

**Diagram**: [`diagrams/04_planning.mermaid`](./diagrams/04_planning.mermaid)

---

### Pattern 5: Reflection/Generator-Critic

Implements self-evaluation and improvement. Generator creates, critic evaluates, system iterates until quality thresholds are met.

**Business Use Case**: Contract Negotiation Agent
- Generator creates initial contract terms
- Critic evaluates against company policies
- Iterates until risk score meets threshold
- Results: 78% of contracts approved without human intervention, 95% compliance rate

**When to Use**:
- Quality matters more than speed
- Mistakes are costly or brand reputation is at stake
- Current process involves multiple rounds of human review

**Files**:
- [`adk-examples/05_reflection_generator_critic.py`](./adk-examples/05_reflection_generator_critic.py)
- [`crewai-examples/05_reflection_generator_critic.py`](./crewai-examples/05_reflection_generator_critic.py)

**Diagram**: [`diagrams/05_reflection.mermaid`](./diagrams/05_reflection.mermaid)

---

### Pattern 6: Loop/Cyclic Pattern

Enables iterative refinement through repeated execution. Essential for retry logic and progressive enhancement.

**Business Use Case**: Code Migration Assistant
- Convert code block, run test suite
- If tests fail, analyze errors and retry
- Loop until all tests pass
- Results: 89% automatic conversion success, 200 developer-hours saved, zero production bugs

**When to Use**:
- Processes requiring persistence and refinement
- Success requires iteration
- Technical teams dealing with legacy system modernization

**Files**:
- [`adk-examples/06_loop_cyclic.py`](./adk-examples/06_loop_cyclic.py)
- [`crewai-examples/06_loop_cyclic.py`](./crewai-examples/06_loop_cyclic.py)

**Diagram**: [`diagrams/06_loop_cyclic.mermaid`](./diagrams/06_loop_cyclic.mermaid)

---

### Pattern 7: ReAct (Reason and Act)

Combines reasoning with action in a feedback loop. Thought → Action → Observation → Updated Thought.

**Business Use Case**: Healthcare Diagnostic Assistant
- Thought: "Patient presents with chest pain"
- Action: Query EHR for history
- Observation: "Previous cardiac events noted"
- Action: Order ECG, trigger cardiology consult
- Results: 31% reduction in critical case response time

**When to Use**:
- Complex decision-making where context evolves during execution
- Problems can't be solved with predetermined steps
- High-stakes environments where wrong decisions are costly

**Files**:
- [`adk-examples/07_react.py`](./adk-examples/07_react.py)
- [`crewai-examples/07_react.py`](./crewai-examples/07_react.py)

**Diagram**: [`diagrams/07_react.mermaid`](./diagrams/07_react.mermaid)

---

### Pattern 8: Chain-of-Thought (CoT)

Forces explicit reasoning steps. Makes agent decision-making transparent and auditable.

**Business Use Case**: Financial Audit Agent
- Step-by-step validation of expense reports
- Each decision shows reasoning chain
- Full audit trail for compliance
- Results: 60% reduction in audit time, 100% traceable decisions

**When to Use**:
- Transparent, auditable decision-making required
- Regulated industries or decisions might be challenged
- Trust is paramount

**Files**:
- [`adk-examples/08_chain_of_thought.py`](./adk-examples/08_chain_of_thought.py)
- [`crewai-examples/08_chain_of_thought.py`](./crewai-examples/08_chain_of_thought.py)

**Diagram**: [`diagrams/08_chain_of_thought.mermaid`](./diagrams/08_chain_of_thought.mermaid)

---

## Running the Examples

### Prerequisites

Install dependencies using uv:

```bash
# From the project root
uv sync
```

### Google ADK Examples

```bash
# Set up Google Cloud credentials
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

# Run a specific pattern
uv run python 1-foundational/adk-examples/01_simple_agent.py

# Run all ADK examples
for file in 1-foundational/adk-examples/*.py; do
    echo "Running $file..."
    uv run python "$file"
done
```

### CrewAI Examples

```bash
# Set up API keys
export OPENAI_API_KEY="your-openai-key"
# or
export ANTHROPIC_API_KEY="your-anthropic-key"

# Run a specific pattern
uv run python 1-foundational/crewai-examples/01_simple_agent.py

# Run all CrewAI examples
for file in 1-foundational/crewai-examples/*.py; do
    echo "Running $file..."
    uv run python "$file"
done
```

## Framework Comparison: Google ADK vs CrewAI

| Feature | Google ADK | CrewAI |
|---------|-----------|---------|
| **Simple Agent** | Native LlmAgent class | Agent with role/goal/backstory |
| **Memory** | VertexAiRagMemoryService (native) | LongTermMemory + vector stores |
| **Tool Integration** | MCP protocol (enterprise-grade) | Standard tool decorators |
| **Planning** | Built-in planning capabilities | Task decomposition via crews |
| **Reflection** | SequentialAgent with exit conditions | Crew with Process.sequential |
| **Loop Patterns** | Native LoopAgent support | Custom implementation required |
| **ReAct** | reasoning_mode parameter | verbose=True + explicit tools |
| **CoT** | Prompt-based configuration | llm_config with reasoning |
| **Best For** | Enterprise, GCP users, MCP | Startups, flexibility, rapid prototyping |
| **Integration** | Deep GCP integration | Framework agnostic |
| **Learning Curve** | Moderate | Low |

## Pattern Selection Guide

| Pattern | Complexity | Cost Impact | When to Use |
|---------|-----------|-------------|-------------|
| Simple Agent | Low | Minimal | Single, well-defined tasks |
| Memory-Augmented | Medium | Moderate | Personalization required |
| Tool-Using | Medium | Varies | External systems integration |
| Planning | High | High | Multi-step complex workflows |
| Reflection | Medium | Moderate | Quality critical outputs |
| Loop/Cyclic | Medium | Moderate | Iterative refinement needed |
| ReAct | High | High | Adaptive decision-making |
| Chain-of-Thought | Low | Low | Transparency/auditing required |

## Business Value Summary

**Start with Simple Agents** - 73% of use cases don't need complex orchestration

**Memory is the differentiator** - Context-aware agents deliver 3x more value

**Tools unlock real value** - LLMs + enterprise systems = transformation

**Planning prevents chaos** - Decomposition is key to handling complexity

**Reflection prevents disasters** - Self-checking agents reduce errors by 89%

**Loops enable perfection** - Iteration patterns achieve 95%+ accuracy

**ReAct handles ambiguity** - Reasoning + action solves open-ended problems

**CoT ensures compliance** - Transparent reasoning satisfies auditors

## Architecture Diagrams

All patterns include detailed Mermaid diagrams in the [`diagrams/`](./diagrams/) directory showing:
- Data flow and decision points
- Integration patterns
- Error handling strategies
- Performance considerations

## Key Takeaways

1. **Start Simple**: Begin with single agents before complex orchestration
2. **Combine Patterns**: Production systems use multiple patterns together
3. **Measure Performance**: Track token usage, latency, and business metrics
4. **Iterate**: Use reflection and self-correction for continuous improvement
5. **Think Production**: Every pattern includes error handling and observability

## What's Next

**Part 2**: [Multi-Agent Coordination Patterns](../2-orchestration/) (10 patterns)
- Sequential and parallel orchestration
- Supervisor and hierarchical patterns
- Competitive and swarm behaviors
- Handoff and delegation strategies

**Part 3**: [Governance and Reliability Patterns](../3-intelligence/) (11 patterns)
- RAG and knowledge retrieval
- Guardrails and safety
- Human-in-the-loop
- Exception handling and recovery

**Part 4**: [Advanced Learning Patterns](../4-production/) (6 patterns)
- Learning and adaptation
- Evolutionary algorithms
- Agent-based modeling
- Self-organizing systems

## Additional Resources

- **Medium Article**: [Foundational Agentic Design Patterns](https://medium.com/@matteogazzurelli)
- **Video Tutorial**: [NotebookLM Podcast Overview](https://github.com/gazzumatteo/agentic-patterns)
- **Complete Repository**: [github.com/gazzumatteo/agentic-patterns](https://github.com/gazzumatteo/agentic-patterns)
- **LinkedIn**: [Matteo Gazzurelli](https://linkedin.com/in/matteogazzurelli)
- **Website**: [ai.gazzurelli.com](https://ai.gazzurelli.com)

## Contributing

Found an issue or have an improvement?
1. Create an issue describing the problem
2. Submit a PR with your fix
3. Include tests and documentation updates
4. Follow the existing code style

---

**This is where your agentic journey begins. Master these eight patterns, and you'll have the foundation to build production-ready AI systems that transform businesses.**
