"""
Snapshot model for storing portfolio analysis history.

Uses SQLAlchemy ORM for database persistence. Currently configured for SQLite,
but can be migrated to PostgreSQL by changing the connection string.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Database configuration
BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / 'data' / 'portfolio.db'
DB_PATH.parent.mkdir(exist_ok=True)

# Create engine and base
DATABASE_URL = f'sqlite:///{DB_PATH}'
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Snapshot(Base):
    """Represents a saved portfolio analysis snapshot."""

    __tablename__ = 'snapshots'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Portfolio summary
    total_value = Column(Float, nullable=False)
    total_cost_basis = Column(Float, nullable=False)
    unrealized_gain_loss = Column(Float, nullable=False)
    return_percent = Column(Float, nullable=False)
    num_accounts = Column(Integer, nullable=False)
    num_holdings = Column(Integer, nullable=False)

    # Scores
    diversification_score = Column(Integer)
    diversification_rating = Column(String(50))
    concentration_risk_level = Column(String(50))
    top_10_concentration = Column(Float)
    tax_efficiency_score = Column(Integer)
    tax_efficiency_rating = Column(String(50))

    # JSON fields for complex nested data
    accounts_json = Column(Text)
    asset_allocation_json = Column(Text)
    sector_allocation_json = Column(Text)
    top_holdings_json = Column(Text)
    source_breakdown_json = Column(Text)

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary for template rendering."""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'created_at_formatted': self.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'portfolio': {
                'total_value': self.total_value,
                'total_cost_basis': self.total_cost_basis,
                'unrealized_gain_loss': self.unrealized_gain_loss,
                'return_percent': self.return_percent,
                'num_accounts': self.num_accounts,
                'num_holdings': self.num_holdings,
            },
            'accounts': json.loads(self.accounts_json) if self.accounts_json else [],
            'asset_allocation': json.loads(self.asset_allocation_json) if self.asset_allocation_json else [],
            'sector_allocation': json.loads(self.sector_allocation_json) if self.sector_allocation_json else [],
            'top_holdings': json.loads(self.top_holdings_json) if self.top_holdings_json else [],
            'source_breakdown': json.loads(self.source_breakdown_json) if self.source_breakdown_json else [],
            'diversification': {
                'score': self.diversification_score,
                'rating': self.diversification_rating,
            },
            'concentration': {
                'risk_level': self.concentration_risk_level,
                'top_10_concentration': self.top_10_concentration,
            },
            'tax': {
                'score': self.tax_efficiency_score,
                'rating': self.tax_efficiency_rating,
            },
        }

    @classmethod
    def from_analysis_data(cls, name: str, analysis_data: Dict[str, Any]) -> 'Snapshot':
        """Create a Snapshot from analysis_data dictionary."""
        portfolio = analysis_data.get('portfolio', {})
        diversification = analysis_data.get('diversification', {})
        concentration = analysis_data.get('concentration', {})
        tax = analysis_data.get('tax', {})

        return cls(
            name=name,
            total_value=portfolio.get('total_value', 0),
            total_cost_basis=portfolio.get('total_cost_basis', 0),
            unrealized_gain_loss=portfolio.get('unrealized_gain_loss', 0),
            return_percent=portfolio.get('return_percent', 0),
            num_accounts=portfolio.get('num_accounts', 0),
            num_holdings=portfolio.get('num_holdings', 0),
            diversification_score=diversification.get('score'),
            diversification_rating=diversification.get('rating'),
            concentration_risk_level=concentration.get('risk_level'),
            top_10_concentration=concentration.get('top_10_concentration'),
            tax_efficiency_score=tax.get('score'),
            tax_efficiency_rating=tax.get('rating'),
            accounts_json=json.dumps(analysis_data.get('accounts', [])),
            asset_allocation_json=json.dumps(analysis_data.get('asset_allocation', [])),
            sector_allocation_json=json.dumps(analysis_data.get('sector_allocation', [])),
            top_holdings_json=json.dumps(analysis_data.get('top_holdings', [])),
            source_breakdown_json=json.dumps(analysis_data.get('source_breakdown', [])),
        )

    def __repr__(self) -> str:
        return f"Snapshot(id={self.id}, name='{self.name}', value=${self.total_value:,.2f})"


# Database initialization
def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(engine)


def get_db() -> Session:
    """Get a database session."""
    return SessionLocal()


# CRUD operations
def save_snapshot(name: str, analysis_data: Dict[str, Any]) -> Snapshot:
    """Save a new snapshot to the database."""
    db = get_db()
    try:
        snapshot = Snapshot.from_analysis_data(name, analysis_data)
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot
    finally:
        db.close()


def get_all_snapshots() -> List[Snapshot]:
    """Get all snapshots ordered by creation date (newest first)."""
    db = get_db()
    try:
        return db.query(Snapshot).order_by(Snapshot.created_at.desc()).all()
    finally:
        db.close()


def get_snapshot_by_id(snapshot_id: int) -> Optional[Snapshot]:
    """Get a specific snapshot by ID."""
    db = get_db()
    try:
        return db.query(Snapshot).filter(Snapshot.id == snapshot_id).first()
    finally:
        db.close()


def delete_snapshot(snapshot_id: int) -> bool:
    """Delete a snapshot by ID. Returns True if deleted, False if not found."""
    db = get_db()
    try:
        snapshot = db.query(Snapshot).filter(Snapshot.id == snapshot_id).first()
        if snapshot:
            db.delete(snapshot)
            db.commit()
            return True
        return False
    finally:
        db.close()


def get_snapshots_for_chart() -> List[Dict[str, Any]]:
    """Get snapshots data formatted for Chart.js."""
    db = get_db()
    try:
        snapshots = db.query(Snapshot).order_by(Snapshot.created_at.asc()).all()
        return [
            {
                'id': s.id,
                'date': s.created_at.strftime('%Y-%m-%d'),
                'label': s.created_at.strftime('%b %d'),
                'value': s.total_value,
                'return_percent': s.return_percent,
                'name': s.name,
            }
            for s in snapshots
        ]
    finally:
        db.close()


def calculate_comparison(snapshot1: Snapshot, snapshot2: Snapshot) -> Dict[str, Any]:
    """Calculate differences between two snapshots."""
    value_change = snapshot2.total_value - snapshot1.total_value
    value_change_percent = (value_change / snapshot1.total_value * 100) if snapshot1.total_value > 0 else 0

    return {
        'value_change': value_change,
        'value_change_percent': value_change_percent,
        'return_change': (snapshot2.return_percent or 0) - (snapshot1.return_percent or 0),
        'diversification_change': (snapshot2.diversification_score or 0) - (snapshot1.diversification_score or 0),
        'holdings_change': snapshot2.num_holdings - snapshot1.num_holdings,
        'accounts_change': snapshot2.num_accounts - snapshot1.num_accounts,
    }
