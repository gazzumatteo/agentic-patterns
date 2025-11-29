# Comprehensive Test Report - All Agentic Patterns

**Generated:** 2025-11-20 19:07:08

## Overall Summary

| Framework | Total | Passed | Failed | Success Rate |
|-----------|-------|--------|--------|--------------|
| Google ADK | 36 | 28 | 8 | 77.8% |
| CrewAI | 35 | 27 | 8 | 77.1% |
| **Total** | **71** | **55** | **16** | **77.5%** |

---

## 1-foundational

### Summary

| Framework | Total | Passed | Failed | Success Rate |
|-----------|-------|--------|--------|--------------|
| Google ADK | 9 | 9 | 0 | 100.0% |
| CrewAI | 8 | 8 | 0 | 100.0% |

### ADK Examples

#### 01_simple_agent.py - ✅ PASS

**Path:** `1-foundational/adk-examples/01_simple_agent.py`

---

#### 02_memory_augmented_agent.py - ✅ PASS

**Path:** `1-foundational/adk-examples/02_memory_augmented_agent.py`

---

#### 03_tool_using_agent.py - ✅ PASS

**Path:** `1-foundational/adk-examples/03_tool_using_agent.py`

---

#### 04_planning.py - ✅ PASS

**Path:** `1-foundational/adk-examples/04_planning.py`

---

#### 05_reflection_generator_critic.py - ✅ PASS

**Path:** `1-foundational/adk-examples/05_reflection_generator_critic.py`

---

#### 06_loop_cyclic.py - ✅ PASS

**Path:** `1-foundational/adk-examples/06_loop_cyclic.py`

---

#### 07_react.py - ✅ PASS

**Path:** `1-foundational/adk-examples/07_react.py`

---

#### 08_chain_of_thought.py - ✅ PASS

**Path:** `1-foundational/adk-examples/08_chain_of_thought.py`

---

#### 09_evals.py - ✅ PASS

**Path:** `1-foundational/adk-examples/09_evals.py`

---


### CrewAI Examples

#### 01_simple_agent.py - ✅ PASS

**Path:** `1-foundational/crewai-examples/01_simple_agent.py`

---

#### 02_memory_augmented_agent.py - ✅ PASS

**Path:** `1-foundational/crewai-examples/02_memory_augmented_agent.py`

---

#### 03_tool_using_agent.py - ✅ PASS

**Path:** `1-foundational/crewai-examples/03_tool_using_agent.py`

---

#### 04_planning.py - ✅ PASS

**Path:** `1-foundational/crewai-examples/04_planning.py`

---

#### 05_reflection_generator_critic.py - ✅ PASS

**Path:** `1-foundational/crewai-examples/05_reflection_generator_critic.py`

---

#### 06_loop_cyclic.py - ✅ PASS

**Path:** `1-foundational/crewai-examples/06_loop_cyclic.py`

---

#### 07_react.py - ✅ PASS

**Path:** `1-foundational/crewai-examples/07_react.py`

---

#### 08_chain_of_thought.py - ✅ PASS

**Path:** `1-foundational/crewai-examples/08_chain_of_thought.py`

---

## 2-orchestration

### Summary

| Framework | Total | Passed | Failed | Success Rate |
|-----------|-------|--------|--------|--------------|
| Google ADK | 10 | 10 | 0 | 100.0% |
| CrewAI | 10 | 4 | 6 | 40.0% |

### ADK Examples

#### 01_sequential_orchestration.py - ✅ PASS

**Path:** `2-orchestration/adk-examples/01_sequential_orchestration.py`

---

#### 02_parallel_orchestration.py - ✅ PASS

**Path:** `2-orchestration/adk-examples/02_parallel_orchestration.py`

---

#### 03_supervisor_pattern.py - ✅ PASS

**Path:** `2-orchestration/adk-examples/03_supervisor_pattern.py`

---

#### 04_hierarchical_pattern.py - ✅ PASS

**Path:** `2-orchestration/adk-examples/04_hierarchical_pattern.py`

---

#### 05_competitive_pattern.py - ✅ PASS

**Path:** `2-orchestration/adk-examples/05_competitive_pattern.py`

---

#### 06_network_swarm_pattern.py - ✅ PASS

**Path:** `2-orchestration/adk-examples/06_network_swarm_pattern.py`

---

#### 07_handoff_orchestration.py - ✅ PASS

**Path:** `2-orchestration/adk-examples/07_handoff_orchestration.py`

---

#### 08_blackboard_pattern.py - ✅ PASS

**Path:** `2-orchestration/adk-examples/08_blackboard_pattern.py`

---

#### 09_magentic_orchestration.py - ✅ PASS

**Path:** `2-orchestration/adk-examples/09_magentic_orchestration.py`

---

#### 10_market_based_pattern.py - ✅ PASS

**Path:** `2-orchestration/adk-examples/10_market_based_pattern.py`

---


### CrewAI Examples

#### 01_sequential_orchestration.py - ✅ PASS

**Path:** `2-orchestration/crewai-examples/01_sequential_orchestration.py`

---

#### 02_parallel_orchestration.py - ✅ PASS

**Path:** `2-orchestration/crewai-examples/02_parallel_orchestration.py`

---

#### 03_supervisor_pattern.py - ❌ FAIL

**Path:** `2-orchestration/crewai-examples/03_supervisor_pattern.py`

**Error:**
```
Timeout after 300 seconds
```

---

#### 04_hierarchical_pattern.py - ❌ FAIL

**Path:** `2-orchestration/crewai-examples/04_hierarchical_pattern.py`

**Error:**
```
Timeout after 300 seconds
```

---

#### 05_competitive_pattern.py - ❌ FAIL

**Path:** `2-orchestration/crewai-examples/05_competitive_pattern.py`

**Error:**
```
Timeout after 300 seconds
```

---

#### 06_network_swarm_pattern.py - ❌ FAIL

**Path:** `2-orchestration/crewai-examples/06_network_swarm_pattern.py`

**Error:**
```
ERROR:root:Failed to connect to OpenAI API: Connection error.
```

---

#### 07_handoff_orchestration.py - ❌ FAIL

**Path:** `2-orchestration/crewai-examples/07_handoff_orchestration.py`

**Error:**
```
ERROR:root:Failed to connect to OpenAI API: Connection error.
```

---

#### 08_blackboard_pattern.py - ❌ FAIL

**Path:** `2-orchestration/crewai-examples/08_blackboard_pattern.py`

**Error:**
```
ERROR:root:Failed to connect to OpenAI API: Connection error.
```

---

#### 09_magentic_orchestration.py - ✅ PASS

**Path:** `2-orchestration/crewai-examples/09_magentic_orchestration.py`

---

#### 10_market_based_pattern.py - ✅ PASS

**Path:** `2-orchestration/crewai-examples/10_market_based_pattern.py`

---

## 3-intelligence

### Summary

| Framework | Total | Passed | Failed | Success Rate |
|-----------|-------|--------|--------|--------------|
| Google ADK | 11 | 9 | 2 | 81.8% |
| CrewAI | 11 | 11 | 0 | 100.0% |

### ADK Examples

#### 01_rag.py - ✅ PASS

**Path:** `3-intelligence/adk-examples/01_rag.py`

---

#### 02_agentic_rag.py - ✅ PASS

**Path:** `3-intelligence/adk-examples/02_agentic_rag.py`

---

#### 03_mcp_tools.py - ✅ PASS

**Path:** `3-intelligence/adk-examples/03_mcp_tools.py`

---

#### 04_a2a_protocol.py - ✅ PASS

**Path:** `3-intelligence/adk-examples/04_a2a_protocol.py`

---

#### 05_guardrails_safety.py - ❌ FAIL

**Path:** `3-intelligence/adk-examples/05_guardrails_safety.py`

**Error:**
```
Traceback (most recent call last):
  File "/Users/matteo/GitRepositories/Gazzumatteo/agentic-patterns/3-intelligence/adk-examples/05_guardrails_safety.py", line 382, in <module>
    asyncio.run(demonstrate_guardrails_pattern())
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/base_events.py", line 686, in run_until_complete
```

---

#### 06_exception_handling.py - ✅ PASS

**Path:** `3-intelligence/adk-examples/06_exception_handling.py`

---

#### 07_hitl.py - ❌ FAIL

**Path:** `3-intelligence/adk-examples/07_hitl.py`

**Error:**
```
Timeout after 180 seconds
```

---

#### 08_resource_optimization.py - ✅ PASS

**Path:** `3-intelligence/adk-examples/08_resource_optimization.py`

---

#### 09_prioritization.py - ✅ PASS

**Path:** `3-intelligence/adk-examples/09_prioritization.py`

---

#### 10_goal_monitoring.py - ✅ PASS

**Path:** `3-intelligence/adk-examples/10_goal_monitoring.py`

---

#### 11_checkpoint_rollback.py - ✅ PASS

**Path:** `3-intelligence/adk-examples/11_checkpoint_rollback.py`

---


### CrewAI Examples

#### 01_rag.py - ✅ PASS

**Path:** `3-intelligence/crewai-examples/01_rag.py`

---

#### 02_agentic_rag.py - ✅ PASS

**Path:** `3-intelligence/crewai-examples/02_agentic_rag.py`

---

#### 03_mcp_tools.py - ✅ PASS

**Path:** `3-intelligence/crewai-examples/03_mcp_tools.py`

---

#### 04_a2a_protocol.py - ✅ PASS

**Path:** `3-intelligence/crewai-examples/04_a2a_protocol.py`

---

#### 05_guardrails_safety.py - ✅ PASS

**Path:** `3-intelligence/crewai-examples/05_guardrails_safety.py`

---

#### 06_exception_handling.py - ✅ PASS

**Path:** `3-intelligence/crewai-examples/06_exception_handling.py`

---

#### 07_hitl.py - ✅ PASS

**Path:** `3-intelligence/crewai-examples/07_hitl.py`

---

#### 08_resource_optimization.py - ✅ PASS

**Path:** `3-intelligence/crewai-examples/08_resource_optimization.py`

---

#### 09_prioritization.py - ✅ PASS

**Path:** `3-intelligence/crewai-examples/09_prioritization.py`

---

#### 10_goal_monitoring.py - ✅ PASS

**Path:** `3-intelligence/crewai-examples/10_goal_monitoring.py`

---

#### 11_checkpoint_rollback.py - ✅ PASS

**Path:** `3-intelligence/crewai-examples/11_checkpoint_rollback.py`

---

## 4-production

### Summary

| Framework | Total | Passed | Failed | Success Rate |
|-----------|-------|--------|--------|--------------|
| Google ADK | 6 | 0 | 6 | 0.0% |
| CrewAI | 6 | 4 | 2 | 66.7% |

### ADK Examples

#### 01_learning_adaptation.py - ❌ FAIL

**Path:** `4-production/adk-examples/01_learning_adaptation.py`

**Error:**
```
Traceback (most recent call last):
  File "/Users/matteo/GitRepositories/Gazzumatteo/agentic-patterns/4-production/adk-examples/01_learning_adaptation.py", line 436, in <module>
    asyncio.run(main())
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/base_events.py", line 686, in run_until_complete
```

---

#### 02_exploration_discovery.py - ❌ FAIL

**Path:** `4-production/adk-examples/02_exploration_discovery.py`

**Error:**
```
Traceback (most recent call last):
  File "/Users/matteo/GitRepositories/Gazzumatteo/agentic-patterns/4-production/adk-examples/02_exploration_discovery.py", line 506, in <module>
    asyncio.run(main())
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/base_events.py", line 686, in run_until_complete
```

---

#### 03_evolutionary_curriculum.py - ❌ FAIL

**Path:** `4-production/adk-examples/03_evolutionary_curriculum.py`

**Error:**
```
Traceback (most recent call last):
  File "/Users/matteo/GitRepositories/Gazzumatteo/agentic-patterns/4-production/adk-examples/03_evolutionary_curriculum.py", line 427, in <module>
    asyncio.run(main())
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/base_events.py", line 686, in run_until_complete
```

---

#### 04_modular_agent.py - ❌ FAIL

**Path:** `4-production/adk-examples/04_modular_agent.py`

**Error:**
```
Traceback (most recent call last):
  File "/Users/matteo/GitRepositories/Gazzumatteo/agentic-patterns/4-production/adk-examples/04_modular_agent.py", line 357, in <module>
    asyncio.run(main())
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/base_events.py", line 686, in run_until_complete
```

---

#### 05_maker_checker.py - ❌ FAIL

**Path:** `4-production/adk-examples/05_maker_checker.py`

**Error:**
```
Traceback (most recent call last):
  File "/Users/matteo/GitRepositories/Gazzumatteo/agentic-patterns/4-production/adk-examples/05_maker_checker.py", line 262, in <module>
    asyncio.run(main())
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/base_events.py", line 686, in run_until_complete
```

---

#### 06_abm.py - ❌ FAIL

**Path:** `4-production/adk-examples/06_abm.py`

**Error:**
```
Traceback (most recent call last):
  File "/Users/matteo/GitRepositories/Gazzumatteo/agentic-patterns/4-production/adk-examples/06_abm.py", line 351, in <module>
    asyncio.run(main())
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/matteo/miniconda3/lib/python3.12/asyncio/base_events.py", line 686, in run_until_complete
```

---


### CrewAI Examples

#### 01_learning_adaptation.py - ✅ PASS

**Path:** `4-production/crewai-examples/01_learning_adaptation.py`

---

#### 02_exploration_discovery.py - ❌ FAIL

**Path:** `4-production/crewai-examples/02_exploration_discovery.py`

**Error:**
```
Timeout after 400 seconds
```

---

#### 03_evolutionary_curriculum.py - ❌ FAIL

**Path:** `4-production/crewai-examples/03_evolutionary_curriculum.py`

**Error:**
```
Timeout after 400 seconds
```

---

#### 04_modular_agent.py - ✅ PASS

**Path:** `4-production/crewai-examples/04_modular_agent.py`

---

#### 05_maker_checker.py - ✅ PASS

**Path:** `4-production/crewai-examples/05_maker_checker.py`

---

#### 06_abm.py - ✅ PASS

**Path:** `4-production/crewai-examples/06_abm.py`

---


## All Issues Found

1. **[2-orchestration] 03_supervisor_pattern.py**: Timeout after 300 seconds...
2. **[2-orchestration] 04_hierarchical_pattern.py**: Timeout after 300 seconds...
3. **[2-orchestration] 05_competitive_pattern.py**: Timeout after 300 seconds...
4. **[2-orchestration] 06_network_swarm_pattern.py**: ERROR:root:Failed to connect to OpenAI API: Connection error....
5. **[2-orchestration] 07_handoff_orchestration.py**: ERROR:root:Failed to connect to OpenAI API: Connection error....
6. **[2-orchestration] 08_blackboard_pattern.py**: ERROR:root:Failed to connect to OpenAI API: Connection error....
7. **[3-intelligence] 05_guardrails_safety.py**: Traceback (most recent call last):
  File "/Users/matteo/GitRepositories/Gazzumatteo/agentic-patterns/3-intelligence/adk-examples/05_guardrails_safety.py", line 382, in <module>
    asyncio.run(demons...
8. **[3-intelligence] 07_hitl.py**: Timeout after 180 seconds...
9. **[4-production] 01_learning_adaptation.py**: Traceback (most recent call last):
  File "/Users/matteo/GitRepositories/Gazzumatteo/agentic-patterns/4-production/adk-examples/01_learning_adaptation.py", line 436, in <module>
    asyncio.run(main()...
10. **[4-production] 02_exploration_discovery.py**: Traceback (most recent call last):
  File "/Users/matteo/GitRepositories/Gazzumatteo/agentic-patterns/4-production/adk-examples/02_exploration_discovery.py", line 506, in <module>
    asyncio.run(main...
11. **[4-production] 03_evolutionary_curriculum.py**: Traceback (most recent call last):
  File "/Users/matteo/GitRepositories/Gazzumatteo/agentic-patterns/4-production/adk-examples/03_evolutionary_curriculum.py", line 427, in <module>
    asyncio.run(ma...
12. **[4-production] 04_modular_agent.py**: Traceback (most recent call last):
  File "/Users/matteo/GitRepositories/Gazzumatteo/agentic-patterns/4-production/adk-examples/04_modular_agent.py", line 357, in <module>
    asyncio.run(main())
  Fi...
13. **[4-production] 05_maker_checker.py**: Traceback (most recent call last):
  File "/Users/matteo/GitRepositories/Gazzumatteo/agentic-patterns/4-production/adk-examples/05_maker_checker.py", line 262, in <module>
    asyncio.run(main())
  Fi...
14. **[4-production] 06_abm.py**: Traceback (most recent call last):
  File "/Users/matteo/GitRepositories/Gazzumatteo/agentic-patterns/4-production/adk-examples/06_abm.py", line 351, in <module>
    asyncio.run(main())
  File "/Users...
15. **[4-production] 02_exploration_discovery.py**: Timeout after 400 seconds...
16. **[4-production] 03_evolutionary_curriculum.py**: Timeout after 400 seconds...
