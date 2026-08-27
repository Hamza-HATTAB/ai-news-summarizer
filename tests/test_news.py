import os
import pytest
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage

from src.fetcher import NewsFetcher
from src.exporter import ReportExporter
from src.graph import NewsSummarizerGraphBuilder


def test_news_fetcher_mock_fallback(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    fetcher = NewsFetcher()
    items = fetcher.fetch(frequency="daily")
    
    assert len(items) > 0
    assert "title" in items[0]
    assert "url" in items[0]


def test_report_exporter(tmp_path):
    output_dir = str(tmp_path / "test_reports")
    exporter = ReportExporter(output_dir=output_dir)
    
    filepath = exporter.save_report("daily", "## Test Summary")
    assert os.path.exists(filepath)
    with open(filepath, "r") as f:
        content = f.read()
    assert "Daily Artificial Intelligence Industry Digest" in content
    assert "## Test Summary" in content


def test_evaluator_optimizer_graph_execution(tmp_path, monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    output_dir = str(tmp_path / "graph_reports")

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="### 2026-08-30\n- [Test Summary](https://example.com)")

    builder = NewsSummarizerGraphBuilder(llm=mock_llm, output_dir=output_dir)
    graph = builder.build_graph()

    initial_state = {
        "frequency": "daily",
        "news_data": [],
        "summary": "",
        "saved_filename": "",
        "quality_score": 0,
        "feedback": "",
        "revision_count": 0,
        "error": None
    }

    result = graph.invoke(initial_state)

    assert result["summary"] != ""
    assert result["quality_score"] >= 7
    assert os.path.exists(result["saved_filename"])
