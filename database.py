"""
Database module for Financial News Simplifier.
Uses SQLite and SQLAlchemy ORM to store and query article analyses.
"""

import json
from datetime import datetime, timezone, date
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    desc,
    asc,
    func
)
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

from config import DATABASE_URL, DATA_DIR

Base = declarative_base()


class ArticleAnalysis(Base):
    """SQLAlchemy model representing a saved financial news analysis."""
    __tablename__ = "article_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_url = Column(String(1024), nullable=True)
    headline = Column(String(512), nullable=False)
    article_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    simple_explanation = Column(Text, nullable=False)
    key_points = Column(Text, nullable=False)          # JSON array string
    financial_terms = Column(Text, nullable=False)     # JSON array string
    entities = Column(Text, nullable=False)            # JSON object/array string
    sector = Column(String(128), default="General Economy")
    business_impact = Column(Text, nullable=True)
    consumer_impact = Column(Text, nullable=True)
    economic_impact = Column(Text, nullable=True)
    market_relevance = Column(Text, nullable=True)
    sentiment = Column(String(64), default="Neutral")
    confidence = Column(Integer, default=80)
    uncertainties = Column(Text, default="[]")         # JSON array string
    source_quality_notes = Column(Text, default="[]")  # JSON array string
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert database record to a clean Python dictionary."""
        def safe_json_load(val: Any, default: Any):
            if not val:
                return default
            if isinstance(val, (dict, list)):
                return val
            try:
                return json.loads(val)
            except Exception:
                return default

        return {
            "id": self.id,
            "source_url": self.source_url,
            "headline": self.headline,
            "article_text": self.article_text,
            "short_summary": self.summary,
            "summary": self.summary,
            "simple_explanation": self.simple_explanation,
            "key_points": safe_json_load(self.key_points, []),
            "financial_terms": safe_json_load(self.financial_terms, []),
            "entities": safe_json_load(self.entities, {}),
            "sector": self.sector or "General Economy",
            "possible_business_impact": self.business_impact or "",
            "possible_consumer_impact": self.consumer_impact or "",
            "possible_economic_impact": self.economic_impact or "",
            "possible_market_relevance": self.market_relevance or "",
            "sentiment": self.sentiment or "Neutral",
            "confidence": self.confidence if self.confidence is not None else 80,
            "uncertainties": safe_json_load(self.uncertainties, []),
            "source_quality_notes": safe_json_load(self.source_quality_notes, []),
            "created_at": self.created_at,
        }


# Setup engine and thread-safe session
DATA_DIR.mkdir(parents=True, exist_ok=True)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False
)
SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Session = scoped_session(SessionFactory)


def init_db() -> None:
    """Initialize SQLite database and create tables if they do not exist."""
    Base.metadata.create_all(bind=engine)


def save_analysis(
    analysis_data: Dict[str, Any],
    article_text: str,
    source_url: Optional[str] = None
) -> ArticleAnalysis:
    """
    Save an analysis dictionary into the SQLite database.
    Serializes list and dict fields into JSON strings safely.
    """
    init_db()
    session = Session()
    try:
        def safe_json_dumps(val: Any) -> str:
            if isinstance(val, str):
                return val
            return json.dumps(val, ensure_ascii=False)

        key_pts = safe_json_dumps(analysis_data.get("key_points", []))
        terms = safe_json_dumps(analysis_data.get("financial_terms", []))
        entities = safe_json_dumps(analysis_data.get("entities", {}))
        uncertainties = safe_json_dumps(analysis_data.get("uncertainties", []))
        quality_notes = safe_json_dumps(analysis_data.get("source_quality_notes", []))

        record = ArticleAnalysis(
            source_url=source_url,
            headline=analysis_data.get("headline", "Financial News Analysis"),
            article_text=article_text,
            summary=analysis_data.get("short_summary", "") or analysis_data.get("summary", ""),
            simple_explanation=analysis_data.get("simple_explanation", ""),
            key_points=key_pts,
            financial_terms=terms,
            entities=entities,
            sector=analysis_data.get("sector", "General Economy"),
            business_impact=analysis_data.get("possible_business_impact", ""),
            consumer_impact=analysis_data.get("possible_consumer_impact", ""),
            economic_impact=analysis_data.get("possible_economic_impact", ""),
            market_relevance=analysis_data.get("possible_market_relevance", ""),
            sentiment=analysis_data.get("sentiment", "Neutral"),
            confidence=int(analysis_data.get("confidence", 80)),
            uncertainties=uncertainties,
            source_quality_notes=quality_notes,
            created_at=datetime.now(timezone.utc)
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_analyses(
    search_query: Optional[str] = None,
    sentiment_filter: Optional[str] = None,
    sector_filter: Optional[str] = None,
    sort_order: str = "newest"
) -> List[ArticleAnalysis]:
    """
    Retrieve analyses matching optional search queries, sentiment, and sector filters.
    """
    init_db()
    session = Session()
    try:
        query = session.query(ArticleAnalysis)

        if search_query:
            pattern = f"%{search_query.strip()}%"
            query = query.filter(
                (ArticleAnalysis.headline.ilike(pattern)) |
                (ArticleAnalysis.summary.ilike(pattern)) |
                (ArticleAnalysis.financial_terms.ilike(pattern)) |
                (ArticleAnalysis.sector.ilike(pattern))
            )

        if sentiment_filter and sentiment_filter != "All":
            query = query.filter(ArticleAnalysis.sentiment.ilike(sentiment_filter))

        if sector_filter and sector_filter != "All":
            query = query.filter(ArticleAnalysis.sector.ilike(sector_filter))

        if sort_order == "oldest":
            query = query.order_by(asc(ArticleAnalysis.created_at))
        else:
            query = query.order_by(desc(ArticleAnalysis.created_at))

        results = query.all()
        return results
    finally:
        session.close()


def get_analysis_by_id(analysis_id: int) -> Optional[ArticleAnalysis]:
    """Retrieve a single article analysis by its ID."""
    init_db()
    session = Session()
    try:
        return session.query(ArticleAnalysis).filter(ArticleAnalysis.id == analysis_id).first()
    finally:
        session.close()


def delete_analysis(analysis_id: int) -> bool:
    """Delete an analysis record by its primary key ID."""
    init_db()
    session = Session()
    try:
        item = session.query(ArticleAnalysis).filter(ArticleAnalysis.id == analysis_id).first()
        if item:
            session.delete(item)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()


def get_analytics_summary() -> Dict[str, Any]:
    """
    Calculate summary statistics for dashboard charts and metrics:
    - Total analyses count
    - Analyses created today
    - Sentiment distribution
    - Top financial terms
    - Sector breakdown
    - Daily activity timeline
    """
    init_db()
    session = Session()
    try:
        records = session.query(ArticleAnalysis).all()
        total_count = len(records)
        today = date.today()

        today_count = sum(
            1 for r in records if r.created_at and r.created_at.date() == today
        )

        # Sentiment counts
        sentiment_counts: Dict[str, int] = {}
        sector_counts: Dict[str, int] = {}
        terms_frequency: Dict[str, int] = {}
        daily_activity: Dict[str, int] = {}

        for r in records:
            # Sentiment
            s = (r.sentiment or "Neutral").capitalize()
            sentiment_counts[s] = sentiment_counts.get(s, 0) + 1

            # Sector
            sec = (r.sector or "General Economy").strip()
            sector_counts[sec] = sector_counts.get(sec, 0) + 1

            # Terms
            try:
                term_list = json.loads(r.financial_terms or "[]")
                for t in term_list:
                    name = t.get("term", "").strip()
                    if name:
                        terms_frequency[name] = terms_frequency.get(name, 0) + 1
            except Exception:
                continue

            # Timeline
            if r.created_at:
                d_str = r.created_at.strftime("%Y-%m-%d")
                daily_activity[d_str] = daily_activity.get(d_str, 0) + 1

        # Sort top terms
        top_terms = sorted(terms_frequency.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "total_count": total_count,
            "today_count": today_count,
            "sentiment_counts": sentiment_counts,
            "sector_counts": sector_counts,
            "top_terms": top_terms,
            "daily_activity": daily_activity,
        }
    finally:
        session.close()
