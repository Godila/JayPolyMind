"""
Deep Research Service
Web-grounded enrichment for ontology generation.
Searches the internet to verify and enrich facts from uploaded documents.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable

from ..utils.llm_client import LLMClient
from ..config import Config
from .web_search import create_search_client, WebSearchClient

logger = logging.getLogger('jaypolymind.deep_research')

# Maximum chars of document text sent to query generation prompt
MAX_DOC_PREVIEW = 5000
# Maximum total chars of search results sent to synthesis prompt
MAX_SEARCH_CONTENT = 15000


QUERY_GENERATION_PROMPT = """You are a research assistant. Analyze the document text and simulation requirement below.
Extract key claims, entities, and facts that should be verified or enriched via web search.
Generate targeted search queries to find real-world information about these entities and claims.

**Output valid JSON only:**
```json
{
  "key_claims": ["claim 1", "claim 2", ...],
  "entities_to_verify": ["Entity Name 1", "Entity Name 2", ...],
  "search_queries": ["search query 1", "search query 2", ...]
}
```

Rules:
- Generate 4-8 search queries (no more than the max_queries limit)
- Queries should be specific and factual (not vague)
- Focus on verifiable claims: names, organizations, dates, roles, events
- Include queries about relationships between key entities
- Write queries in the same language as the document content"""


SYNTHESIS_PROMPT = """You are a fact-checking research analyst. You have been given:
1. Key claims from a document
2. Web search results that may verify, contradict, or enrich these claims

Your task: synthesize the search results into a structured enrichment context that will help
an LLM build a more accurate ontology of entities and relationships.

**Output valid JSON only:**
```json
{
  "enriched_context": "A structured text (500-1500 words) summarizing verified facts, corrections, and newly discovered entities/relationships. Group by topic. For each fact, note whether it was CONFIRMED, CORRECTED, or NEW.",
  "citations": [
    {"fact": "factual statement", "source_url": "https://...", "source_title": "Page Title"},
    ...
  ]
}
```

Rules:
- Focus on facts relevant to social media simulation (entities that can voice opinions, their roles, relationships)
- If search results contradict the document, note the correction clearly
- Include newly discovered stakeholders or organizations not in the original document
- Keep citations concise -- only the most important facts (max 15)
- Write enriched_context in the same language as the original claims"""


@dataclass
class ResearchResult:
    """Result of deep research."""
    enriched_context: str
    citations: List[Dict[str, str]]
    queries_used: List[str]
    total_sources: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enriched_context": self.enriched_context,
            "citations": self.citations,
            "queries_used": self.queries_used,
            "total_sources": self.total_sources,
        }


class DeepResearchService:
    """
    Deep Research: web-grounded enrichment for ontology generation.

    Pipeline:
    1. Extract key claims + generate search queries (LLM)
    2. Execute web searches in parallel
    3. Deduplicate results by URL
    4. Synthesize findings into structured context (LLM)
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        search_client: Optional[WebSearchClient] = None,
    ):
        self.llm_client = llm_client or LLMClient()
        self.search_client = search_client or create_search_client()

    def research(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        max_queries: int = None,
        max_results_per_query: int = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ResearchResult:
        """
        Execute deep research pipeline.

        Args:
            document_texts: Extracted document texts
            simulation_requirement: User's simulation requirement
            max_queries: Max search queries to generate
            max_results_per_query: Max results per query
            progress_callback: Optional callback for progress updates

        Returns:
            ResearchResult with enriched_context and citations
        """
        max_queries = max_queries or Config.DEEP_RESEARCH_MAX_QUERIES
        max_results_per_query = max_results_per_query or Config.DEEP_RESEARCH_MAX_RESULTS

        # Step 1: Generate search queries via LLM
        self._report(progress_callback, "Analyzing document for key claims...")
        queries_data = self._generate_search_queries(
            document_texts, simulation_requirement, max_queries
        )
        queries = queries_data.get("search_queries", [])[:max_queries]
        key_claims = queries_data.get("key_claims", [])

        if not queries:
            logger.warning("No search queries generated, returning empty result")
            return ResearchResult(
                enriched_context="",
                citations=[],
                queries_used=[],
                total_sources=0,
            )

        logger.info(f"Generated {len(queries)} search queries")

        # Step 2: Parallel web search
        self._report(progress_callback, f"Searching web ({len(queries)} queries)...")
        all_results = self._execute_searches_parallel(
            queries, max_results_per_query, progress_callback
        )

        # Step 3: Deduplicate by URL
        unique_results = self._deduplicate_results(all_results)
        logger.info(f"Got {len(unique_results)} unique search results")

        if not unique_results:
            logger.warning("No search results found")
            return ResearchResult(
                enriched_context="",
                citations=[],
                queries_used=queries,
                total_sources=0,
            )

        # Step 4: Synthesize via LLM
        self._report(progress_callback, "Synthesizing research findings...")
        synthesis = self._synthesize_findings(unique_results, key_claims)

        return ResearchResult(
            enriched_context=synthesis.get("enriched_context", ""),
            citations=synthesis.get("citations", []),
            queries_used=queries,
            total_sources=len(unique_results),
        )

    def _generate_search_queries(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        max_queries: int,
    ) -> Dict[str, Any]:
        """Generate search queries from document text via LLM."""
        combined = "\n\n".join(document_texts)
        if len(combined) > MAX_DOC_PREVIEW:
            combined = combined[:MAX_DOC_PREVIEW] + "..."

        user_msg = f"""## Simulation Requirement
{simulation_requirement}

## Document Text (preview)
{combined}

Generate up to {max_queries} search queries to verify and enrich the key facts."""

        messages = [
            {"role": "system", "content": QUERY_GENERATION_PROMPT},
            {"role": "user", "content": user_msg},
        ]

        try:
            return self.llm_client.chat_json(
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
            )
        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            return {"search_queries": [], "key_claims": []}

    def _execute_searches_parallel(
        self,
        queries: List[str],
        max_results_per_query: int,
        progress_callback: Optional[Callable],
    ) -> List[Dict[str, Any]]:
        """Execute searches in parallel using ThreadPoolExecutor."""
        all_results = []

        def do_search(query: str):
            return self.search_client.search(query, max_results=max_results_per_query)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(do_search, q): q for q in queries
            }
            for future in as_completed(futures):
                query = futures[future]
                try:
                    results = future.result()
                    for r in results:
                        all_results.append({
                            "title": r.title,
                            "url": r.url,
                            "content": r.content,
                            "score": r.score,
                            "query": query,
                        })
                except Exception as e:
                    logger.warning(f"Search failed for '{query}': {e}")

        return all_results

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Deduplicate search results by URL."""
        seen_urls = set()
        unique = []
        for r in results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(r)
        return unique

    def _synthesize_findings(
        self,
        results: List[Dict],
        key_claims: List[str],
    ) -> Dict[str, Any]:
        """Synthesize search results into enriched context via LLM."""
        # Build search results text, respecting size limit
        results_text = ""
        for r in results:
            entry = f"### {r['title']}\nURL: {r['url']}\n{r['content']}\n\n"
            if len(results_text) + len(entry) > MAX_SEARCH_CONTENT:
                break
            results_text += entry

        claims_text = "\n".join(f"- {c}" for c in key_claims) if key_claims else "(none extracted)"

        user_msg = f"""## Key Claims from Document
{claims_text}

## Web Search Results
{results_text}

Synthesize these findings into enriched context for ontology generation."""

        messages = [
            {"role": "system", "content": SYNTHESIS_PROMPT},
            {"role": "user", "content": user_msg},
        ]

        try:
            return self.llm_client.chat_json(
                messages=messages,
                temperature=0.2,
                max_tokens=4096,
            )
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return {"enriched_context": "", "citations": []}

    @staticmethod
    def _report(callback: Optional[Callable], msg: str):
        """Report progress if callback is provided."""
        logger.info(msg)
        if callback:
            callback(msg)
