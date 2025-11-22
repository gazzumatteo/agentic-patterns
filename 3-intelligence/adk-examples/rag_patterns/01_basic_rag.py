"""
RAG (Retrieval-Augmented Generation) Pattern - Basic Implementation
Article 2: Orchestration & Collaboration Patterns

RAG enhances LLM responses by retrieving relevant context from a knowledge base
before generating answers. This reduces hallucinations and provides up-to-date information.

Components:
1. Document Loader: Loads and chunks documents
2. Embedding Model: Converts text to vector embeddings
3. Vector Store: Stores and retrieves embeddings
4. Retriever: Finds relevant documents
5. Generator: LLM that generates responses using retrieved context

Use Cases:
- Customer support knowledge bases
- Technical documentation Q&A
- Enterprise search
- Research assistants

Business Value:
- Accurate, grounded responses
- Reduced hallucinations
- Easy knowledge base updates
- Cost-effective vs fine-tuning
"""

import asyncio
import json
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


# ========================================
# DOCUMENT STORE
# ========================================

KNOWLEDGE_BASE = [
    {
        "id": "doc_001",
        "title": "Product Pricing",
        "content": """Our SaaS platform offers three pricing tiers:

        Basic Plan: $29/month
        - Up to 5 users
        - 10GB storage
        - Email support

        Pro Plan: $99/month
        - Up to 25 users
        - 100GB storage
        - Priority support
        - Advanced analytics

        Enterprise Plan: Custom pricing
        - Unlimited users
        - Unlimited storage
        - 24/7 phone support
        - Custom integrations
        - Dedicated account manager""",
        "category": "pricing",
        "last_updated": "2024-11-01"
    },
    {
        "id": "doc_002",
        "title": "API Authentication",
        "content": """API Authentication Guide:

        All API requests require authentication using API keys.

        1. Generate API Key:
           - Go to Settings > API Keys
           - Click 'Generate New Key'
           - Copy your key (shown only once)

        2. Using API Keys:
           - Add header: Authorization: Bearer YOUR_API_KEY
           - Rate limit: 1000 requests/hour

        3. Best Practices:
           - Never commit keys to version control
           - Rotate keys every 90 days
           - Use environment variables""",
        "category": "technical",
        "last_updated": "2024-10-15"
    },
    {
        "id": "doc_003",
        "title": "Data Export",
        "content": """How to Export Your Data:

        We provide multiple export options:

        1. Manual Export:
           - Navigate to Settings > Data Export
           - Select data type (contacts, transactions, reports)
           - Choose format (CSV, JSON, Excel)
           - Click 'Generate Export'
           - Download link sent via email (within 30 minutes)

        2. API Export:
           - Use GET /api/v2/export endpoint
           - Supports pagination for large datasets
           - Returns data in JSON format

        3. Scheduled Exports:
           - Available on Pro and Enterprise plans
           - Schedule daily, weekly, or monthly exports
           - Auto-delivery to email or cloud storage""",
        "category": "features",
        "last_updated": "2024-10-20"
    },
    {
        "id": "doc_004",
        "title": "Troubleshooting Common Issues",
        "content": """Common Issues and Solutions:

        Issue: Login not working
        Solution:
        - Clear browser cache and cookies
        - Try incognito/private mode
        - Reset password via 'Forgot Password'
        - Check for service status at status.company.com

        Issue: Slow performance
        Solution:
        - Check your internet connection
        - Disable browser extensions
        - Try different browser
        - Contact support with browser console logs

        Issue: Data not syncing
        Solution:
        - Verify internet connectivity
        - Check sync status in Settings
        - Force manual sync
        - Wait 5 minutes for auto-sync""",
        "category": "support",
        "last_updated": "2024-11-05"
    },
    {
        "id": "doc_005",
        "title": "Integration Setup",
        "content": """Third-Party Integration Guide:

        We support integrations with popular tools:

        Slack Integration:
        - Install from Slack App Directory
        - Authorize access to your workspace
        - Configure notifications in Settings > Integrations

        Salesforce Integration:
        - Available on Enterprise plan
        - Sync contacts and deals bidirectionally
        - Set up in Settings > Integrations > Salesforce
        - Requires Salesforce admin permissions

        Zapier Integration:
        - Connect with 3000+ apps
        - Use pre-built Zaps or create custom workflows
        - API key required""",
        "category": "integrations",
        "last_updated": "2024-10-28"
    }
]


# ========================================
# SIMPLE EMBEDDING MODEL (Mock)
# ========================================

class SimpleEmbeddingModel:
    """
    Mock embedding model. In production, use:
    - OpenAI embeddings
    - Google Vertex AI embeddings
    - Sentence Transformers
    - Cohere embeddings
    """

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions
        self.vocab = {}  # Word to index mapping

    def _get_word_vector(self, word: str) -> np.ndarray:
        """Get vector for a word (simplified)."""
        # Use hash to get consistent vector for each word
        seed = hash(word) % 10000
        np.random.seed(seed)
        return np.random.randn(self.dimensions)

    def embed_text(self, text: str) -> np.ndarray:
        """Convert text to embedding vector."""
        # Simplified: average word vectors
        words = text.lower().split()
        if not words:
            return np.zeros(self.dimensions)

        vectors = [self._get_word_vector(word) for word in words]
        embedding = np.mean(vectors, axis=0)

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Embed multiple texts."""
        return [self.embed_text(text) for text in texts]


# ========================================
# VECTOR STORE
# ========================================

@dataclass
class Document:
    """Document with embedding."""
    id: str
    content: str
    embedding: np.ndarray
    metadata: Dict[str, Any]


class VectorStore:
    """In-memory vector store for semantic search."""

    def __init__(self, embedding_model: SimpleEmbeddingModel):
        self.embedding_model = embedding_model
        self.documents: List[Document] = []

    def add_documents(self, docs: List[Dict[str, Any]]):
        """Add documents to the store."""
        print(f"Adding {len(docs)} documents to vector store...")

        for doc in docs:
            embedding = self.embedding_model.embed_text(doc["content"])

            document = Document(
                id=doc["id"],
                content=doc["content"],
                embedding=embedding,
                metadata={
                    "title": doc["title"],
                    "category": doc["category"],
                    "last_updated": doc["last_updated"]
                }
            )

            self.documents.append(document)

        print(f"✓ Indexed {len(self.documents)} documents")

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        filter_category: Optional[str] = None
    ) -> List[Tuple[Document, float]]:
        """Find k most similar documents using cosine similarity."""

        # Embed query
        query_embedding = self.embedding_model.embed_text(query)

        # Calculate similarities
        results = []
        for doc in self.documents:
            # Apply filter if specified
            if filter_category and doc.metadata.get("category") != filter_category:
                continue

            # Cosine similarity
            similarity = np.dot(query_embedding, doc.embedding)
            results.append((doc, float(similarity)))

        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:k]


# ========================================
# RAG SYSTEM
# ========================================

class RAGSystem:
    """Complete RAG system combining retrieval and generation."""

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    async def query(
        self,
        question: str,
        k: int = 2,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG:
        1. Retrieve relevant documents
        2. Generate answer using retrieved context
        """

        print(f"\n{'='*80}")
        print(f"Question: {question}")
        print(f"{'='*80}")

        # Step 1: Retrieve relevant documents
        print(f"\nStep 1: Retrieving relevant documents (k={k})...")
        results = self.vector_store.similarity_search(
            query=question,
            k=k,
            filter_category=category
        )

        if not results:
            return {
                "question": question,
                "answer": "I don't have enough information to answer that question.",
                "sources": [],
                "confidence": 0
            }

        # Show retrieved documents
        print("\nRetrieved Documents:")
        for i, (doc, score) in enumerate(results, 1):
            print(f"\n{i}. {doc.metadata['title']} (similarity: {score:.3f})")
            print(f"   Category: {doc.metadata['category']}")
            print(f"   Preview: {doc.content[:100]}...")

        # Step 2: Generate answer (mock LLM response)
        print("\nStep 2: Generating answer from retrieved context...")

        # Build context from retrieved docs
        context = "\n\n".join([
            f"Source {i}: {doc.content}"
            for i, (doc, _) in enumerate(results, 1)
        ])

        # Mock answer generation (in production, use actual LLM)
        answer = self._generate_answer(question, context, results)

        sources = [
            {
                "id": doc.id,
                "title": doc.metadata["title"],
                "category": doc.metadata["category"],
                "relevance_score": score
            }
            for doc, score in results
        ]

        # Calculate confidence based on top similarity score
        confidence = results[0][1] if results else 0

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "confidence": round(confidence * 100, 1),
            "retrieved_docs": len(results)
        }

    def _generate_answer(
        self,
        question: str,
        context: str,
        results: List[Tuple[Document, float]]
    ) -> str:
        """
        Mock answer generation.
        In production, this would call an LLM like:
        - Google Gemini
        - OpenAI GPT
        - Anthropic Claude
        """

        # Simple answer based on retrieved content
        top_doc = results[0][0]

        if "pricing" in question.lower() or "price" in question.lower() or "cost" in question.lower():
            return f"""Based on our pricing documentation, {top_doc.content[:200]}...

For detailed pricing information and to find the best plan for your needs, please visit our pricing page or contact our sales team."""

        elif "api" in question.lower() or "authentication" in question.lower():
            return f"""Here's how to work with our API:

{top_doc.content[:300]}...

For complete API documentation, visit docs.company.com/api"""

        elif "export" in question.lower() or "download" in question.lower():
            return f"""You can export your data using several methods:

{top_doc.content[:250]}...

All exports are secure and comply with data protection regulations."""

        else:
            return f"""Based on our documentation:

{top_doc.content[:200]}...

If you need more specific information, please contact our support team or check our full documentation."""


# ========================================
# DEMO
# ========================================

async def main():
    """Demonstrate RAG system."""

    print("="*80)
    print("RAG (Retrieval-Augmented Generation) DEMO")
    print("="*80)

    # Step 1: Initialize components
    print("\n1. Initializing RAG System...")
    embedding_model = SimpleEmbeddingModel(dimensions=384)
    vector_store = VectorStore(embedding_model)

    # Step 2: Index knowledge base
    print("\n2. Indexing Knowledge Base...")
    vector_store.add_documents(KNOWLEDGE_BASE)

    # Step 3: Create RAG system
    rag = RAGSystem(vector_store)

    # Step 4: Ask questions
    questions = [
        "How much does the Pro plan cost?",
        "How do I authenticate with the API?",
        "How can I export my data?",
        "What should I do if login is not working?",
    ]

    results = []
    for question in questions:
        result = await rag.query(question, k=2)
        results.append(result)

        print(f"\nAnswer: {result['answer']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Sources: {len(result['sources'])}")

    # Summary
    print(f"\n{'='*80}")
    print("DEMO SUMMARY")
    print(f"{'='*80}")
    print(f"Questions Answered: {len(results)}")
    print(f"Average Confidence: {sum(r['confidence'] for r in results) / len(results):.1f}%")
    print(f"Documents in Index: {len(vector_store.documents)}")


if __name__ == "__main__":
    asyncio.run(main())
