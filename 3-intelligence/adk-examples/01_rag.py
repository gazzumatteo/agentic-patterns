"""
Pattern 19: Knowledge Retrieval (RAG) - Google ADK Implementation

Grounds agent responses in verified data sources. Prevents hallucinations by anchoring
outputs to your knowledge base.

Business Example: GlobalLegal (2,000 attorneys)
- 10M documents indexed in vector database
- Research time: 8 hours → 30 minutes per case
- Accuracy: 94% (vs 78% keyword search)
- Annual value: $12M additional revenue

Mermaid Diagram Reference: diagrams/pattern-19-rag.mmd
Medium Article: Part 3 - Governance and Reliability Patterns
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai.types import GenerateContentConfig
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Load environment variables
load_dotenv()

console = Console()


@dataclass
class LegalDocument:
    """Represents a legal document in the knowledge base."""
    doc_id: str
    title: str
    content: str
    case_year: int
    jurisdiction: str
    precedent_value: float


@dataclass
class RetrievalResult:
    """RAG retrieval result with citation."""
    document: LegalDocument
    relevance_score: float
    citation: str
    excerpt: str


class VectorDatabase:
    """Vector database for legal document storage and retrieval."""

    def __init__(self, collection_name: str = "legal_precedents"):
        """Initialize ChromaDB vector store."""
        self.client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        # Initialize embedding model
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

        console.print(f"[green]✓[/green] Vector database initialized: {collection_name}")

    def index_documents(self, documents: List[LegalDocument]) -> None:
        """Index legal documents into vector database."""
        console.print(f"\n[yellow]Indexing {len(documents)} documents...[/yellow]")

        for doc in documents:
            # Generate embedding
            embedding = self.embedder.encode(doc.content).tolist()

            # Store in ChromaDB
            self.collection.add(
                ids=[doc.doc_id],
                embeddings=[embedding],
                documents=[doc.content],
                metadatas=[{
                    "title": doc.title,
                    "case_year": doc.case_year,
                    "jurisdiction": doc.jurisdiction,
                    "precedent_value": doc.precedent_value
                }]
            )

        console.print(f"[green]✓[/green] Indexed {len(documents)} documents")

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_relevance: float = 0.7
    ) -> List[RetrievalResult]:
        """Search for relevant documents."""
        # Generate query embedding
        query_embedding = self.embedder.encode(query).tolist()

        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        # Convert to RetrievalResult objects
        retrieval_results = []

        for i, doc_id in enumerate(results['ids'][0]):
            distance = results['distances'][0][i]
            # Convert distance to similarity score (cosine similarity)
            relevance_score = 1 - distance

            if relevance_score >= min_relevance:
                metadata = results['metadatas'][0][i]
                content = results['documents'][0][i]

                doc = LegalDocument(
                    doc_id=doc_id,
                    title=metadata['title'],
                    content=content,
                    case_year=metadata['case_year'],
                    jurisdiction=metadata['jurisdiction'],
                    precedent_value=metadata['precedent_value']
                )

                # Create citation
                citation = f"{metadata['title']}, {metadata['jurisdiction']} ({metadata['case_year']})"

                # Extract excerpt (first 200 chars)
                excerpt = content[:200] + "..." if len(content) > 200 else content

                retrieval_results.append(RetrievalResult(
                    document=doc,
                    relevance_score=relevance_score,
                    citation=citation,
                    excerpt=excerpt
                ))

        return retrieval_results


class RAGLegalAgent:
    """Legal research agent with RAG capabilities."""

    def __init__(self, vector_db: VectorDatabase):
        """Initialize RAG agent with vector database."""
        self.vector_db = vector_db

        # Create ADK agent
        self.agent = LlmAgent(
    name="Agent",
    model="gemini-2.5-flash"
        )

        console.print("[green]✓[/green] RAG Legal Agent initialized")

    async def research_case(
        self,
        query: str,
        jurisdiction: Optional[str] = None
    ) -> Dict[str, Any]:
        """Research legal precedents for a case query."""
        console.print(f"\n[cyan]Research Query:[/cyan] {query}")

        # Retrieve relevant documents
        retrieval_results = self.vector_db.search(
            query=query,
            top_k=5,
            min_relevance=0.75
        )

        if not retrieval_results:
            return {
                "success": False,
                "message": "No relevant precedents found",
                "citations": []
            }

        # Display retrieved documents
        self._display_retrieved_docs(retrieval_results)

        # Build context from retrieved documents
        context = self._build_context(retrieval_results)

        # Generate response with RAG
        prompt = f"""You are a legal research assistant analyzing case precedents.

Query: {query}

Retrieved Precedents:
{context}

Instructions:
1. Analyze the retrieved precedents
2. Identify the most relevant cases
3. Provide a summary of how these precedents apply to the query
4. Include specific citations for each referenced case
5. Note any conflicts or distinctions between precedents

Provide a structured legal research memorandum."""

        # Run agent
        runner = InMemoryRunner(agent=self.agent)
        response = await runner.run(input=prompt)

        # Extract response
        final_response = response.final_message.content.parts[0].text

        return {
            "success": True,
            "query": query,
            "research_memo": final_response,
            "citations": [r.citation for r in retrieval_results],
            "num_precedents": len(retrieval_results),
            "avg_relevance": sum(r.relevance_score for r in retrieval_results) / len(retrieval_results)
        }

    def _build_context(self, results: List[RetrievalResult]) -> str:
        """Build context string from retrieval results."""
        context_parts = []

        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Precedent {i}] {result.citation}\n"
                f"Relevance: {result.relevance_score:.2f}\n"
                f"Excerpt: {result.excerpt}\n"
            )

        return "\n".join(context_parts)

    def _display_retrieved_docs(self, results: List[RetrievalResult]) -> None:
        """Display retrieved documents in a table."""
        table = Table(title="Retrieved Legal Precedents")
        table.add_column("Rank", style="cyan")
        table.add_column("Citation", style="green")
        table.add_column("Relevance", style="yellow")
        table.add_column("Excerpt", style="white", max_width=50)

        for i, result in enumerate(results, 1):
            table.add_row(
                str(i),
                result.citation,
                f"{result.relevance_score:.2%}",
                result.excerpt[:50] + "..."
            )

        console.print(table)


def create_sample_legal_corpus() -> List[LegalDocument]:
    """Create sample legal documents for demonstration."""
    return [
        LegalDocument(
            doc_id="case_001",
            title="Smith v. Johnson",
            content="The court held that in contract disputes involving material breach, "
                   "the non-breaching party is entitled to both rescission and damages. "
                   "A material breach is defined as a failure to perform that is so fundamental "
                   "that it defeats the essential purpose of the contract. The burden of proof "
                   "rests with the party claiming breach.",
            case_year=2018,
            jurisdiction="Federal Circuit",
            precedent_value=0.95
        ),
        LegalDocument(
            doc_id="case_002",
            title="Davis Corp v. TechStart Inc",
            content="In employment contract disputes, non-compete clauses must be reasonable "
                   "in scope, duration, and geographic limitation to be enforceable. The court "
                   "found that a 5-year nationwide restriction was overly broad and contrary to "
                   "public policy. Reasonable restrictions typically range from 6-24 months in "
                   "limited geographic areas.",
            case_year=2020,
            jurisdiction="9th Circuit",
            precedent_value=0.88
        ),
        LegalDocument(
            doc_id="case_003",
            title="Green v. Blue Industries",
            content="Trade secret misappropriation requires proof of: (1) the existence of a "
                   "trade secret, (2) misappropriation through improper means, and (3) damages. "
                   "The plaintiff must demonstrate reasonable efforts to maintain secrecy, "
                   "including confidentiality agreements, restricted access, and security measures. "
                   "Independent discovery or reverse engineering are valid defenses.",
            case_year=2019,
            jurisdiction="Delaware Supreme Court",
            precedent_value=0.92
        ),
        LegalDocument(
            doc_id="case_004",
            title="Martinez v. Software Solutions LLC",
            content="In breach of contract cases, the injured party has a duty to mitigate damages. "
                   "Failure to make reasonable efforts to reduce losses may bar or reduce recovery. "
                   "The court emphasized that mitigation is mandatory, not optional, and the burden "
                   "of proving failure to mitigate rests with the breaching party.",
            case_year=2021,
            jurisdiction="California Supreme Court",
            precedent_value=0.90
        ),
        LegalDocument(
            doc_id="case_005",
            title="United Ventures v. CompetitorCo",
            content="Non-solicitation agreements preventing former employees from soliciting "
                   "the employer's clients are generally enforceable if reasonable. The agreement "
                   "must protect legitimate business interests without unduly restricting employee "
                   "mobility. Courts will blue-pencil overly broad provisions to render them reasonable "
                   "rather than void them entirely.",
            case_year=2022,
            jurisdiction="New York Court of Appeals",
            precedent_value=0.87
        )
    ]


async def demonstrate_rag_pattern():
    """Demonstrate RAG pattern with legal research use case."""
    console.print("\n[bold blue]═══ Pattern 19: Knowledge Retrieval (RAG) ═══[/bold blue]")
    console.print("[bold]Business: GlobalLegal - Legal Research Intelligence[/bold]\n")

    # Initialize vector database
    vector_db = VectorDatabase(collection_name="legal_precedents_demo")

    # Create and index sample legal corpus
    legal_corpus = create_sample_legal_corpus()
    vector_db.index_documents(legal_corpus)

    # Initialize RAG agent
    rag_agent = RAGLegalAgent(vector_db=vector_db)

    # Test queries
    test_queries = [
        {
            "query": "What are the requirements for enforcing a non-compete agreement?",
            "jurisdiction": "Federal"
        },
        {
            "query": "How do courts determine material breach in contract disputes?",
            "jurisdiction": None
        }
    ]

    # Process queries
    results = []
    for test_case in test_queries:
        result = await rag_agent.research_case(
            query=test_case["query"],
            jurisdiction=test_case["jurisdiction"]
        )
        results.append(result)

        # Display research memo
        if result["success"]:
            console.print(f"\n[bold green]Research Memorandum:[/bold green]")
            console.print(result["research_memo"])
            console.print(f"\n[bold]Citations ({result['num_precedents']}):[/bold]")
            for citation in result["citations"]:
                console.print(f"  • {citation}")
            console.print(f"\n[yellow]Average Relevance:[/yellow] {result['avg_relevance']:.2%}")

    # Display business metrics
    display_business_metrics()


def display_business_metrics():
    """Display GlobalLegal business impact metrics."""
    console.print("\n[bold cyan]═══ Business Impact: GlobalLegal ═══[/bold cyan]")

    metrics = Table(title="Legal Research Intelligence Metrics")
    metrics.add_column("Metric", style="cyan")
    metrics.add_column("Before RAG", style="red")
    metrics.add_column("After RAG", style="green")
    metrics.add_column("Impact", style="yellow")

    metrics.add_row(
        "Research Time per Case",
        "8 hours",
        "30 minutes",
        "94% reduction"
    )
    metrics.add_row(
        "Research Accuracy",
        "78% (keyword)",
        "94% (semantic)",
        "+16 points"
    )
    metrics.add_row(
        "Billable Efficiency",
        "Baseline",
        "+34%",
        "$12M value"
    )
    metrics.add_row(
        "Documents Indexed",
        "Manual search",
        "10M docs",
        "Complete coverage"
    )

    console.print(metrics)

    console.print("\n[bold green]Key Benefits:[/bold green]")
    console.print("✓ Grounded responses prevent hallucinations")
    console.print("✓ Citation capability provides transparency")
    console.print("✓ Semantic search improves accuracy")
    console.print("✓ Instant access to entire knowledge base")


if __name__ == "__main__":
    asyncio.run(demonstrate_rag_pattern())
