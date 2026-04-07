"""
Deep Research Service v2
3-round iterative web-grounded enrichment for ontology generation.
Searches the internet to verify and enrich facts from uploaded documents.
"""

import uuid
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Callable

from ..utils.llm_client import LLMClient
from ..config import Config
from .web_search import create_search_client, WebSearchClient

logger = logging.getLogger('jaypolymind.deep_research')


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

QUERY_GENERATION_PROMPT = """You are a research analyst preparing to verify claims in a document.

Analyze the document and generate search queries to verify its claims.

Return JSON:
{
  "key_claims": [
    {"claim": "...", "importance": "high/medium", "category": "fact/person/org/date/financial"}
  ],
  "entities_to_verify": [
    {"name": "...", "type": "person/org/product", "context": "mentioned as..."}
  ],
  "search_queries": [
    {"query": "...", "language": "en", "target": "which claim this verifies"}
  ]
}

Rules:
- Generate queries in BOTH the document's language AND English
- Focus on verifiable factual claims, not opinions
- Prioritize: people's roles/titles, financial figures, dates, org relationships
- Each query should target a specific claim
- Write concise, search-engine-friendly queries"""


GAP_ANALYSIS_PROMPT = """You are analyzing research progress to identify gaps.

Determine:
1. Which claims are now CONFIRMED (with source)?
2. Which claims are CONTRADICTED (with counter-evidence)?
3. Which claims remain UNVERIFIED (no relevant results)?

Return JSON:
{
  "confirmed": [{"claim": "...", "source_url": "...", "source_title": "..."}],
  "contradicted": [{"claim": "...", "counter_evidence": "...", "source_url": "..."}],
  "unresolved_gaps": ["claim that needs more search"],
  "follow_up_queries": [
    {"query": "...", "language": "en", "target_gap": "which unresolved claim"}
  ]
}

Rules:
- Only mark as confirmed if source explicitly supports the claim
- Try different search angles (synonym, related org, news vs wiki)
- Do not repeat queries that were already searched"""


SYNTHESIS_PROMPT = """You are synthesizing web research findings into a structured report.

Create a comprehensive research report with individual findings.

Return JSON:
{
  "findings": [
    {
      "fact": "verified factual statement",
      "status": "confirmed/contradicted/unverified",
      "confidence": "high/medium/low",
      "source_url": "https://...",
      "source_title": "Page Title",
      "related_entities": ["entity names mentioned in this fact"]
    }
  ],
  "enriched_context": "Narrative summary (500-1500 words) for ontology generation. Group by topic. For each fact note if CONFIRMED, CORRECTED, or NEW.",
  "summary": {
    "total_claims": 0,
    "confirmed": 0,
    "contradicted": 0,
    "unverified": 0
  }
}

Rules:
- Focus on facts relevant to simulation (entities, roles, relationships)
- If search results contradict the document, note the correction
- Include newly discovered stakeholders not in the original document
- Max 20 findings, prioritize by importance
- Write enriched_context in the same language as the original claims"""


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ResearchFinding:
    """A single verified/unverified fact from web research."""
    id: str
    fact: str
    source_url: str
    source_title: str
    research_round: int
    confidence: str  # confirmed / unverified / contradicted
    related_entities: List[str] = field(default_factory=list)
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResearchResult:
    """Result of deep research."""
    enriched_context: str
    citations: List[Dict[str, str]]
    queries_used: List[str]
    total_sources: int
    findings: List[ResearchFinding] = field(default_factory=list)
    rounds_completed: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enriched_context": self.enriched_context,
            "citations": self.citations,
            "queries_used": self.queries_used,
            "total_sources": self.total_sources,
            "findings": [f.to_dict() for f in self.findings],
            "rounds_completed": self.rounds_completed,
        }


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class DeepResearchService:
    """
    Deep Research v2: 3-round iterative web-grounded enrichment.

    Pipeline per round:
    1. Generate/refine search queries (LLM)
    2. Execute web searches in parallel (SearXNG)
    3. Deduplicate results

    After all rounds:
    4. Synthesize findings (LLM) -> structured ResearchResult
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        search_client: Optional[WebSearchClient] = None,
    ):
        self.llm_client = llm_client or LLMClient()
        self.search_client = search_client or create_search_client()

    # ------------------------------------------------------------------
    # v2: Async iterative research (called from background thread)
    # ------------------------------------------------------------------

    def research_iterative(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        task_id: str,
        task_manager,
    ) -> None:
        """
        3-round iterative research. Runs in a background thread.
        Updates progress via task_manager. Stores result in task on completion.
        """
        try:
            self._run_iterative(document_texts, simulation_requirement, task_id, task_manager)
        except Exception as e:
            logger.error(f"Research failed: {e}", exc_info=True)
            task_manager.fail_task(task_id, str(e))

    def _run_iterative(self, document_texts, requirement, task_id, task_manager):
        doc_preview_len = Config.DEEP_RESEARCH_DOC_PREVIEW
        max_content = Config.DEEP_RESEARCH_MAX_CONTENT
        round_queries = [
            Config.DEEP_RESEARCH_ROUND1_QUERIES,
            Config.DEEP_RESEARCH_ROUND2_QUERIES,
            Config.DEEP_RESEARCH_ROUND3_QUERIES,
        ]

        combined_text = "\n\n".join(document_texts)
        doc_preview = combined_text[:doc_preview_len]
        if len(combined_text) > doc_preview_len:
            doc_preview += "..."

        all_search_results = []
        all_queries_used = []
        key_claims = []
        accumulated_findings_text = ""

        # ---- Round 1: Initial queries ----
        task_manager.update_task(task_id, status="running", progress=5,
                                message="Round 1/3: Analyzing document...")

        queries_data = self._generate_initial_queries(doc_preview, requirement, round_queries[0])
        key_claims = queries_data.get("key_claims", [])
        queries = [q["query"] if isinstance(q, dict) else q
                   for q in queries_data.get("search_queries", [])][:round_queries[0]]
        all_queries_used.extend(queries)

        if not queries:
            task_manager.complete_task(task_id, ResearchResult(
                enriched_context="", citations=[], queries_used=[],
                total_sources=0, findings=[], rounds_completed=0,
            ).to_dict())
            return

        task_manager.update_task(task_id, status="running", progress=10,
                                message=f"Round 1/3: Searching ({len(queries)} queries)...",
                                result={"current_query": queries[0] if queries else ""})

        r1_results = self._execute_searches_parallel(queries)
        r1_unique = self._deduplicate_results(r1_results, set())
        all_search_results.extend(r1_unique)
        seen_urls = {r["url"] for r in all_search_results}

        accumulated_findings_text = self._results_to_text(r1_unique, max_content // 3)

        task_manager.update_task(task_id, status="running", progress=30,
                                message=f"Round 1/3: Found {len(r1_unique)} sources")

        # ---- Round 2: Gap analysis + follow-up ----
        task_manager.update_task(task_id, status="running", progress=35,
                                message="Round 2/3: Analyzing gaps...")

        gap_data = self._analyze_gaps(key_claims, accumulated_findings_text, all_queries_used)
        r2_queries = [q["query"] if isinstance(q, dict) else q
                      for q in gap_data.get("follow_up_queries", [])][:round_queries[1]]
        all_queries_used.extend(r2_queries)

        if r2_queries:
            task_manager.update_task(task_id, status="running", progress=40,
                                    message=f"Round 2/3: Searching ({len(r2_queries)} queries)...",
                                    result={"current_query": r2_queries[0]})

            r2_results = self._execute_searches_parallel(r2_queries)
            r2_unique = self._deduplicate_results(r2_results, seen_urls)
            all_search_results.extend(r2_unique)
            seen_urls.update(r["url"] for r in r2_unique)

            accumulated_findings_text += "\n" + self._results_to_text(r2_unique, max_content // 3)

        task_manager.update_task(task_id, status="running", progress=60,
                                message=f"Round 2/3: Total {len(all_search_results)} sources")

        # ---- Round 3: Final follow-up ----
        task_manager.update_task(task_id, status="running", progress=65,
                                message="Round 3/3: Final verification...")

        gap_data_2 = self._analyze_gaps(key_claims, accumulated_findings_text, all_queries_used)
        r3_queries = [q["query"] if isinstance(q, dict) else q
                      for q in gap_data_2.get("follow_up_queries", [])][:round_queries[2]]
        all_queries_used.extend(r3_queries)

        if r3_queries:
            task_manager.update_task(task_id, status="running", progress=70,
                                    message=f"Round 3/3: Searching ({len(r3_queries)} queries)...",
                                    result={"current_query": r3_queries[0]})

            r3_results = self._execute_searches_parallel(r3_queries)
            r3_unique = self._deduplicate_results(r3_results, seen_urls)
            all_search_results.extend(r3_unique)

            accumulated_findings_text += "\n" + self._results_to_text(r3_unique, max_content // 3)

        task_manager.update_task(task_id, status="running", progress=85,
                                message="Synthesizing all findings...")

        # ---- Synthesis ----
        synthesis = self._synthesize_findings_v2(
            accumulated_findings_text, key_claims, max_content
        )

        findings = []
        for i, f in enumerate(synthesis.get("findings", [])):
            findings.append(ResearchFinding(
                id=str(uuid.uuid4()),
                fact=f.get("fact", ""),
                source_url=f.get("source_url", ""),
                source_title=f.get("source_title", ""),
                research_round=f.get("research_round", 1),
                confidence=f.get("status", f.get("confidence", "unverified")),
                related_entities=f.get("related_entities", []),
                enabled=f.get("status", "") != "contradicted",
            ))

        citations = [{"fact": f.fact, "source_url": f.source_url,
                       "source_title": f.source_title} for f in findings]

        result = ResearchResult(
            enriched_context=synthesis.get("enriched_context", ""),
            citations=citations,
            queries_used=all_queries_used,
            total_sources=len(all_search_results),
            findings=findings,
            rounds_completed=3,
        )

        task_manager.update_task(task_id, status="running", progress=95,
                                message=f"Done: {len(findings)} findings from {len(all_search_results)} sources")
        task_manager.complete_task(task_id, result.to_dict())

    # ------------------------------------------------------------------
    # v1: Synchronous research (backward compat)
    # ------------------------------------------------------------------

    def research(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        max_queries: int = None,
        max_results_per_query: int = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ResearchResult:
        """Synchronous single-round research (v1 backward compat)."""
        max_queries = max_queries or Config.DEEP_RESEARCH_MAX_QUERIES
        max_results_per_query = max_results_per_query or Config.DEEP_RESEARCH_MAX_RESULTS

        self._report(progress_callback, "Analyzing document for key claims...")
        queries_data = self._generate_initial_queries(
            "\n\n".join(document_texts)[:Config.DEEP_RESEARCH_DOC_PREVIEW],
            simulation_requirement, max_queries,
        )
        queries = [q["query"] if isinstance(q, dict) else q
                   for q in queries_data.get("search_queries", [])][:max_queries]
        key_claims = queries_data.get("key_claims", [])

        if not queries:
            return ResearchResult(enriched_context="", citations=[],
                                  queries_used=[], total_sources=0)

        self._report(progress_callback, f"Searching web ({len(queries)} queries)...")
        all_results = self._execute_searches_parallel(queries, max_results_per_query)
        unique_results = self._deduplicate_results(all_results, set())

        if not unique_results:
            return ResearchResult(enriched_context="", citations=[],
                                  queries_used=queries, total_sources=0)

        self._report(progress_callback, "Synthesizing research findings...")
        results_text = self._results_to_text(unique_results, Config.DEEP_RESEARCH_MAX_CONTENT)
        synthesis = self._synthesize_findings_v2(
            results_text,
            [c["claim"] if isinstance(c, dict) else c for c in key_claims],
            Config.DEEP_RESEARCH_MAX_CONTENT,
        )

        findings = []
        for f in synthesis.get("findings", []):
            findings.append(ResearchFinding(
                id=str(uuid.uuid4()),
                fact=f.get("fact", ""),
                source_url=f.get("source_url", ""),
                source_title=f.get("source_title", ""),
                research_round=1,
                confidence=f.get("status", "unverified"),
                related_entities=f.get("related_entities", []),
            ))

        citations = [{"fact": f.fact, "source_url": f.source_url,
                       "source_title": f.source_title} for f in findings]

        return ResearchResult(
            enriched_context=synthesis.get("enriched_context", ""),
            citations=citations,
            queries_used=queries,
            total_sources=len(unique_results),
            findings=findings,
            rounds_completed=1,
        )

    # ------------------------------------------------------------------
    # LLM call helpers
    # ------------------------------------------------------------------

    def _generate_initial_queries(self, doc_preview, requirement, max_queries):
        """Round 1: generate search queries from document text."""
        user_msg = f"""## Simulation Requirement
{requirement}

## Document Text (preview)
{doc_preview}

Generate up to {max_queries} search queries to verify and enrich the key facts."""

        messages = [
            {"role": "system", "content": QUERY_GENERATION_PROMPT},
            {"role": "user", "content": user_msg},
        ]
        try:
            return self.llm_client.chat_json(messages=messages, temperature=0.3, max_tokens=1500)
        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            return {"search_queries": [], "key_claims": []}

    def _analyze_gaps(self, key_claims, accumulated_results_text, already_searched):
        """Rounds 2-3: analyze gaps and generate follow-up queries."""
        claims_text = "\n".join(
            f"- {c['claim'] if isinstance(c, dict) else c}" for c in key_claims
        ) if key_claims else "(none)"

        already_text = "\n".join(f"- {q}" for q in already_searched) if already_searched else "(none)"

        user_msg = f"""## Original Claims
{claims_text}

## Already Searched Queries
{already_text}

## Search Results So Far
{accumulated_results_text[:Config.DEEP_RESEARCH_MAX_CONTENT]}

Analyze gaps and generate follow-up queries for unresolved claims."""

        messages = [
            {"role": "system", "content": GAP_ANALYSIS_PROMPT},
            {"role": "user", "content": user_msg},
        ]
        try:
            return self.llm_client.chat_json(messages=messages, temperature=0.3, max_tokens=1500)
        except Exception as e:
            logger.error(f"Gap analysis failed: {e}")
            return {"follow_up_queries": [], "unresolved_gaps": []}

    def _synthesize_findings_v2(self, results_text, key_claims, max_content):
        """Final synthesis: combine all results into structured findings."""
        claims_text = "\n".join(
            f"- {c['claim'] if isinstance(c, dict) else c}" for c in key_claims
        ) if key_claims else "(none extracted)"

        user_msg = f"""## Key Claims from Document
{claims_text}

## All Web Search Results
{results_text[:max_content]}

Synthesize these findings into structured report with individual findings."""

        messages = [
            {"role": "system", "content": SYNTHESIS_PROMPT},
            {"role": "user", "content": user_msg},
        ]
        try:
            return self.llm_client.chat_json(messages=messages, temperature=0.2, max_tokens=4096)
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return {"enriched_context": "", "findings": [], "citations": []}

    # ------------------------------------------------------------------
    # Search helpers
    # ------------------------------------------------------------------

    def _execute_searches_parallel(self, queries, max_results_per_query=None):
        """Execute searches in parallel using ThreadPoolExecutor."""
        max_results = max_results_per_query or Config.DEEP_RESEARCH_MAX_RESULTS
        all_results = []

        def do_search(query):
            return self.search_client.search(query, max_results=max_results)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(do_search, q): q for q in queries}
            for future in as_completed(futures):
                query = futures[future]
                try:
                    results = future.result(timeout=20)
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

    def _deduplicate_results(self, results, seen_urls=None):
        """Deduplicate search results by URL."""
        if seen_urls is None:
            seen_urls = set()
        unique = []
        for r in results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(r)
        return unique

    def _results_to_text(self, results, max_chars):
        """Convert search results to text for LLM consumption."""
        text = ""
        for r in results:
            entry = f"### {r['title']}\nURL: {r['url']}\n{r['content']}\n\n"
            if len(text) + len(entry) > max_chars:
                break
            text += entry
        return text

    @staticmethod
    def _report(callback, msg):
        logger.info(msg)
        if callback:
            callback(msg)
