"""
Pattern 20: Agentic RAG - Google ADK Implementation

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

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai.types import GenerateContentConfig
from google.genai import types
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
    credibility_score: float  # 0.0 - 1.0
    recency_score: float  # 0.0 - 1.0


@dataclass
class EvaluatedSource:
    """Source evaluation result."""
    document: FinancialDocument
    relevance_score: float
    quality_score: float
    final_score: float
    reasoning: str
    conflicts: List[str] = field(default_factory=list)


class AgenticVectorDB:
    """Vector database with agentic capabilities."""

    def __init__(self, collection_name: str = "financial_intelligence"):
        self.client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        console.print(f"[green]✓[/green] Agentic Vector DB initialized: {collection_name}")

    def index_documents(self, documents: List[FinancialDocument]) -> None:
        """Index financial documents with rich metadata."""
        console.print(f"\n[yellow]Indexing {len(documents)} financial documents...[/yellow]")

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

    def retrieve_candidates(
        self,
        query: str,
        top_k: int = 10
    ) -> List[FinancialDocument]:
        """Retrieve candidate documents for agentic evaluation."""
        query_embedding = self.embedder.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        candidates = []
        for i, doc_id in enumerate(results['ids'][0]):
            metadata = results['metadatas'][0][i]
            content = results['documents'][0][i]
            distance = results['distances'][0][i]

            doc = FinancialDocument(
                doc_id=doc_id,
                title=metadata['title'],
                content=content,
                source_type=SourceType(metadata['source_type']),
                publisher=metadata['publisher'],
                publish_date=datetime.fromisoformat(metadata['publish_date']),
                credibility_score=metadata['credibility_score'],
                recency_score=metadata['recency_score']
            )

            # Add relevance score
            doc.initial_relevance = 1 - distance
            candidates.append(doc)

        return candidates


class SourceEvaluatorAgent:
    """Agent that evaluates source quality and relevance."""

    def __init__(self):
        self.agent = LlmAgent(
    name="Agent",
    model="gemini-2.5-flash"
        )

    async def evaluate_source(
        self,
        document: FinancialDocument,
        query: str
    ) -> EvaluatedSource:
        """Evaluate a single source for quality and relevance."""
        prompt = f"""Evaluate this financial source for quality and relevance.

Query: {query}

Source Information:
- Title: {document.title}
- Publisher: {document.publisher}
- Type: {document.source_type.value}
- Date: {document.publish_date.strftime('%Y-%m-%d')}
- Content Preview: {document.content[:300]}...

Evaluate on:
1. Relevance to query (0-1)
2. Source credibility (already scored: {document.credibility_score})
3. Information recency (already scored: {document.recency_score})
4. Overall quality assessment

Provide:
- Quality score (0-1)
- Brief reasoning for your assessment
- Any concerns or limitations

Format: quality_score|reasoning"""

        runner = InMemoryRunner(agent=self.agent, app_name="source_evaluator")
        session = await runner.session_service.create_session(
            app_name="source_evaluator",
            user_id="evaluator"
        )

        content = types.Content(role='user', parts=[types.Part(text=prompt)])
        events = runner.run_async(
            user_id="evaluator",
            session_id=session.id,
            new_message=content
        )

        result = None
        async for event in events:
            if event.is_final_response() and event.content:
                result = event.content.parts[0].text
                break

        # Parse response
        try:
            quality_str, reasoning = result.split('|', 1)
            quality_score = float(quality_str.strip())
        except:
            quality_score = 0.7
            reasoning = result

        # Calculate final score combining all factors
        final_score = (
            document.initial_relevance * 0.4 +
            quality_score * 0.3 +
            document.credibility_score * 0.2 +
            document.recency_score * 0.1
        )

        return EvaluatedSource(
            document=document,
            relevance_score=document.initial_relevance,
            quality_score=quality_score,
            final_score=final_score,
            reasoning=reasoning.strip()
        )


class ConflictResolverAgent:
    """Agent that identifies and resolves conflicts between sources."""

    def __init__(self):
        self.agent = LlmAgent(
    name="Agent",
    model="gemini-2.5-flash"
        )

    async def resolve_conflicts(
        self,
        sources: List[EvaluatedSource],
        query: str
    ) -> Dict[str, Any]:
        """Identify conflicts and synthesize unified perspective."""
        # Build context from all sources
        sources_context = "\n\n".join([
            f"[Source {i+1}] {src.document.title} (Score: {src.final_score:.2f})\n"
            f"Publisher: {src.document.publisher}\n"
            f"Date: {src.document.publish_date.strftime('%Y-%m-%d')}\n"
            f"Content: {src.document.content[:400]}...\n"
            for i, src in enumerate(sources)
        ])

        prompt = f"""Analyze these financial sources and resolve any conflicts.

Query: {query}

Sources:
{sources_context}

Tasks:
1. Identify any conflicting information or recommendations
2. Evaluate which sources are more trustworthy for each conflict
3. Synthesize a unified investment thesis
4. Note any unresolved uncertainties

Provide structured analysis with:
- Identified conflicts
- Resolution reasoning
- Unified recommendation
- Confidence level"""

        runner = InMemoryRunner(agent=self.agent, app_name="conflict_resolver")
        session = await runner.session_service.create_session(
            app_name="conflict_resolver",
            user_id="resolver"
        )

        content = types.Content(role='user', parts=[types.Part(text=prompt)])
        events = runner.run_async(
            user_id="resolver",
            session_id=session.id,
            new_message=content
        )

        synthesis_text = None
        async for event in events:
            if event.is_final_response() and event.content:
                synthesis_text = event.content.parts[0].text
                break

        return {
            "synthesis": synthesis_text,
            "num_sources": len(sources),
            "avg_quality": sum(s.final_score for s in sources) / len(sources)
        }


class AgenticRAGAdvisor:
    """Agentic RAG system for financial advisory."""

    def __init__(self, vector_db: AgenticVectorDB):
        self.vector_db = vector_db
        self.evaluator = SourceEvaluatorAgent()
        self.resolver = ConflictResolverAgent()

        console.print("[green]✓[/green] Agentic RAG Advisor initialized")

    async def generate_investment_thesis(
        self,
        query: str,
        min_quality_threshold: float = 0.6
    ) -> Dict[str, Any]:
        """Generate investment thesis using agentic RAG."""
        console.print(f"\n[cyan]Investment Query:[/cyan] {query}")

        # Step 1: Retrieve candidate sources
        console.print("\n[yellow]Step 1: Retrieving candidate sources...[/yellow]")
        candidates = self.vector_db.retrieve_candidates(query, top_k=10)
        console.print(f"Retrieved {len(candidates)} candidate sources")

        # Step 2: Evaluate each source
        console.print("\n[yellow]Step 2: Evaluating source quality...[/yellow]")
        evaluated_sources = []

        for candidate in candidates:
            evaluation = await self.evaluator.evaluate_source(candidate, query)
            evaluated_sources.append(evaluation)

        # Filter by quality threshold
        high_quality_sources = [
            src for src in evaluated_sources
            if src.final_score >= min_quality_threshold
        ]

        console.print(f"Qualified {len(high_quality_sources)}/{len(evaluated_sources)} high-quality sources")

        # Display source evaluation
        self._display_source_evaluation(high_quality_sources)

        # Step 3: Resolve conflicts and synthesize
        if not high_quality_sources:
            return {
                "success": False,
                "message": "No high-quality sources found"
            }

        console.print("\n[yellow]Step 3: Resolving conflicts and synthesizing...[/yellow]")
        synthesis = await self.resolver.resolve_conflicts(high_quality_sources, query)

        return {
            "success": True,
            "query": query,
            "investment_thesis": synthesis["synthesis"],
            "sources_evaluated": len(evaluated_sources),
            "sources_used": len(high_quality_sources),
            "avg_quality_score": synthesis["avg_quality"],
            "sources": [
                {
                    "title": src.document.title,
                    "publisher": src.document.publisher,
                    "score": src.final_score,
                    "reasoning": src.reasoning
                }
                for src in high_quality_sources
            ]
        }

    def _display_source_evaluation(self, sources: List[EvaluatedSource]) -> None:
        """Display source evaluation results."""
        table = Table(title="Source Quality Evaluation")
        table.add_column("Rank", style="cyan")
        table.add_column("Source", style="green", max_width=30)
        table.add_column("Publisher", style="yellow", max_width=20)
        table.add_column("Final Score", style="magenta")
        table.add_column("Reasoning", style="white", max_width=40)

        # Sort by final score
        sorted_sources = sorted(sources, key=lambda x: x.final_score, reverse=True)

        for i, src in enumerate(sorted_sources, 1):
            table.add_row(
                str(i),
                src.document.title[:30],
                src.document.publisher[:20],
                f"{src.final_score:.2%}",
                src.reasoning[:40] + "..."
            )

        console.print(table)


def create_sample_financial_corpus() -> List[FinancialDocument]:
    """Create sample financial documents with varying quality and recency."""
    base_date = datetime.now()

    return [
        FinancialDocument(
            doc_id="fin_001",
            title="Tech Sector Outlook Q4 2024",
            content="Technology sector shows strong fundamentals with cloud computing and AI "
                   "driving growth. Major tech companies report 15-20% YoY revenue growth. "
                   "However, valuations are elevated with P/E ratios above historical averages. "
                   "Recommend selective positioning in companies with strong cash flow and "
                   "sustainable competitive advantages. AI infrastructure and cybersecurity "
                   "remain attractive subsectors.",
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
                   "at >50x revenue despite no profitability. Historical parallels to dot-com "
                   "era suggest caution. However, established tech giants integrating AI show "
                   "strong fundamentals. Recommend avoiding speculative AI-only companies and "
                   "focusing on profitable enterprises with AI as growth driver.",
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
                   "Valuations justified by future growth potential. Strong buy recommendation "
                   "across the sector. This is the beginning of a new tech supercycle that could "
                   "last for years.",
            source_type=SourceType.ANALYST_OPINION,
            publisher="BullMarket Weekly",
            publish_date=base_date - timedelta(days=3),
            credibility_score=0.65,  # Lower credibility - promotional source
            recency_score=0.99
        ),
        FinancialDocument(
            doc_id="fin_004",
            title="Q3 Earnings: Technology Sector",
            content="Technology sector Q3 earnings exceeded expectations with 18% average growth. "
                   "Cloud services revenue up 25%, AI-related revenue up 40% from previous quarter. "
                   "Guidance remains strong for Q4 despite macroeconomic uncertainties. Operating "
                   "margins expanding as companies achieve scale. Free cash flow generation robust "
                   "across large-cap tech names.",
            source_type=SourceType.REGULATORY_FILING,
            publisher="SEC Filings Analysis",
            publish_date=base_date - timedelta(days=15),
            credibility_score=0.98,  # Highest credibility - regulatory data
            recency_score=0.90
        ),
        FinancialDocument(
            doc_id="fin_005",
            title="Tech Bubble Warning Signs",
            content="Several indicators suggest technology sector overheating: Shiller P/E above "
                   "30, retail investor participation at all-time highs, margin debt elevated. "
                   "While AI transformation is real, current valuations price in perfection. "
                   "Historical corrections in tech sector average 35-40% from peaks. Recommend "
                   "taking profits and increasing cash positions.",
            source_type=SourceType.MARKET_ANALYSIS,
            publisher="Contrarian Capital Research",
            publish_date=base_date - timedelta(days=7),
            credibility_score=0.80,
            recency_score=0.96
        )
    ]


async def demonstrate_agentic_rag():
    """Demonstrate agentic RAG pattern for financial advisory."""
    console.print("\n[bold blue]═══ Pattern 20: Agentic RAG ═══[/bold blue]")
    console.print("[bold]Business: PremiumWealth - Financial Advisory Platform[/bold]\n")

    # Initialize system
    vector_db = AgenticVectorDB(collection_name="financial_intelligence")

    # Index financial corpus
    financial_corpus = create_sample_financial_corpus()
    vector_db.index_documents(financial_corpus)

    # Create agentic RAG advisor
    advisor = AgenticRAGAdvisor(vector_db=vector_db)

    # Generate investment thesis
    query = "Should we increase allocation to technology stocks in client portfolios?"

    result = await advisor.generate_investment_thesis(
        query=query,
        min_quality_threshold=0.7
    )

    # Display results
    if result["success"]:
        console.print(Panel(
            result["investment_thesis"],
            title="[bold green]Investment Thesis[/bold green]",
            border_style="green"
        ))

        console.print(f"\n[bold]Analysis Summary:[/bold]")
        console.print(f"  Sources Evaluated: {result['sources_evaluated']}")
        console.print(f"  High-Quality Sources Used: {result['sources_used']}")
        console.print(f"  Average Quality Score: {result['avg_quality_score']:.2%}")

    # Display business impact
    display_business_metrics()


def display_business_metrics():
    """Display PremiumWealth business impact metrics."""
    console.print("\n[bold cyan]═══ Business Impact: PremiumWealth ═══[/bold cyan]")

    metrics = Table(title="Financial Advisory Platform Metrics")
    metrics.add_column("Metric", style="cyan")
    metrics.add_column("Before Agentic RAG", style="red")
    metrics.add_column("After Agentic RAG", style="green")
    metrics.add_column("Impact", style="yellow")

    metrics.add_row(
        "Advisory Quality Score",
        "7.8/10",
        "9.2/10",
        "+18% improvement"
    )
    metrics.add_row(
        "Client Retention Rate",
        "87%",
        "94%",
        "+7 points"
    )
    metrics.add_row(
        "Compliance Violations",
        "Baseline",
        "-76%",
        "Risk reduction"
    )
    metrics.add_row(
        "AUM Growth (18mo)",
        "$50B baseline",
        "+$8B",
        "16% growth"
    )

    console.print(metrics)

    console.print("\n[bold green]Key Advantages Over Simple RAG:[/bold green]")
    console.print("✓ Source quality evaluation prevents bad information")
    console.print("✓ Conflict resolution synthesizes contradictory data")
    console.print("✓ Recency weighting favors current market conditions")
    console.print("✓ Credibility scoring filters unreliable sources")


if __name__ == "__main__":
    asyncio.run(demonstrate_agentic_rag())
