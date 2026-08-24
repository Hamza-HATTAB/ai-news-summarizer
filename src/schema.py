from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class NewsItem(BaseModel):
    """
    Pydantic schema representing an individual fetched news article.
    """
    title: str = Field(description="Title of the news article")
    url: str = Field(description="URL source link of the article")
    content: str = Field(description="Body snippet or text content")
    published_date: Optional[str] = Field(default="N/A", description="Publication timestamp")
    score: float = Field(default=0.0, description="Relevance relevance score")


class NewsSummaryState(TypedDict):
    """
    Immutable state schema passed across LangGraph nodes, supporting
    Evaluator-Optimizer loop state variables (Ch. 13 & 15).
    """
    frequency: Literal["daily", "weekly", "monthly", "year"]
    news_data: List[dict]
    summary: str
    saved_filename: str
    quality_score: int
    feedback: str
    revision_count: int
    error: Optional[str]
