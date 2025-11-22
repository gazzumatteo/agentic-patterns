"""
Pattern 19: Knowledge Retrieval (RAG) - CrewAI Implementation

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
from typing import List, Dict, Any
from dataclasses import dataclass
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
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


class VectorSearchInput(BaseModel):
    """Input schema for vector search tool."""
    query: str = Field(..., description="The search query to find relevant legal precedents")
    top_k: int = Field(default=5, description="Number of results to return")


class LegalRAGTool(BaseTool):
    """RAG tool for legal document retrieval."""
    name: str = "legal_precedent_search"
    description: str = "Search legal precedent database for relevant cases using semantic search"

    def __init__(self, vector_db: 'VectorDatabase'):
        super().__init__()
        # Use object.__setattr__ to bypass Pydantic's extra='forbid'
        object.__setattr__(self, 'vector_db', vector_db)

    def _run(self, query: str, top_k: int = 5) -> str:
        """Execute the legal precedent search."""
        results = self.vector_db.search(query=query, top_k=top_k, min_relevance=0.75)

        if not results:
            return "No relevant legal precedents found for this query."

        # Format results as structured text
        output = f"Found {len(results)} relevant precedents:\n\n"

        for i, result in enumerate(results, 1):
            output += f"[Precedent {i}] {result['citation']}\n"
            output += f"Relevance Score: {result['relevance_score']:.2%}\n"
            output += f"Excerpt: {result['excerpt']}\n"
            output += f"Full Text: {result['content']}\n\n"

        return output


class VectorDatabase:
    """Vector database for legal document storage and retrieval."""

    def __init__(self, collection_name: str = "legal_precedents_crewai"):
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
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents."""
        # Generate query embedding
        query_embedding = self.embedder.encode(query).tolist()

        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        # Convert to structured results
        retrieval_results = []

        for i, doc_id in enumerate(results['ids'][0]):
            distance = results['distances'][0][i]
            # Convert distance to similarity score (cosine similarity)
            relevance_score = 1 - distance

            if relevance_score >= min_relevance:
                metadata = results['metadatas'][0][i]
                content = results['documents'][0][i]

                # Create citation
                citation = f"{metadata['title']}, {metadata['jurisdiction']} ({metadata['case_year']})"

                # Extract excerpt
                excerpt = content[:200] + "..." if len(content) > 200 else content

                retrieval_results.append({
                    "doc_id": doc_id,
                    "citation": citation,
                    "content": content,
                    "excerpt": excerpt,
                    "relevance_score": relevance_score,
                    "metadata": metadata
                })

        return retrieval_results


class LegalRAGCrew:
    """Legal research crew with RAG capabilities."""

    def __init__(self, vector_db: VectorDatabase):
        """Initialize RAG crew with vector database."""
        self.vector_db = vector_db

        # Create RAG tool
        self.rag_tool = LegalRAGTool(vector_db=vector_db)

        # Create legal researcher agent
        self.researcher = Agent(
            role="Legal Research Specialist",
            goal="Research legal precedents and provide accurate case analysis",
            backstory="""You are an experienced legal researcher with expertise in
            case law analysis. You excel at finding relevant precedents and
            synthesizing complex legal information.""",
            tools=[self.rag_tool],
            verbose=True,
            allow_delegation=False
        )

        # Create legal analyst agent
        self.analyst = Agent(
            role="Legal Analysis Expert",
            goal="Analyze legal precedents and create comprehensive research memos",
            backstory="""You are a senior legal analyst who specializes in
            creating clear, well-structured legal research memoranda. You
            cite sources meticulously and identify key legal principles.""",
            verbose=True,
            allow_delegation=False
        )

        console.print("[green]✓[/green] Legal RAG Crew initialized")

    def research_case(self, query: str) -> Dict[str, Any]:
        """Research legal precedents for a case query."""
        console.print(f"\n[cyan]Research Query:[/cyan] {query}")

        # Create research task
        research_task = Task(
            description=f"""Search the legal precedent database for cases relevant to: {query}

            Use the legal_precedent_search tool to find relevant precedents.
            Retrieve the top 5 most relevant cases.""",
            agent=self.researcher,
            expected_output="List of relevant legal precedents with citations and excerpts"
        )

        # Create analysis task
        analysis_task = Task(
            description=f"""Analyze the retrieved legal precedents and create a comprehensive
            research memorandum addressing: {query}

            Your memorandum should include:
            1. Summary of the legal issue
            2. Analysis of relevant precedents
            3. Key legal principles identified
            4. Application to the query
            5. Complete citations for all referenced cases

            Provide a structured legal research memorandum.""",
            agent=self.analyst,
            expected_output="Comprehensive legal research memorandum with citations"
        )

        # Create and run crew
        crew = Crew(
            agents=[self.researcher, self.analyst],
            tasks=[research_task, analysis_task],
            verbose=True
        )

        # Execute research
        result = crew.kickoff()

        # Extract citations from vector DB search
        search_results = self.vector_db.search(query=query, top_k=5, min_relevance=0.75)

        return {
            "success": True,
            "query": query,
            "research_memo": str(result),
            "citations": [r["citation"] for r in search_results],
            "num_precedents": len(search_results),
            "avg_relevance": sum(r["relevance_score"] for r in search_results) / len(search_results) if search_results else 0
        }


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


def demonstrate_rag_pattern():
    """Demonstrate RAG pattern with legal research use case."""
    console.print("\n[bold blue]═══ Pattern 19: Knowledge Retrieval (RAG) - CrewAI ═══[/bold blue]")
    console.print("[bold]Business: GlobalLegal - Legal Research Intelligence[/bold]\n")

    # Initialize vector database
    vector_db = VectorDatabase(collection_name="legal_precedents_crewai")

    # Create and index sample legal corpus
    legal_corpus = create_sample_legal_corpus()
    vector_db.index_documents(legal_corpus)

    # Initialize RAG crew
    rag_crew = LegalRAGCrew(vector_db=vector_db)

    # Test query
    query = "What are the requirements for enforcing a non-compete agreement?"

    result = rag_crew.research_case(query=query)

    # Display result
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
    demonstrate_rag_pattern()
