"""
RAG (Retrieval-Augmented Generation) with CrewAI
Article 2: Orchestration & Collaboration Patterns

This example shows how to implement RAG patterns with CrewAI agents.
Agents can retrieve relevant context before generating responses.

Use Case: Technical Support System
- Retriever Agent: Finds relevant documentation
- Answerer Agent: Generates responses using retrieved context
- Validator Agent: Ensures answer quality

Business Value:
- Accurate, grounded technical support
- Reduced hallucinations
- Scalable knowledge base
"""

import json
import numpy as np
from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool


# ========================================
# MOCK KNOWLEDGE BASE
# ========================================

DOCS = {
    "api_auth": "API Authentication: Use Bearer tokens in Authorization header. Get token from Settings > API Keys. Rate limit: 1000 req/hour.",
    "pricing_basic": "Basic Plan: $29/month for 5 users, 10GB storage, email support",
    "pricing_pro": "Pro Plan: $99/month for 25 users, 100GB storage, priority support, analytics",
    "data_export": "Data Export: Go to Settings > Data Export, select format (CSV/JSON), receive email link within 30 min",
    "troubleshoot_login": "Login issues: Clear cache, try incognito mode, reset password, check status.company.com",
    "integration_slack": "Slack Integration: Install from Slack directory, authorize workspace, configure in Settings > Integrations",
}

# Simple mock embeddings (in production use real embedding model)
DOC_EMBEDDINGS = {
    doc_id: np.random.randn(128) for doc_id in DOCS.keys()
}


# ========================================
# RAG TOOLS
# ========================================

@tool("Search Documentation")
def search_documentation(query: str, top_k: str = "2") -> str:
    """Search documentation for relevant information. Returns top_k most relevant docs."""

    # Simple keyword matching (in production, use vector similarity)
    query_lower = query.lower()
    scores = {}

    for doc_id, content in DOCS.items():
        score = sum(1 for word in query_lower.split() if word in content.lower())
        if score > 0:
            scores[doc_id] = score

    # Sort and get top k
    k = int(top_k)
    top_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]

    results = [
        {
            "doc_id": doc_id,
            "content": DOCS[doc_id],
            "relevance_score": score
        }
        for doc_id, score in top_docs
    ]

    return json.dumps(results, indent=2)


@tool("Get Document By ID")
def get_document_by_id(doc_id: str) -> str:
    """Retrieve a specific document by its ID."""
    content = DOCS.get(doc_id, "Document not found")
    return json.dumps({"doc_id": doc_id, "content": content})


@tool("Verify Answer Quality")
def verify_answer_quality(answer: str, sources: str) -> str:
    """Verify that answer is grounded in the provided sources."""

    # Simple check: answer should contain information from sources
    sources_text = sources.lower()
    answer_lower = answer.lower()

    # Check if key facts from sources appear in answer
    grounded = any(word in answer_lower for word in sources_text.split()[:10])

    result = {
        "is_grounded": grounded,
        "confidence": 0.9 if grounded else 0.5,
        "recommendation": "Answer appears grounded in sources" if grounded else "Answer may contain unsupported claims"
    }

    return json.dumps(result, indent=2)


# ========================================
# AGENTS
# ========================================

# Retriever Agent - finds relevant docs
retriever_agent = Agent(
    role="Documentation Retriever",
    goal="Find the most relevant documentation for user questions",
    backstory="""You are an expert at searching through technical documentation
    to find relevant information. You understand semantic meaning and can identify
    the best sources for any question.""",
    verbose=True,
    allow_delegation=False,
    tools=[search_documentation, get_document_by_id]
)

# Answer Agent - generates responses using retrieved context
answer_agent = Agent(
    role="Technical Support Specialist",
    goal="Provide accurate answers using retrieved documentation",
    backstory="""You are a senior technical support specialist. You always base
    your answers on official documentation and never make up information. You cite
    sources and provide clear, actionable guidance.""",
    verbose=True,
    allow_delegation=False
)

# Validator Agent - ensures answer quality
validator_agent = Agent(
    role="Quality Assurance Specialist",
    goal="Verify answers are grounded in documentation and accurate",
    backstory="""You review technical support answers to ensure they are accurate,
    grounded in official documentation, and helpful. You catch unsupported claims
    and hallucinations.""",
    verbose=True,
    allow_delegation=False,
    tools=[verify_answer_quality]
)


# ========================================
# RAG WORKFLOW
# ========================================

def answer_question_with_rag(question: str) -> Dict[str, Any]:
    """Answer a question using RAG pattern with CrewAI."""

    print(f"\n{'='*80}")
    print(f"Question: {question}")
    print(f"{'='*80}\n")

    # Task 1: Retrieve relevant documentation
    retrieve_task = Task(
        description=f"""Find relevant documentation for this question:

"{question}"

Use the search_documentation tool to find the top 2 most relevant documents.
Return the retrieved documents with their IDs and content.""",
        agent=retriever_agent,
        expected_output="List of relevant documents with IDs and content"
    )

    # Task 2: Generate answer using retrieved context
    answer_task = Task(
        description=f"""Based on the retrieved documentation, answer this question:

"{question}"

Important:
- Only use information from the retrieved documents
- Do not make up or assume information
- If the docs don't fully answer the question, say so
- Cite which documents you used
- Be clear and concise

Provide a helpful, accurate answer.""",
        agent=answer_agent,
        expected_output="Clear answer based on retrieved documentation with citations",
        context=[retrieve_task]
    )

    # Task 3: Validate answer quality
    validate_task = Task(
        description="""Verify the answer quality:

1. Check if the answer is grounded in the retrieved documentation
2. Ensure no unsupported claims were made
3. Verify the answer is helpful and accurate
4. Use verify_answer_quality tool

Provide validation results with confidence score.""",
        agent=validator_agent,
        expected_output="Validation report with confidence score and any issues found",
        context=[retrieve_task, answer_task]
    )

    # Create and run crew
    crew = Crew(
        agents=[retriever_agent, answer_agent, validator_agent],
        tasks=[retrieve_task, answer_task, validate_task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()

    return {
        "question": question,
        "result": str(result)
    }


# ========================================
# DEMO
# ========================================

def main():
    """Demonstrate RAG pattern with CrewAI."""

    print("="*80)
    print("RAG PATTERN WITH CREWAI")
    print("="*80)

    questions = [
        "How do I authenticate with your API?",
        "What does the Pro plan include?",
        "How can I export my data?",
    ]

    for question in questions:
        result = answer_question_with_rag(question)

        print(f"\n{'='*80}")
        print("RESULT")
        print(f"{'='*80}")
        print(f"Question: {result['question']}")
        print(f"\nFull Output:\n{result['result']}")

    print(f"\n{'='*80}")
    print("DEMO COMPLETE")
    print(f"{'='*80}")
    print("\nRAG Pattern Benefits:")
    print("✓ Answers grounded in documentation")
    print("✓ Reduced hallucinations")
    print("✓ Quality validation built-in")
    print("✓ Easy to update knowledge base")


if __name__ == "__main__":
    main()
