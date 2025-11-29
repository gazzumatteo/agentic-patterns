# Agent Card: [Agent Name]

## Overview
**Agent ID:** [Unique Identifier]
**Version:** [Version Number]
**Owner:** [Team/Person]
**Last Updated:** [Date]
**Status:** [Development/Staging/Production]

## Purpose
[Brief description of what this agent does and why it exists]

## Capabilities
- **Primary Function:** [Main task the agent performs]
- **Input Types:** [What data/formats the agent accepts]
- **Output Types:** [What the agent produces]
- **Tools/APIs Used:** [List of external tools or APIs]
- **Model:** [LLM model used, e.g., gemini-2.5-flash]

## Performance Metrics
- **Accuracy:** [Target/Actual accuracy rate]
- **Latency:** [Average response time]
- **Throughput:** [Requests per minute/hour]
- **Success Rate:** [Percentage of successful completions]
- **Cost:** [Per-request cost estimate]

## Safety & Compliance
- **Data Classification:** [Public/Internal/Confidential/Restricted]
- **PII Handling:** [Yes/No - If yes, describe safeguards]
- **Regulatory Requirements:** [GDPR, HIPAA, SOC2, etc.]
- **Guardrails:** [List of implemented safety measures]
- **Human Oversight:** [HITL requirements, escalation criteria]

## Testing & Validation
- **Test Coverage:** [Percentage]
- **Test Scenarios:** [Number of test cases]
- **Edge Cases:** [List of known edge cases]
- **Failure Modes:** [How agent behaves when it fails]
- **Rollback Plan:** [Steps to revert to previous version]

## Dependencies
- **Upstream Systems:** [Systems this agent depends on]
- **Downstream Systems:** [Systems that depend on this agent]
- **External APIs:** [Third-party services]
- **Data Sources:** [Databases, vector stores, knowledge bases]

## Monitoring & Observability
- **Metrics Tracked:** [List of monitored metrics]
- **Logging Level:** [DEBUG/INFO/WARN/ERROR]
- **Alert Conditions:** [When to trigger alerts]
- **Dashboard:** [Link to monitoring dashboard]
- **On-Call:** [Escalation contact]

## Known Limitations
1. [Limitation 1]
2. [Limitation 2]
3. [Limitation 3]

## Training Data
- **Dataset:** [Name/description of training data]
- **Last Trained:** [Date]
- **Training Method:** [Fine-tuning/RAG/Prompt engineering]
- **Bias Mitigation:** [Steps taken to reduce bias]

## Example Usage

### Input Example
```json
{
  "query": "Example input",
  "context": "Additional context"
}
```

### Output Example
```json
{
  "result": "Example output",
  "confidence": 0.95,
  "metadata": {}
}
```

## Change Log
| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | YYYY-MM-DD | Initial release | [Name] |
| 1.1.0 | YYYY-MM-DD | Added feature X | [Name] |

## Approval
- **Technical Review:** [Name, Date]
- **Security Review:** [Name, Date]
- **Compliance Review:** [Name, Date]
- **Production Approval:** [Name, Date]

## References
- [Architecture Document]
- [API Documentation]
- [Runbook]
- [Incident Response Plan]
