# Agentic Design Patterns: Comparison Matrix

Comprehensive comparison of all 35 agentic design patterns to help you choose the right pattern for your use case.

## Pattern Categories

1. **Foundational** (8 patterns) - Core building blocks
2. **Orchestration** (10 patterns) - Multi-agent coordination
3. **Governance & Reliability** (11 patterns) - Enterprise-ready patterns
4. **Advanced & Learning** (6 patterns) - Adaptive and learning behaviors

## Quick Reference Matrix

| Pattern | Category | Complexity | Cost | Use When | Avoid When |
|---------|----------|-----------|------|----------|------------|
| **Simple Agent** | Foundation | ⭐ Low | $ | Single deterministic task | Multi-step complexity needed |
| **Memory-Augmented** | Foundation | ⭐⭐ Med | $$ | Context across interactions | Stateless operations |
| **Tool-Using Agent** | Foundation | ⭐⭐ Med | $$ | External data/actions | All data in prompt |
| **Planning** | Foundation | ⭐⭐⭐ High | $$$ | Complex, dynamic goals | Simple, fixed workflow |
| **Reflection/Generator-Critic** | Foundation | ⭐⭐⭐ Med-High | $$$ | Quality critical | Speed > quality |
| **Loop/Cyclic** | Foundation | ⭐⭐ Med | $$ | Iterative refinement | One-shot execution |
| **ReAct** | Foundation | ⭐⭐⭐ Med-High | $$$ | Dynamic reasoning needed | Fixed workflow sufficient |
| **Chain-of-Thought (CoT)** | Foundation | ⭐⭐ Med | $$ | Transparency required | Black box acceptable |
| **Sequential Orchestration** | Orchestration | ⭐⭐ Med | $$ | Strict order required | Parallelization possible |
| **Parallel Orchestration** | Orchestration | ⭐⭐ Med | $$$ | Independent tasks | Tasks depend on each other |
| **Supervisor Pattern** | Orchestration | ⭐⭐⭐ High | $$$ | Dynamic routing | Fixed workflow |
| **Hierarchical Pattern** | Orchestration | ⭐⭐⭐⭐ Very High | $$$$ | Multi-level management | Flat structure works |
| **Competitive Pattern** | Orchestration | ⭐⭐⭐ High | $$$$ | Quality critical | Cost critical |
| **Network/Swarm** | Orchestration | ⭐⭐⭐⭐ Very High | $$$$ | Decentralized needed | Central control works |
| **Handoff Orchestration** | Orchestration | ⭐⭐ Med | $$ | Specialist handoffs | No specialization needed |
| **Blackboard Pattern** | Orchestration | ⭐⭐⭐ High | $$$ | Collaborative building | Simple pipeline works |
| **Magentic Orchestration** | Orchestration | ⭐⭐⭐ High | $$$ | Dynamic replanning | Static plan sufficient |
| **Market-Based** | Orchestration | ⭐⭐⭐⭐ Very High | $$$$ | Resource allocation | No scarcity issues |
| **RAG** | Governance | ⭐⭐⭐ Med-High | $$$ | Large knowledge base | All info fits in prompt |
| **Agentic RAG** | Governance | ⭐⭐⭐ High | $$$$ | Complex reasoning on data | Simple lookup sufficient |
| **MCP** | Governance | ⭐⭐⭐ High | $$ | Standardize tools | Simple, single tool |
| **A2A Protocol** | Governance | ⭐⭐⭐ High | $$$ | Cross-system agents | Same framework agents |
| **Guardrails** | Governance | ⭐⭐ Med | $$ | Always! Safety critical | Never skip in prod |
| **Exception Handling** | Governance | ⭐⭐ Med | $$ | Errors expected | Error-free environment |
| **HITL** | Governance | ⭐⭐ Med | $$$ | Critical decisions | Fully automated OK |
| **Resource Optimization** | Governance | ⭐⭐⭐ High | $$$ | Cost/performance balance | Cost not a concern |
| **Prioritization** | Governance | ⭐⭐ Med | $$ | Resource constraints | Unlimited resources |
| **Goal Monitoring** | Governance | ⭐⭐ Med | $$ | Long-running tasks | Single-shot queries |
| **Checkpoint/Rollback** | Governance | ⭐⭐ Med | $$ | Long-running, failable | Quick, reliable tasks |
| **Learning/Adaptation** | Advanced | ⭐⭐⭐⭐ Very High | $$$$ | Performance improvement | Static requirements |
| **Exploration** | Advanced | ⭐⭐⭐ High | $$$ | Discovery tasks | Known solutions exist |
| **Evolutionary Curriculum** | Advanced | ⭐⭐⭐⭐ Very High | $$$$ | Progressive learning | No learning needed |
| **Self-Organizing** | Advanced | ⭐⭐⭐⭐ Very High | $$$$ | Dynamic scaling | Fixed architecture |
| **Maker-Checker** | Advanced | ⭐⭐ Med | $$$ | Dual validation needed | Speed critical |
| **ABM** | Advanced | ⭐⭐⭐⭐ Very High | $$$$ | Simulation needed | Real-world execution |

## Detailed Pattern Comparison

### Foundational Patterns

#### Prompt Chaining vs Planning
| Aspect | Prompt Chaining | Planning |
|--------|----------------|----------|
| **Workflow** | Fixed sequence | Dynamic, adaptive |
| **Complexity** | Low | High |
| **Debuggability** | Excellent | Moderate |
| **Flexibility** | Low | High |
| **Best for** | Known multi-step processes | Open-ended goals |
| **Example** | Data ETL pipeline | Research project |

#### Parallelization vs Sequential
| Aspect | Parallelization | Sequential (Chaining) |
|--------|----------------|---------------------|
| **Speed** | Much faster | Slower |
| **Dependencies** | Tasks independent | Tasks dependent |
| **Complexity** | Higher | Lower |
| **Resource Use** | Burst usage | Steady usage |
| **Cost** | Potentially lower (faster = less time) | More predictable |

#### Reflection vs Self-Correction
| Aspect | Reflection | Self-Correction |
|--------|-----------|-----------------|
| **Critic** | Separate agent | Built-in validation |
| **Flexibility** | High | Moderate |
| **Iterations** | Limited (manual stop) | Automated (until valid) |
| **Use Case** | Subjective quality | Objective errors |

### Orchestration Patterns

#### Multi-Agent vs Single Agent with Tools
| Aspect | Multi-Agent | Single Agent + Tools |
|--------|------------|---------------------|
| **Complexity** | High | Low |
| **Specialization** | Agents are experts | Tools are specialized |
| **Coordination** | Required | Not needed |
| **Best for** | Complex collaboration | Simple tool usage |
| **Cost** | Higher | Lower |

#### MCP vs Direct Tool Integration
| Aspect | MCP | Direct Integration |
|--------|-----|-------------------|
| **Standardization** | High | Low |
| **Reusability** | Excellent | Limited |
| **Setup Effort** | Higher upfront | Lower upfront |
| **Maintenance** | Easier (centralized) | Harder (scattered) |
| **Best for** | Multiple agents/tools | Single use case |

#### RAG vs Fine-Tuning
| Aspect | RAG | Fine-Tuning |
|--------|-----|-------------|
| **Knowledge Updates** | Real-time | Periodic retraining |
| **Setup Cost** | Moderate | High |
| **Runtime Cost** | Higher (retrieval) | Lower |
| **Flexibility** | High | Low |
| **Accuracy** | Context-dependent | Generally better |

### Intelligence Patterns

#### Learning/Adaptation vs Static Agents
| Aspect | Learning | Static |
|--------|----------|--------|
| **Improvement** | Continuous | None |
| **Complexity** | Very high | Low |
| **Cost** | High (training loops) | Low |
| **Use Case** | Evolving requirements | Fixed requirements |

#### Resource Optimization vs Fixed Allocation
| Aspect | Resource Optimization | Fixed Allocation |
|--------|---------------------|-----------------|
| **Efficiency** | Adapts to load | Constant |
| **Cost** | Lower over time | Higher |
| **Complexity** | High | Low |
| **Predictability** | Lower | Higher |

### Production Patterns

#### Guardrails vs HITL
| Aspect | Guardrails | HITL |
|--------|-----------|------|
| **Automation** | Fully automated | Requires human |
| **Speed** | Fast | Slower |
| **Safety** | Rule-based | Judgment-based |
| **Cost** | Low | High (human time) |
| **Best for** | Known constraints | Complex decisions |

## Pattern Combinations

### Recommended Combos

**High-Performance Search System:**
- Routing + Parallelization + Tool Use + Evals
- Example: E-commerce recommendations

**Reliable Content Generation:**
- Planning + Self-Correction + Reflection + Guardrails
- Example: Legal document drafting

**Enterprise Document Processing:**
- RAG + Multi-Agent + Maker-Checker + Audit Logs
- Example: Contract analysis

**Cost-Optimized System:**
- Resource Optimization + Prioritization + Checkpoint/Rollback
- Example: Batch data processing

**Production-Ready Agent:**
- Any pattern + Evals + Guardrails + Monitoring + Exception Handling
- Example: Customer support automation

### Anti-Patterns (Avoid These Combos)

❌ **Over-Engineering:**
- Multi-Agent + A2A + MCP for simple single-purpose task
- Use: Single agent with tools

❌ **Under-Monitoring:**
- Learning/Adaptation without Evaluation/Monitoring
- Result: Can't measure if learning helps

❌ **Cost Bomb:**
- Reflection + Self-Correction + Planning + Multi-Agent on every request
- Better: Use selectively based on importance

## Selection Decision Tree

```
Start
  ↓
Multiple distinct paths needed?
  YES → Routing
  NO → Continue
  ↓
Tasks can run in parallel?
  YES → Parallelization
  NO → Continue
  ↓
Need external data/actions?
  YES → Tool Use (+ maybe RAG)
  NO → Continue
  ↓
Multiple specialized agents?
  YES → Multi-Agent Collaboration
  NO → Continue
  ↓
Quality critical?
  YES → Reflection + Self-Correction
  NO → Continue
  ↓
Going to production?
  YES → Add: Guardrails + Monitoring + Evals
  NO → You're done!
```

## Performance Characteristics

| Pattern | Latency Impact | Token Usage | Reliability |
|---------|---------------|-------------|-------------|
| Prompt Chaining | +Linear | ++Medium | +++High |
| Routing | +Low | +Low | +++High |
| Parallelization | --Reduces | +++High (parallel) | ++Medium |
| Reflection | +++High | ++++Very High | ++++Very High |
| Tool Use | ++Medium (API calls) | ++Medium | ++Medium |
| Planning | ++++Very High | ++++Very High | ++Medium |
| RAG | +++High (retrieval) | +++High | +++High |
| Multi-Agent | ++++Very High | ++++Very High | ++Medium |
| Guardrails | +Low | +Low | ++++Very High |

## Framework Support

| Pattern | Google ADK | CrewAI | Notes |
|---------|-----------|---------|-------|
| Prompt Chaining | ✅ Native | ✅ Native | SequentialAgent / Sequential Process |
| Routing | ✅ RouterAgent | ⚠️ Manual | ADK has built-in support |
| Parallelization | ✅ ParallelAgent | ✅ Parallel Tasks | Both support well |
| Tool Use | ✅ @Tool | ✅ @tool | Similar syntax |
| Multi-Agent | ⚠️ Custom | ✅ Native | CrewAI designed for this |
| RAG | ✅ Vertex AI RAG | ⚠️ Manual | ADK has managed RAG |
| MCP | ✅ Native | ⚠️ Via adapters | ADK first-class support |

## Resources

- [Pattern Implementations](../README.md)
- [Framework Selection Guide](./framework-selection-guide.md)
- [Deployment Checklist](./deployment-checklist.md)

**Last Updated:** November 2025
