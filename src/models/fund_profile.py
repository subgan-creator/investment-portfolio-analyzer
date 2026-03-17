"""
Fund Profile model for storing fund composition data.

Stores asset allocation breakdowns for target date funds and other investment funds,
enabling "look-through" analysis of portfolio holdings.
"""
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, Integer, Float, String, DateTime, Text

# Import Base from existing snapshot model to share the same database
from src.models.snapshot import Base, engine, SessionLocal


class FundProfile(Base):
    """Represents a fund's composition profile for look-through analysis."""

    __tablename__ = 'fund_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Fund identification
    fund_name = Column(String(255), nullable=False, index=True)
    source = Column(String(100), nullable=True)  # e.g., "JPMC Empower", "Wells Fargo"
    fund_type = Column(String(100), nullable=True)  # e.g., "Target Date", "Index", "Balanced"
    target_year = Column(Integer, nullable=True)  # e.g., 2045 for Target Date 2045 Fund

    # Fund metadata
    risk_assessment = Column(String(50), nullable=True)  # e.g., "Aggressive", "Moderate", "Conservative"
    expense_ratio = Column(Float, nullable=True)

    # Asset allocation as JSON
    # Example: {"us_large_cap": 45.69, "us_mid_cap": 6.05, "international": 21.65, ...}
    asset_allocation_json = Column(Text, nullable=True)

    # Sector breakdown as JSON (optional, if available)
    # Example: {"technology": 25, "healthcare": 15, "financials": 12, ...}
    sector_breakdown_json = Column(Text, nullable=True)

    # Top holdings as JSON (optional, if available)
    # Example: [{"ticker": "AAPL", "name": "Apple Inc", "percent": 3.5}, ...]
    top_holdings_json = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def asset_allocation(self) -> Dict[str, float]:
        """Get asset allocation as dictionary."""
        if self.asset_allocation_json:
            return json.loads(self.asset_allocation_json)
        return {}

    @asset_allocation.setter
    def asset_allocation(self, value: Dict[str, float]):
        """Set asset allocation from dictionary."""
        self.asset_allocation_json = json.dumps(value)

    @property
    def sector_breakdown(self) -> Dict[str, float]:
        """Get sector breakdown as dictionary."""
        if self.sector_breakdown_json:
            return json.loads(self.sector_breakdown_json)
        return {}

    @sector_breakdown.setter
    def sector_breakdown(self, value: Dict[str, float]):
        """Set sector breakdown from dictionary."""
        self.sector_breakdown_json = json.dumps(value)

    @property
    def top_holdings(self) -> List[Dict[str, Any]]:
        """Get top holdings as list."""
        if self.top_holdings_json:
            return json.loads(self.top_holdings_json)
        return []

    @top_holdings.setter
    def top_holdings(self, value: List[Dict[str, Any]]):
        """Set top holdings from list."""
        self.top_holdings_json = json.dumps(value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert fund profile to dictionary."""
        return {
            'id': self.id,
            'fund_name': self.fund_name,
            'source': self.source,
            'fund_type': self.fund_type,
            'target_year': self.target_year,
            'risk_assessment': self.risk_assessment,
            'expense_ratio': self.expense_ratio,
            'asset_allocation': self.asset_allocation,
            'sector_breakdown': self.sector_breakdown,
            'top_holdings': self.top_holdings,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    def get_display_name(self) -> str:
        """Get a display-friendly name for the fund."""
        if self.target_year:
            return f"Target Date {self.target_year} Fund"
        return self.fund_name

    def __repr__(self) -> str:
        return f"FundProfile(id={self.id}, name='{self.fund_name}', source='{self.source}')"


# Create table if it doesn't exist
def init_fund_profiles_db():
    """Create fund_profiles table if it doesn't exist."""
    FundProfile.__table__.create(engine, checkfirst=True)


# CRUD operations
def save_fund_profile(
    fund_name: str,
    source: Optional[str] = None,
    fund_type: Optional[str] = None,
    target_year: Optional[int] = None,
    risk_assessment: Optional[str] = None,
    expense_ratio: Optional[float] = None,
    asset_allocation: Optional[Dict[str, float]] = None,
    sector_breakdown: Optional[Dict[str, float]] = None,
    top_holdings: Optional[List[Dict[str, Any]]] = None,
) -> FundProfile:
    """Save a new fund profile to the database."""
    db = SessionLocal()
    try:
        profile = FundProfile(
            fund_name=fund_name,
            source=source,
            fund_type=fund_type,
            target_year=target_year,
            risk_assessment=risk_assessment,
            expense_ratio=expense_ratio,
            asset_allocation_json=json.dumps(asset_allocation) if asset_allocation else None,
            sector_breakdown_json=json.dumps(sector_breakdown) if sector_breakdown else None,
            top_holdings_json=json.dumps(top_holdings) if top_holdings else None,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    finally:
        db.close()


def update_fund_profile(
    profile_id: int,
    **kwargs
) -> Optional[FundProfile]:
    """Update an existing fund profile."""
    db = SessionLocal()
    try:
        profile = db.query(FundProfile).filter(FundProfile.id == profile_id).first()
        if not profile:
            return None

        # Handle JSON fields specially
        if 'asset_allocation' in kwargs:
            kwargs['asset_allocation_json'] = json.dumps(kwargs.pop('asset_allocation'))
        if 'sector_breakdown' in kwargs:
            kwargs['sector_breakdown_json'] = json.dumps(kwargs.pop('sector_breakdown'))
        if 'top_holdings' in kwargs:
            kwargs['top_holdings_json'] = json.dumps(kwargs.pop('top_holdings'))

        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        db.commit()
        db.refresh(profile)
        return profile
    finally:
        db.close()


def get_all_fund_profiles() -> List[FundProfile]:
    """Get all fund profiles ordered by name."""
    db = SessionLocal()
    try:
        return db.query(FundProfile).order_by(FundProfile.fund_name.asc()).all()
    finally:
        db.close()


def get_fund_profile_by_id(profile_id: int) -> Optional[FundProfile]:
    """Get a specific fund profile by ID."""
    db = SessionLocal()
    try:
        return db.query(FundProfile).filter(FundProfile.id == profile_id).first()
    finally:
        db.close()


def get_fund_profile_by_name(fund_name: str, source: Optional[str] = None) -> Optional[FundProfile]:
    """Get a fund profile by name, optionally filtered by source."""
    db = SessionLocal()
    try:
        query = db.query(FundProfile).filter(FundProfile.fund_name == fund_name)
        if source:
            query = query.filter(FundProfile.source == source)
        return query.first()
    finally:
        db.close()


def find_matching_profile(fund_name: str, source: Optional[str] = None) -> Optional[FundProfile]:
    """
    Find a fund profile that matches the given fund name.

    Matching priority:
    1. Exact match with same source
    2. Exact match (any source)
    3. Fuzzy match (contains key terms)
    """
    db = SessionLocal()
    try:
        # 1. Exact match with source
        if source:
            profile = db.query(FundProfile).filter(
                FundProfile.fund_name == fund_name,
                FundProfile.source == source
            ).first()
            if profile:
                return profile

        # 2. Exact match (any source)
        profile = db.query(FundProfile).filter(
            FundProfile.fund_name == fund_name
        ).first()
        if profile:
            return profile

        # 3. Fuzzy match - look for target date funds by year
        import re
        year_match = re.search(r'(\d{4})', fund_name)
        if year_match and 'target' in fund_name.lower():
            target_year = int(year_match.group(1))
            profile = db.query(FundProfile).filter(
                FundProfile.target_year == target_year
            ).first()
            if profile:
                return profile

        return None
    finally:
        db.close()


def delete_fund_profile(profile_id: int) -> bool:
    """Delete a fund profile by ID. Returns True if deleted, False if not found."""
    db = SessionLocal()
    try:
        profile = db.query(FundProfile).filter(FundProfile.id == profile_id).first()
        if profile:
            db.delete(profile)
            db.commit()
            return True
        return False
    finally:
        db.close()


def get_fund_profiles_summary() -> List[Dict[str, Any]]:
    """Get a summary of all fund profiles for display."""
    db = SessionLocal()
    try:
        profiles = db.query(FundProfile).order_by(FundProfile.fund_name.asc()).all()
        return [
            {
                'id': p.id,
                'fund_name': p.fund_name,
                'source': p.source or 'Unknown',
                'fund_type': p.fund_type or 'Unknown',
                'target_year': p.target_year,
                'risk_assessment': p.risk_assessment or 'Unknown',
                'expense_ratio': p.expense_ratio,
                'num_allocations': len(p.asset_allocation) if p.asset_allocation else 0,
                'updated_at': p.updated_at.strftime('%Y-%m-%d'),
            }
            for p in profiles
        ]
    finally:
        db.close()
