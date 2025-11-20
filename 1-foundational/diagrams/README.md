# Foundational Patterns - Mermaid Diagrams

Visual representations of all 9 foundational agentic design patterns with architectural flows, decision points, and data flows.

## Diagram Files

### Individual Pattern Diagrams

1. **[01_prompt_chaining.mermaid](./01_prompt_chaining.mermaid)** - Sequential task decomposition
   - Customer onboarding flow example
   - State persistence across agents
   - ADK: SequentialAgent | CrewAI: Process.sequential

2. **[02_routing.mermaid](./02_routing.mermaid)** - Dynamic workflow selection
   - Request classification system
   - Supervisor pattern with specialists
   - ADK: LlmAgent routing | CrewAI: Process.hierarchical

3. **[03_parallelization.mermaid](./03_parallelization.mermaid)** - Concurrent execution
   - Multi-source market research
   - Fan-out/fan-in pattern
   - ADK: ParallelAgent | CrewAI: Context-based parallelization

4. **[04_reflection.mermaid](./04_reflection.mermaid)** - Iterative refinement
   - Generator-Critic loop
   - Quality threshold-based exit
   - ADK: LoopAgent | CrewAI: Dynamic task creation

5. **[05_tool_use.mermaid](./05_tool_use.mermaid)** - External integration
   - Research agent with multiple tools
   - ReAct pattern (Reason-Act-Observe)
   - ADK: FunctionTools | CrewAI: @tool decorator

6. **[06_planning.mermaid](./06_planning.mermaid)** - Multi-step strategy
   - Project management assistant
   - Task decomposition and resource allocation
   - ADK: Sequential planning | CrewAI: planning=True

7. **[07_multi_modal.mermaid](./07_multi_modal.mermaid)** - Cross-format processing
   - Document analysis (text + images + tables)
   - Modal-specific processors with synthesis
   - ADK: Gemini 2.0 multimodal | CrewAI: Specialized agents

8. **[08_self_correction.mermaid](./08_self_correction.mermaid)** - Error recovery
   - Code generation with automated testing
   - Test-analyze-fix loop
   - ADK: LoopAgent validation | CrewAI: Generator-validator-fixer

9. **[09_evals.mermaid](./09_evals.mermaid)** - Performance measurement
   - Model comparison and benchmarking
   - Multi-metric evaluation
   - ADK: Custom eval framework | CrewAI: Agent performance testing

### Consolidated Diagram

- **[all_patterns.mermaid](./all_patterns.mermaid)** - All 9 patterns in one file
  - Complete pattern collection
  - Comparison matrix
  - Framework support overview
  - Color legend and conventions

## Viewing the Diagrams

### Online Viewers

1. **Mermaid Live Editor**: https://mermaid.live
   - Paste diagram code
   - Export as SVG/PNG
   - Interactive editing

2. **GitHub**: Renders Mermaid natively in Markdown files
   - View directly in repository
   - No additional tools needed

3. **VS Code**: Install Mermaid extension
   - Preview in editor
   - Export capabilities

### Local Rendering

```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Convert to PNG
mmdc -i 01_prompt_chaining.mermaid -o 01_prompt_chaining.png

# Convert to SVG (recommended for articles)
mmdc -i 01_prompt_chaining.mermaid -o 01_prompt_chaining.svg

# Batch convert all diagrams
for file in *.mermaid; do
  mmdc -i "$file" -o "${file%.mermaid}.svg"
done
```

### Embedding in Documentation

**Markdown**:
```markdown
![Pattern Name](./diagrams/01_prompt_chaining.svg)
```

**HTML**:
```html
<img src="./diagrams/01_prompt_chaining.svg" alt="Prompt Chaining Pattern">
```

**Medium Articles**:
1. Export diagram as PNG/SVG
2. Upload as image
3. Add caption with pattern name

## Diagram Conventions

### Node Types

- **Rounded Rectangle** `([...])`: Input/Output, Start/End
- **Rectangle** `[...]`: Processing agents/components
- **Diamond** `{...}`: Decision points, conditionals
- **Cylinder** `[(...)]`: Data stores, state, context
- **Dashed** `-.->`: Metadata, optional flows

### Color Coding

Following Google's Material Design colors:

- **Blue (#4285f4)**: Main agents, core logic components
- **Green (#34a853)**: Success paths, validation, data processing
- **Yellow (#fbbc04)**: Routing, orchestration, decisions
- **Red (#ea4335)**: Critics, validators, error handling
- **Gray (#9aa0a6)**: Supporting components, fallbacks

### Arrow Types

- **Solid** `-->`: Primary data/control flow
- **Dotted** `-.->`: State reads/writes, metadata
- **Labeled**: Flow conditions, data keys

## Pattern Selection Guide

Use this quick reference to choose the right pattern:

| Need | Pattern | Diagram |
|------|---------|---------|
| Sequential steps with dependencies | Prompt Chaining | #01 |
| Route to different handlers | Routing | #02 |
| Speed up independent tasks | Parallelization | #03 |
| Improve output quality | Reflection | #04 |
| Access external systems | Tool Use | #05 |
| Break down complex goals | Planning | #06 |
| Process mixed content types | Multi-Modal | #07 |
| Auto-fix errors | Self-Correction | #08 |
| Compare models/agents | Evals | #09 |

## Combining Patterns

Most production systems combine multiple patterns:

- **Routing → Prompt Chaining**: Route to different sequential workflows
- **Planning → Parallelization**: Execute plan steps in parallel
- **Tool Use → Reflection**: Use tools, then validate/improve results
- **Self-Correction → Evals**: Test corrections, measure improvement

See `all_patterns.mermaid` for the complete pattern ecosystem.

## Customization

To create custom diagrams:

1. Copy a template diagram
2. Modify node names and flows
3. Adjust colors using `style` directives
4. Add your specific business logic
5. Test in Mermaid Live Editor
6. Export and integrate

## Contributing

To improve these diagrams:

1. Fork the repository
2. Edit `.mermaid` files
3. Test rendering in multiple viewers
4. Submit pull request with:
   - Clear description of changes
   - Screenshots of before/after
   - Rationale for modifications

## Resources

- **Mermaid Documentation**: https://mermaid.js.org/
- **Google ADK Docs**: https://github.com/google/adk-docs
- **CrewAI Docs**: https://docs.crewai.com/
- **Pattern Implementations**: See `../adk-examples/` and `../crewai-examples/`

---

**Last Updated**: November 2024
**Diagram Format**: Mermaid 10.6+
**Maintained By**: Matteo Gazzurelli
