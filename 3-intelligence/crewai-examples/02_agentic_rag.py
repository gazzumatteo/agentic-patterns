"""
Pattern 20: Agentic RAG - CrewAI Implementation

Adds reasoning layer to retrieval. Agent evaluates source quality, resolves conflicts,
and synthesizes contradictory information.

Business Example: PremiumWealth ($50B AUM)
- Advisory quality score: 7.8 → 9.2
- Client retention: 87% → 94%
- Compliance violations: -76%
- AUM growth: +$8B in 18 months

Mermaid Diagram Reference: diagrams/pattern-20-agentic-rag.mmd
Medium Article: Part 3 - Governance and Reliability Patterns
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

load_dotenv()
console = Console()


class SourceType(Enum):
    """Types of financial information sources."""
    MARKET_ANALYSIS = "market_analysis"
    RESEARCH_REPORT = "research_report"
    REGULATORY_FILING = "regulatory_filing"
    NEWS_ARTICLE = "news_article"
    ANALYST_OPINION = "analyst_opinion"


@dataclass
class FinancialDocument:
    """Financial advisory document with metadata."""
    doc_id: str
    title: str
    content: str
    source_type: SourceType
    publisher: str
    publish_date: datetime
    credibility_score: float
    recency_score: float


class AgenticVectorDB:
    """Vector database with quality metadata."""

    def __init__(self, collection_name: str = "financial_intelligence_crew"):
        self.client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        console.print(f"[green]✓[/green] Agentic Vector DB initialized")

    def index_documents(self, documents: List[FinancialDocument]) -> None:
        """Index financial documents."""
        for doc in documents:
            embedding = self.embedder.encode(doc.content).tolist()

            self.collection.add(
                ids=[doc.doc_id],
                embeddings=[embedding],
                documents=[doc.content],
                metadatas=[{
                    "title": doc.title,
                    "source_type": doc.source_type.value,
                    "publisher": doc.publisher,
                    "publish_date": doc.publish_date.isoformat(),
                    "credibility_score": doc.credibility_score,
                    "recency_score": doc.recency_score
                }]
            )

        console.print(f"[green]✓[/green] Indexed {len(documents)} documents")

    def retrieve_with_quality(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Retrieve documents with quality scores."""
        query_embedding = self.embedder.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        candidates = []
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            content = results['documents'][0][i]
            relevance = 1 - results['distances'][0][i]

            # Calculate composite quality score
            quality_score = (
                relevance * 0.4 +
                metadata['credibility_score'] * 0.4 +
                metadata['recency_score'] * 0.2
            )

            candidates.append({
                "title": metadata['title'],
                "content": content,
                "publisher": metadata['publisher'],
                "source_type": metadata['source_type'],
                "publish_date": metadata['publish_date'],
                "relevance_score": relevance,
                "credibility_score": metadata['credibility_score'],
                "recency_score": metadata['recency_score'],
                "quality_score": quality_score
            })

        return sorted(candidates, key=lambda x: x['quality_score'], reverse=True)


class FinancialRetrievalTool(BaseTool):
    """Tool for retrieving and evaluating financial sources."""
    name: str = "financial_source_retrieval"
    description: str = "Retrieve and evaluate financial sources with quality scoring"

    def __init__(self, vector_db: AgenticVectorDB):
        super().__init__()
        object.__setattr__(self, 'vector_db', vector_db)

    def _run(self, query: str, min_quality: float = 0.7) -> str:
        """Execute retrieval with quality filtering."""
        results = self.vector_db.retrieve_with_quality(query, top_k=10)

        # Filter by quality threshold
        high_quality = [r for r in results if r['quality_score'] >= min_quality]

        if not high_quality:
            return "No high-quality sources found meeting the threshold."

        output = f"Retrieved {len(high_quality)} high-quality sources:\n\n"

        for i, source in enumerate(high_quality, 1):
            output += f"[Source {i}] {source['title']}\n"
            output += f"Publisher: {source['publisher']}\n"
            output += f"Quality Score: {source['quality_score']:.2%}\n"
            output += f"  - Relevance: {source['relevance_score']:.2%}\n"
            output += f"  - Credibility: {source['credibility_score']:.2%}\n"
            output += f"  - Recency: {source['recency_score']:.2%}\n"
            output += f"Content: {source['content'][:300]}...\n\n"

        return output


class AgenticRAGCrew:
    """Agentic RAG crew for financial advisory."""

    def __init__(self, vector_db: AgenticVectorDB):
        self.vector_db = vector_db
        self.retrieval_tool = FinancialRetrievalTool(vector_db=vector_db)

        # Source Evaluator Agent
        self.evaluator = Agent(
            role="Financial Source Evaluator",
            goal="Evaluate financial sources for quality, credibility, and relevance",
            backstory="""You are an expert at assessing the quality and reliability
            of financial information sources. You consider source credibility,
            recency, relevance, and potential biases.""",
            tools=[self.retrieval_tool],
            verbose=True,
            allow_delegation=False
        )

        # Conflict Resolver Agent
        self.resolver = Agent(
            role="Financial Analyst",
            goal="Resolve conflicts between sources and synthesize investment thesis",
            backstory="""You are a senior financial analyst skilled at identifying
            conflicts in financial data, evaluating contradictory recommendations,
            and synthesizing coherent investment perspectives.""",
            verbose=True,
            allow_delegation=False
        )

        # Quality Assurance Agent
        self.qa_agent = Agent(
            role="Compliance Officer",
            goal="Ensure investment recommendations meet compliance and quality standards",
            backstory="""You ensure all investment advice is well-supported,
            balanced, and compliant with regulatory requirements. You flag
            any potential compliance issues.""",
            verbose=True,
            allow_delegation=False
        )

        console.print("[green]✓[/green] Agentic RAG Crew initialized")

    def generate_advisory(self, query: str) -> Dict[str, Any]:
        """Generate investment advisory using agentic RAG."""
        console.print(f"\n[cyan]Investment Query:[/cyan] {query}")

        # Task 1: Retrieve and evaluate sources
        eval_task = Task(
            description=f"""Retrieve financial sources relevant to: {query}

            Use the financial_source_retrieval tool with min_quality=0.7.
            Evaluate each source for:
            1. Relevance to the query
            2. Source credibility
            3. Information recency
            4. Potential biases

            Identify the top 3-5 highest quality sources.""",
            agent=self.evaluator,
            expected_output="List of evaluated sources with quality assessments"
        )

        # Task 2: Resolve conflicts and synthesize
        resolve_task = Task(
            description=f"""Analyze the evaluated sources and create investment thesis.

            Tasks:
            1. Identify any conflicting recommendations
            2. Evaluate which sources are more trustworthy
            3. Synthesize a balanced investment perspective
            4. Note areas of uncertainty or disagreement

            Provide structured investment recommendation.""",
            agent=self.resolver,
            expected_output="Synthesized investment thesis with conflict resolution"
        )

        # Task 3: Quality assurance
        qa_task = Task(
            description="""Review the investment thesis for compliance and quality.

            Check:
            1. Is the recommendation well-supported by evidence?
            2. Are risks and uncertainties clearly disclosed?
            3. Is the advice balanced and not overly promotional?
            4. Does it meet fiduciary standards?

            Provide final approved recommendation or required modifications.""",
            agent=self.qa_agent,
            expected_output="Compliance-approved investment recommendation"
        )

        # Create and run crew
        crew = Crew(
            agents=[self.evaluator, self.resolver, self.qa_agent],
            tasks=[eval_task, resolve_task, qa_task],
            verbose=True
        )

        result = crew.kickoff()

        # Get quality metrics
        sources = self.vector_db.retrieve_with_quality(query, top_k=10)
        high_quality = [s for s in sources if s['quality_score'] >= 0.7]

        return {
            "success": True,
            "query": query,
            "investment_thesis": str(result),
            "sources_evaluated": len(sources),
            "sources_used": len(high_quality),
            "avg_quality_score": sum(s['quality_score'] for s in high_quality) / len(high_quality) if high_quality else 0
        }


def create_sample_financial_corpus() -> List[FinancialDocument]:
    """Create sample financial documents."""
    base_date = datetime.now()

    return [
        FinancialDocument(
            doc_id="fin_001",
            title="Tech Sector Outlook Q4 2024",
            content="Technology sector shows strong fundamentals with cloud computing and AI "
                   "driving growth. Major tech companies report 15-20% YoY revenue growth. "
                   "However, valuations are elevated with P/E ratios above historical averages.",
            source_type=SourceType.MARKET_ANALYSIS,
            publisher="Goldman Sachs Research",
            publish_date=base_date - timedelta(days=5),
            credibility_score=0.95,
            recency_score=0.98
        ),
        FinancialDocument(
            doc_id="fin_002",
            title="AI Companies Valuation Analysis",
            content="AI sector experiencing bubble-like conditions with many companies trading "
                   "at >50x revenue despite no profitability. Historical parallels to dot-com era "
                   "suggest caution. However, established tech giants integrating AI show strong fundamentals.",
            source_type=SourceType.RESEARCH_REPORT,
            publisher="Morgan Stanley",
            publish_date=base_date - timedelta(days=10),
            credibility_score=0.93,
            recency_score=0.95
        ),
        FinancialDocument(
            doc_id="fin_003",
            title="Tech Stock Rally to Continue",
            content="Technology stocks poised for continued rally as AI adoption accelerates. "
                   "Every company is investing in AI infrastructure, creating massive TAM. "
                   "Valuations justified by future growth potential. Strong buy recommendation.",
            source_type=SourceType.ANALYST_OPINION,
            publisher="BullMarket Weekly",
            publish_date=base_date - timedelta(days=3),
            credibility_score=0.65,
            recency_score=0.99
        ),
        FinancialDocument(
            doc_id="fin_004",
            title="Q3 Earnings: Technology Sector",
            content="Technology sector Q3 earnings exceeded expectations with 18% average growth. "
                   "Cloud services revenue up 25%, AI-related revenue up 40% from previous quarter. "
                   "Operating margins expanding as companies achieve scale.",
            source_type=SourceType.REGULATORY_FILING,
            publisher="SEC Filings Analysis",
            publish_date=base_date - timedelta(days=15),
            credibility_score=0.98,
            recency_score=0.90
        ),
        FinancialDocument(
            doc_id="fin_005",
            title="Tech Bubble Warning Signs",
            content="Several indicators suggest technology sector overheating: Shiller P/E above 30, "
                   "retail investor participation at all-time highs, margin debt elevated. "
                   "While AI transformation is real, current valuations price in perfection.",
            source_type=SourceType.MARKET_ANALYSIS,
            publisher="Contrarian Capital Research",
            publish_date=base_date - timedelta(days=7),
            credibility_score=0.80,
            recency_score=0.96
        )
    ]


def demonstrate_agentic_rag():
    """Demonstrate agentic RAG pattern."""
    console.print("\n[bold blue]═══ Pattern 20: Agentic RAG - CrewAI ═══[/bold blue]")
    console.print("[bold]Business: PremiumWealth - Financial Advisory[/bold]\n")

    # Initialize
    vector_db = AgenticVectorDB()
    financial_corpus = create_sample_financial_corpus()
    vector_db.index_documents(financial_corpus)

    # Create crew
    advisor = AgenticRAGCrew(vector_db=vector_db)

    # Generate advisory
    query = "Should we increase allocation to technology stocks in client portfolios?"
    result = advisor.generate_advisory(query)

    # Display results
    if result["success"]:
        console.print(Panel(
            result["investment_thesis"],
            title="[bold green]Investment Thesis[/bold green]",
            border_style="green"
        ))

        console.print(f"\n[bold]Analysis Summary:[/bold]")
        console.print(f"  Sources Evaluated: {result['sources_evaluated']}")
        console.print(f"  High-Quality Sources: {result['sources_used']}")
        console.print(f"  Avg Quality Score: {result['avg_quality_score']:.2%}")

    # Display metrics
    display_business_metrics()


def display_business_metrics():
    """Display business impact metrics."""
    console.print("\n[bold cyan]═══ Business Impact: PremiumWealth ═══[/bold cyan]")

    metrics = Table(title="Financial Advisory Metrics")
    metrics.add_column("Metric", style="cyan")
    metrics.add_column("Before", style="red")
    metrics.add_column("After", style="green")
    metrics.add_column("Impact", style="yellow")

    metrics.add_row("Advisory Quality", "7.8/10", "9.2/10", "+18%")
    metrics.add_row("Client Retention", "87%", "94%", "+7 points")
    metrics.add_row("Compliance Violations", "Baseline", "-76%", "Risk reduction")
    metrics.add_row("AUM Growth (18mo)", "$50B", "+$8B", "16% growth")

    console.print(metrics)


if __name__ == "__main__":
    demonstrate_agentic_rag()
