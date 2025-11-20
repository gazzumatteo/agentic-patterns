# Agentic Design Patterns: Complete Implementation Guide

A comprehensive 4-part series demonstrating 35 agentic design patterns with production-ready implementations in Google ADK and CrewAI.

## 📚 Series Overview

This repository accompanies a Medium article series exploring the complete landscape of agentic design patterns. Each article focuses on a specific theme with detailed implementations, Mermaid diagrams, and real-world business examples.

### Series Navigation

1. **[Foundational Patterns](./1-foundational/)** - 9 core building blocks
2. **[Orchestration & Collaboration](./2-orchestration/)** - 9 multi-agent patterns
3. **[Intelligence & Learning](./3-intelligence/)** - 9 adaptive patterns
4. **[Production & Safety](./4-production/)** - 8 enterprise patterns

## 🎯 What You'll Learn

- **35 Production-Ready Patterns**: From basic prompt chaining to advanced multi-agent orchestration
- **Dual Framework Implementation**: Every pattern implemented in both Google ADK and CrewAI
- **Real Business Examples**: E-commerce, finance, healthcare, and enterprise use cases
- **Visual Architecture**: Mermaid diagrams for every pattern
- **Performance Metrics**: Cost analysis, benchmarks, and optimization strategies

## 🏗️ Repository Structure

```
agentic-patterns/
├── 1-foundational/      # Core patterns (Prompt Chaining, Routing, etc.)
├── 2-orchestration/     # Multi-agent coordination (MCP, A2A, RAG)
├── 3-intelligence/      # Learning and adaptation patterns
├── 4-production/        # Safety, compliance, and scale patterns
├── shared-utilities/    # Reusable components and tools
├── diagrams/            # All Mermaid diagrams
└── docs/                # Guides and comparisons
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- uv (Python package manager)
- Google Cloud account (for ADK examples)
- API keys for OpenAI/Anthropic (for CrewAI examples)

### Installation

```bash
# Clone the repository
git clone https://github.com/gazzumatteo/agentic-patterns.git
cd agentic-patterns

# Install dependencies with uv
uv sync
```

### Environment Configuration

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Configure your API keys:**

   Open `.env` and follow the inline instructions to obtain and configure:

   - **Google Cloud (Required for ADK examples)**
     - Get your credentials from [Google Cloud Console](https://console.cloud.google.com/)
     - See detailed instructions in [.env.example](./.env.example)

   - **OpenAI (Optional - for CrewAI examples)**
     - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

   - **Anthropic (Optional - for CrewAI examples)**
     - Get your API key from [Anthropic Console](https://console.anthropic.com/settings/keys)

   - **Vector Stores (Optional - for RAG patterns)**
     - ChromaDB: Works locally, no setup required
     - Pinecone: Get credentials from [Pinecone.io](https://www.pinecone.io/)

   - **Monitoring Tools (Optional)**
     - LangSmith: [smith.langchain.com](https://smith.langchain.com/)
     - Weights & Biases: [wandb.ai](https://wandb.ai/)

   **📖 See [.env.example](./.env.example) for detailed setup instructions for each service.**

### Running Examples

```bash
# Run a Google ADK example
uv run python 1-foundational/adk-examples/01_prompt_chaining.py

# Run a CrewAI example
uv run python 1-foundational/crewai-examples/01_prompt_chaining.py
```

## 📖 Pattern Catalog

### Article 1: Foundational Patterns (8 patterns)
Core building blocks for individual agent behavior

| Pattern | Description | Use Case |
|---------|-------------|----------|
| Simple Agent | Single-agent, single-task execution | Documentation generation |
| Memory-Augmented Agent | Persistent context across interactions | Sales assistant |
| Tool-Using Agent | External API and system integration | Supply chain optimization |
| Planning Pattern | Multi-step strategy generation | M&A due diligence |
| Reflection/Generator-Critic | Self-evaluation and iterative refinement | Contract negotiation |
| Loop/Cyclic Pattern | Iterative execution with conditions | Code migration |
| ReAct | Reasoning + action in feedback loop | Medical diagnosis |
| Chain-of-Thought (CoT) | Explicit reasoning steps | Financial audit |

### Article 2: Multi-Agent Coordination (10 patterns)
Orchestrating complex AI workflows at scale

| Pattern | Description | Use Case |
|---------|-------------|----------|
| Sequential Orchestration | Agents execute in strict order | Insurance claim processing |
| Parallel Orchestration | Simultaneous independent execution | Market analysis |
| Supervisor Pattern | Dynamic routing to specialists | IT helpdesk |
| Hierarchical Pattern | Multi-level management structure | Global supply chain |
| Competitive Pattern | Multiple solutions, best wins | Creative campaigns |
| Network/Swarm Pattern | Decentralized peer coordination | Warehouse robots |
| Handoff Orchestration | Dynamic task transfer | Loan origination |
| Blackboard Pattern | Shared workspace collaboration | Product design |
| Magentic Orchestration | Dynamic plan with task ledger | Project management |
| Market-Based Pattern | Economic resource allocation | Cloud computing |

### Article 3: Governance & Reliability (11 patterns)
Making AI agents enterprise-ready

| Pattern | Description | Use Case |
|---------|-------------|----------|
| Knowledge Retrieval (RAG) | Grounding in verified data | Legal research |
| Agentic RAG | Reasoning layer on retrieval | Financial advisory |
| Tool Use with MCP | Standardized enterprise integration | ERP systems |
| Inter-Agent (A2A) | Cross-framework communication | Hybrid ecosystems |
| Guardrails/Safety | Input/output filters | Trading protection |
| Exception Handling | Resilience and recovery | Supply chain |
| Human-in-the-Loop (HITL) | Critical decision oversight | Medical diagnosis |
| Resource-Aware Optimization | Dynamic model selection | Cost management |
| Prioritization | Business impact scheduling | Customer service |
| Goal Setting & Monitoring | SMART goals with tracking | Sales pipeline |
| Checkpoint & Rollback | Restoration points | Database migration |

### Article 4: Advanced & Learning (6 patterns)
Agents that evolve and discover

| Pattern | Description | Use Case |
|---------|-------------|----------|
| Learning & Adaptation | Continuous improvement | Dynamic pricing |
| Exploration & Discovery | Hypothesis generation and testing | Drug interactions |
| Evolutionary Curriculum | Population-based optimization | Trading algorithms |
| Self-Organizing Modular | Dynamic module assembly | Universal support |
| Maker-Checker Loop | Creation with formal verification | Compliance automation |
| Agent-Based Modeling (ABM) | Complex system simulation | Supply chain resilience |

## 🛠️ Frameworks Compared

### Google ADK
- **Best For**: GCP-native applications, Vertex AI integration
- **Strengths**: Enterprise features, scalability, observability
- **Setup**: Requires Google Cloud project and credentials

### CrewAI
- **Best For**: Rapid prototyping, flexible agent teams
- **Strengths**: Intuitive API, role-based design, extensive tools
- **Setup**: Simple pip install, works with any LLM provider

See [Framework Selection Guide](./docs/framework-selection-guide.md) for detailed comparison.

## 📊 Benchmarks & Performance

Each pattern includes:
- **Execution Time**: Latency measurements
- **Token Usage**: Cost analysis
- **Success Rates**: Reliability metrics
- **Error Recovery**: Resilience testing

See [3-intelligence/benchmarks/](./3-intelligence/benchmarks/) for detailed results.

## 🎓 Learning Path

**Beginners**: Start with Article 1 (Foundational Patterns)
- Master basic patterns like Prompt Chaining and Tool Use
- Understand single-agent architectures
- Build your first production agent

**Intermediate**: Progress to Articles 2 & 3
- Implement multi-agent systems
- Add memory and learning capabilities
- Optimize performance and costs

**Advanced**: Complete with Article 4
- Deploy production-ready systems
- Implement enterprise security
- Achieve compliance and scale

## 📝 Documentation

- **[Pattern Comparison Matrix](./docs/pattern-comparison-matrix.md)**: Side-by-side pattern analysis
- **[Framework Selection Guide](./docs/framework-selection-guide.md)**: Choose ADK vs CrewAI
- **[Deployment Checklist](./docs/deployment-checklist.md)**: Production readiness guide
- **[CLAUDE.md](./CLAUDE.md)**: Development guidelines for contributors

## 🤝 Contributing

Contributions welcome! Please:
1. Follow the existing pattern structure
2. Include both ADK and CrewAI implementations
3. Add comprehensive docstrings and comments
4. Include unit tests
5. Update relevant documentation

## 📄 License

GPL-3.0 - See [LICENSE](./LICENSE) for details

## 🔗 Links

- **Medium Series**: [Coming Soon]
- **Video Tutorials**: [NotebookLM Channel]
- **Twitter Thread**: [@YourHandle]

## ⭐ Star History

If you find this helpful, please star the repo and share with others!

---

**Built with**: Google ADK, CrewAI, LangChain, Vertex AI
**Maintained by**: [Your Name]
**Last Updated**: November 2025