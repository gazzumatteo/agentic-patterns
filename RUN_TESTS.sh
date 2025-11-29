#!/bin/bash
# Comprehensive test runner with proper environment setup

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                Running Comprehensive Tests with All Fixes                 ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Configuration:"
echo "  - TEST_MODE: enabled (auto-approve prompts)"
echo "  - DEMO_MODE: enabled (reduced iterations)"
echo "  - Rate limiting: 3s delay (ADK), 2s delay (CrewAI)"
echo "  - Timeouts: 180-400s based on complexity"
echo ""
echo "Estimated time: 30-45 minutes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Ensure we're in the right directory
cd /Users/matteo/GitRepositories/Gazzumatteo/agentic-patterns

# Run tests
uv run python test_runner.py 2>&1 | tee test_output_v2.log

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                          Tests Complete!                                  ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Results available in:"
echo "  - TEST_REPORT.md (formatted report)"
echo "  - test_results.json (machine-readable)"
echo "  - test_output_v2.log (full execution log)"
echo ""
