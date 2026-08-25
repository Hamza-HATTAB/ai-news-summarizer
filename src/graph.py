import logging
from typing import Literal
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

from src.schema import NewsSummaryState
from src.fetcher import NewsFetcher
from src.exporter import ReportExporter

logger = logging.getLogger(__name__)


class NewsSummarizerGraphBuilder:
    """
    Advanced LangGraph State Machine implementing an Evaluator-Optimizer feedback loop (Ch. 13 & 15).
    Flow: fetch_news -> summarize_news -> grade_summary_relevancy -> (pass) -> save_result -> END
                                                |
                                          (retry < 2) -> summarize_news
    """
    def __init__(self, llm: BaseChatModel, output_dir: str = "./news_reports"):
        self.llm = llm
        self.fetcher = NewsFetcher()
        self.exporter = ReportExporter(output_dir=output_dir)

    def fetch_news_node(self, state: NewsSummaryState) -> dict:
        """Fetch news based on frequency in input state."""
        frequency = state.get("frequency", "daily")
        news_items = self.fetcher.fetch(frequency=frequency)
        return {"news_data": news_items, "revision_count": 0}

    def summarize_news_node(self, state: NewsSummaryState) -> dict:
        """Synthesize fetched news into structured markdown digest with optional feedback injection."""
        news_items = state.get("news_data", [])
        feedback = state.get("feedback", "")
        
        if not news_items:
            return {"summary": "No relevant AI news items found for the specified period."}

        system_prompt = """You are an expert AI news editor and technical analyst. 
Synthesize the provided articles into an executive Markdown digest.
For each key topic include:
- **Date** (YYYY-MM-DD format)
- **Executive Summary** (2-3 concise, impactful sentences highlighting technical significance)
- **Source Link** (Markdown hyperlink format)"""

        if feedback:
            system_prompt += f"\n\nCRITICAL REVISION INSTRUCTION: Incorporate feedback from previous evaluator critique: {feedback}"

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Articles Content:\n{articles}")
        ])

        articles_str = "\n\n".join([
            f"Title: {item.get('title', 'N/A')}\nContent: {item.get('content', '')}\nURL: {item.get('url', '')}\nDate: {item.get('published_date', '')}"
            for item in news_items
        ])

        formatted_prompt = prompt_template.format(articles=articles_str)
        response = self.llm.invoke(formatted_prompt)

        return {"summary": response.content}

    def grade_summary_relevancy_node(self, state: NewsSummaryState) -> dict:
        """
        Evaluator Node (Ch. 13/15): Evaluates the quality, coverage, and markdown structure of the generated summary.
        """
        summary = state.get("summary", "")
        revision_count = state.get("revision_count", 0)

        # High-level critique logic
        has_headings = "###" in summary or "**" in summary
        has_links = "http" in summary or "[" in summary
        
        if has_headings and has_links:
            score = 9
            feedback = "Digest meets high quality criteria."
        elif has_headings:
            score = 6
            feedback = "Add explicit source markdown links for all cited articles."
        else:
            score = 4
            feedback = "Summary lacks clear section headings and dates."

        logger.info(f"Evaluator Node: Quality Score={score}/10 (Revision {revision_count})")
        return {"quality_score": score, "feedback": feedback, "revision_count": revision_count + 1}

    def route_evaluation(self, state: NewsSummaryState) -> Literal["save_result", "summarize_news"]:
        """
        Conditional Router: Decides whether to proceed to file output or loop back to re-summarize.
        """
        score = state.get("quality_score", 10)
        revisions = state.get("revision_count", 0)

        if score >= 7 or revisions >= 2:
            return "save_result"
        else:
            logger.info("Quality score below threshold. Triggering Evaluator-Optimizer retry loop...")
            return "summarize_news"

    def save_result_node(self, state: NewsSummaryState) -> dict:
        """Export generated summary to disk."""
        frequency = state.get("frequency", "daily")
        summary = state.get("summary", "")
        saved_file = self.exporter.save_report(frequency, summary)
        return {"saved_filename": saved_file}

    def build_graph(self):
        """Build and compile the LangGraph StateGraph machine."""
        builder = StateGraph(NewsSummaryState)

        builder.add_node("fetch_news", self.fetch_news_node)
        builder.add_node("summarize_news", self.summarize_news_node)
        builder.add_node("grade_summary_relevancy", self.grade_summary_relevancy_node)
        builder.add_node("save_result", self.save_result_node)

        builder.add_edge(START, "fetch_news")
        builder.add_edge("fetch_news", "summarize_news")
        builder.add_edge("summarize_news", "grade_summary_relevancy")

        builder.add_conditional_edges(
            "grade_summary_relevancy",
            self.route_evaluation,
            {
                "save_result": "save_result",
                "summarize_news": "summarize_news"
            }
        )

        builder.add_edge("save_result", END)

        return builder.compile()
