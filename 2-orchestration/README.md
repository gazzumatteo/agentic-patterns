# Multi-Agent Coordination Patterns

**Part 2 of 4**: Orchestrating Complex AI Workflows at Scale

Single agents solve problems. Coordinated agents transform industries.

## Overview

This directory covers **10 essential coordination patterns** that enable agents to work together—from simple pipelines to complex swarm behaviors. These patterns power everything from supply chain optimization to creative content generation at scale.

Multi-agent coordination is where automation becomes intelligence. By orchestrating multiple specialized agents, you can tackle complex business challenges that single agents can't solve efficiently.

## Pattern Catalog

### Pattern 9: Sequential Orchestration

Agents execute in strict order, each building on the previous agent's output. The backbone of deterministic workflows where sequence matters.

**Business Use Case**: Insurance Claim Processing
- 5-step pipeline: OCR → Validation → Fraud Detection → Adjuster → Payment
- Processing time: 5 days → 4 hours
- Manual touchpoints: 12 → 2
- Results: Fraud detection rate up 34%, customer satisfaction 4.2 → 4.7 stars, $8.2M annual savings

**When to Use**:
- Process requires strict order and compliance
- Audit trails are mandatory
- Each step must complete successfully before the next begins
- Reliability trumps speed

**Files**:
- [`adk-examples/09_sequential_orchestration.py`](./adk-examples/09_sequential_orchestration.py)
- [`crewai-examples/09_sequential_orchestration.py`](./crewai-examples/09_sequential_orchestration.py)

**Diagram**: [`diagrams/09_sequential_orchestration.mermaid`](./diagrams/09_sequential_orchestration.mermaid)

---

### Pattern 10: Parallel Orchestration

Multiple agents work simultaneously on independent tasks. Fan-out for distribution, fan-in for aggregation. Speed through parallelism.

**Business Use Case**: Real-Time Market Analysis
- 15 agents analyzing different market indicators simultaneously
- Signal generation: 45 seconds → 3 seconds
- Data sources analyzed: 6 → 47
- Results: Alpha generation +180 basis points, infrastructure cost -60%

**When to Use**:
- Speed determines competitive advantage
- Multiple perspectives need synthesis
- Tasks are truly independent
- High-throughput processing required

**Files**:
- [`adk-examples/10_parallel_orchestration.py`](./adk-examples/10_parallel_orchestration.py)
- [`crewai-examples/10_parallel_orchestration.py`](./crewai-examples/10_parallel_orchestration.py)

**Diagram**: [`diagrams/10_parallel_orchestration.mermaid`](./diagrams/10_parallel_orchestration.mermaid)

---

### Pattern 11: Supervisor Pattern (Router)

A coordinator agent analyzes requests and delegates to specialized workers. Dynamic routing based on content, not predetermined paths.

**Business Use Case**: Intelligent IT Helpdesk
- Supervisor classifies tickets in real-time
- Routes to: Password Reset Bot, Software Install Agent, Hardware Request Agent, or Human Expert
- First-contact resolution: 31% → 67%
- Results: Average resolution time 6 hours → 35 minutes, ticket volume to humans -73%, $4.1M annual savings

**When to Use**:
- Diverse, unpredictable workloads
- Manual routing is a bottleneck
- Expertise is scarce or expensive
- Resource utilization needs optimization

**Files**:
- [`adk-examples/11_supervisor_router.py`](./adk-examples/11_supervisor_router.py)
- [`crewai-examples/11_supervisor_router.py`](./crewai-examples/11_supervisor_router.py)

**Diagram**: [`diagrams/11_supervisor_router.mermaid`](./diagrams/11_supervisor_router.mermaid)

---

### Pattern 12: Hierarchical Pattern

Multi-level management structure. Managers delegate to supervisors who coordinate workers. Mirrors organizational hierarchies.

**Business Use Case**: Global Supply Chain Coordination
- Three-tier architecture: Strategic Agent → Regional Agents (4) → Operational Agents (20)
- Inventory turns: 8 → 12 per year
- Stockout events: -67%
- Results: Working capital reduction $45M, on-time delivery 87% → 96%

**When to Use**:
- Scale requires multiple management layers
- Different levels require different decision-making types
- Centralized control would create bottlenecks
- Clear accountability and reporting structures needed

**Files**:
- [`adk-examples/12_hierarchical.py`](./adk-examples/12_hierarchical.py)
- [`crewai-examples/12_hierarchical.py`](./crewai-examples/12_hierarchical.py)

**Diagram**: [`diagrams/12_hierarchical.mermaid`](./diagrams/12_hierarchical.mermaid)

---

### Pattern 13: Competitive Pattern

Multiple agents solve the same problem differently. Best solution wins. Drives innovation through competition.

**Business Use Case**: Creative Campaign Generation
- 5 copywriter agents generate unique campaign concepts
- Evaluator scores on: brand alignment, creativity, conversion potential
- Campaign performance: +43% CTR
- Results: Creative production time 2 weeks → 2 days, client approval rate 68% → 91%, cost per campaign -55%

**When to Use**:
- Quality matters more than consensus
- Novel problems without clear solutions
- High-stakes decisions where suboptimal solutions are costly
- Creative fields where diversity drives value

**Files**:
- [`adk-examples/13_competitive.py`](./adk-examples/13_competitive.py)
- [`crewai-examples/13_competitive.py`](./crewai-examples/13_competitive.py)

**Diagram**: [`diagrams/13_competitive.mermaid`](./diagrams/13_competitive.mermaid)

---

### Pattern 14: Network/Swarm Pattern

Decentralized, peer-to-peer agent communication. No central authority. Collective intelligence emerges from local interactions.

**Business Use Case**: Warehouse Robot Coordination
- 200 autonomous robots communicate peer-to-peer
- No central traffic controller, self-organizing task allocation
- Pick rate: 180 → 340 items/hour
- Results: Collision incidents 0 in 6 months, system resilience (30% robots can fail), energy efficiency +26%

**When to Use**:
- Resilience matters more than control
- Central coordination would create single points of failure
- Operating in unpredictable environments
- Distributed systems, edge computing

**Files**:
- [`adk-examples/14_network_swarm.py`](./adk-examples/14_network_swarm.py)
- [`crewai-examples/14_network_swarm.py`](./crewai-examples/14_network_swarm.py)

**Diagram**: [`diagrams/14_network_swarm.mermaid`](./diagrams/14_network_swarm.mermaid)

---

### Pattern 15: Handoff Orchestration (Delegation)

Dynamic task transfer between agents based on expertise. Includes context preservation during handoffs.

**Business Use Case**: Complex Loan Origination
- Simple loans: Basic agent (70% of volume)
- Complex cases: Specialist agent with underwriting logic
- Edge cases: Senior credit officer agent
- Application to approval: 3 days → 6 hours
- Results: Approval accuracy 94% → 97%, compliance violations -89%, revenue per loan officer +220%

**When to Use**:
- Quality needs optimization while maintaining costs
- Complexity varies significantly between cases
- Currently overpaying for routine work
- Context preservation prevents customer frustration

**Files**:
- [`adk-examples/15_handoff_delegation.py`](./adk-examples/15_handoff_delegation.py)
- [`crewai-examples/15_handoff_delegation.py`](./crewai-examples/15_handoff_delegation.py)

**Diagram**: [`diagrams/15_handoff_delegation.mermaid`](./diagrams/15_handoff_delegation.mermaid)

---

### Pattern 16: Blackboard Pattern

Shared workspace where agents asynchronously contribute to evolving solutions. Collaborative problem-solving through incremental refinement.

**Business Use Case**: Collaborative Product Design
- Industrial Designer, Engineer, Cost Analyst, Marketing agents all iterate on shared design document
- Design cycles: 6 months → 6 weeks
- Prototype iterations: 8 → 3
- Results: Market fit score 7.2 → 8.9, development cost -40%

**When to Use**:
- Complex problems requiring diverse expertise
- Answer emerges from collective intelligence
- Problems span multiple domains
- Innovation through incremental contributions

**Files**:
- [`adk-examples/16_blackboard.py`](./adk-examples/16_blackboard.py)
- [`crewai-examples/16_blackboard.py`](./crewai-examples/16_blackboard.py)

**Diagram**: [`diagrams/16_blackboard.mermaid`](./diagrams/16_blackboard.mermaid)

---

### Pattern 17: Magentic Orchestration

Dynamic plan generation with task ledger management. Agents create and update execution plans in real-time.

**Business Use Case**: Dynamic Project Management
- Manager agent creates initial project plan
- Continuously updates task ledger based on progress
- Re-allocates resources dynamically
- On-time delivery: 62% → 94%
- Results: Resource utilization 71% → 89%, client change requests handled 3x faster, project profitability +28%

**When to Use**:
- Projects in dynamic environments
- Plans must evolve with reality
- Traditional project management struggles with constant change
- Learning during execution is important

**Files**:
- [`adk-examples/17_magentic_orchestration.py`](./adk-examples/17_magentic_orchestration.py)
- [`crewai-examples/17_magentic_orchestration.py`](./crewai-examples/17_magentic_orchestration.py)

**Diagram**: [`diagrams/17_magentic_orchestration.mermaid`](./diagrams/17_magentic_orchestration.mermaid)

---

### Pattern 18: Market-Based Pattern

Agents bid for tasks or resources. Economic principles drive resource allocation and task distribution.

**Business Use Case**: Cloud Resource Allocation
- Compute agents bid for incoming jobs
- Pricing based on current load and capabilities
- Automatic load balancing through market dynamics
- Resource utilization: 68% → 91%
- Results: Customer cost -23% average, SLA compliance 99.95% → 99.99%, revenue per server +41%

**When to Use**:
- Resource allocation where demand exceeds supply
- Transparent, efficient allocation needed
- Priorities shift rapidly
- Politics-free resource distribution required

**Files**:
- [`adk-examples/18_market_based.py`](./adk-examples/18_market_based.py)
- [`crewai-examples/18_market_based.py`](./crewai-examples/18_market_based.py)

**Diagram**: [`diagrams/18_market_based.mermaid`](./diagrams/18_market_based.mermaid)

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
uv run python 2-orchestration/adk-examples/09_sequential_orchestration.py

# Run all ADK examples
for file in 2-orchestration/adk-examples/*.py; do
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
uv run python 2-orchestration/crewai-examples/09_sequential_orchestration.py

# Run all CrewAI examples
for file in 2-orchestration/crewai-examples/*.py; do
    echo "Running $file..."
    uv run python "$file"
done
```

## Framework Comparison: Google ADK vs CrewAI

| Feature | Google ADK | CrewAI |
|---------|-----------|---------|
| **Sequential** | SequentialAgent with state passing | Crew with Process.sequential |
| **Parallel** | ParallelAgent with aggregator | Crew with Process.parallel |
| **Supervisor** | LlmAgent with delegates | Agent with delegation_strategy |
| **Hierarchical** | Multi-level agent structure | Crew with Process.hierarchical |
| **Competitive** | ParallelAgent with selection_method | Crew with Process.competitive |
| **Swarm** | A2A mesh network protocol | Crew with Process.swarm |
| **Handoff** | Dynamic delegate selection | Context preservation between agents |
| **Blackboard** | VectorStore shared state | SharedMemoryStore |
| **Magentic** | Dynamic task ledger management | Adaptive planning strategy |
| **Market-Based** | Bidding and auction mechanisms | Market-based allocation |
| **Best For** | Enterprise orchestration, GCP | Flexible multi-agent systems |
| **Coordination** | Native coordination primitives | Process-based abstractions |
| **Scalability** | Handles 1000+ agents | Optimized for dozens of agents |

## Pattern Selection Guide

| Pattern | Complexity | Scalability | When to Use |
|---------|-----------|-------------|-------------|
| Sequential | Low | Medium | Strict ordering required |
| Parallel | Medium | High | Independent tasks, speed critical |
| Supervisor | Medium | High | Dynamic routing needed |
| Hierarchical | High | Very High | Multi-level management |
| Competitive | Medium | Medium | Quality over speed |
| Network/Swarm | High | Very High | Resilience, no single point of failure |
| Handoff | Medium | Medium | Variable complexity tasks |
| Blackboard | High | Medium | Collaborative problem-solving |
| Magentic | High | Medium | Dynamic environments |
| Market-Based | Medium | High | Resource optimization |

## Business Value Summary

**Sequential for Compliance** - When audit trails and determinism are non-negotiable

**Parallel for Speed** - 10x faster with proper task decomposition

**Supervisor for Flexibility** - Dynamic routing beats static workflows

**Hierarchical for Scale** - Natural way to manage complexity

**Competitive for Quality** - Multiple attempts yield superior results

**Swarm for Resilience** - No single point of failure

**Handoff for Expertise** - Right agent for the right task

**Blackboard for Collaboration** - Collective intelligence emerges

**Magentic for Adaptation** - Plans that evolve with reality

**Market for Optimization** - Economic principles drive efficiency

## Multi-Agent Coordination Considerations

### Performance

- **Sequential**: Slowest but most reliable
- **Parallel**: Fastest for independent tasks
- **Hierarchical**: Scales linearly with agents
- **Swarm**: Scales exponentially with resilience

### Cost

- **Sequential**: Predictable, moderate cost
- **Parallel**: Higher concurrent costs, faster completion
- **Competitive**: Multiple attempts = higher cost, better results
- **Market-Based**: Self-optimizing cost allocation

### Complexity

- **Simple**: Sequential, Parallel, Supervisor
- **Moderate**: Handoff, Competitive, Market-Based
- **Advanced**: Hierarchical, Swarm, Blackboard, Magentic

## Architecture Diagrams

All patterns include detailed Mermaid diagrams in the [`diagrams/`](./diagrams/) directory showing:
- Agent communication flows
- Coordination mechanisms
- State management
- Error handling strategies
- Performance optimization points

## Key Takeaways

1. **Start with Sequential**: Understand pipeline coordination before complexity
2. **Parallel for Scale**: Decompose properly for maximum parallelism
3. **Supervisor for Flexibility**: Dynamic routing adapts to changing needs
4. **Hierarchical Mirrors Reality**: Organizational structure = agent structure
5. **Competition Drives Quality**: Multiple solutions beat single attempts
6. **Swarm for Resilience**: Decentralized coordination prevents cascading failures
7. **Handoff Optimizes Resources**: Match expertise to task complexity
8. **Blackboard Enables Innovation**: Asynchronous collaboration compounds insights
9. **Magentic Handles Change**: Adaptive planning beats rigid schedules
10. **Markets Balance Resources**: Economic principles optimize allocation

## What's Next

**Part 3**: [Governance and Reliability Patterns](../3-intelligence/) (11 patterns)
- RAG and Agentic RAG
- MCP and A2A protocols
- Guardrails and safety
- Exception handling and recovery
- Human-in-the-loop
- Resource optimization
- Prioritization and goal setting

**Part 4**: [Advanced Learning Patterns](../4-production/) (6 patterns)
- Learning and adaptation
- Exploration and discovery
- Evolutionary curriculum
- Self-organizing modular agents
- Maker-checker loops
- Agent-based modeling

## Additional Resources

- **Medium Article**: [Multi-Agent Coordination Patterns](https://medium.com/@matteogazzurelli)
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

**Master multi-agent coordination and unlock the power of collaborative intelligence. These patterns transform isolated automation into orchestrated systems that solve complex business challenges at scale.**
