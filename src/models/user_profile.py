"""
User Profile model for storing onboarding data and user preferences.

Stores investment objectives, risk tolerance, and other profile information
collected during onboarding. Used to personalize AI advisor recommendations.
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text

# Import shared database components
try:
    from src.models.snapshot import Base, engine, SessionLocal
except ImportError:
    from models.snapshot import Base, engine, SessionLocal


class UserProfile(Base):
    """Represents a user's investment profile and preferences."""

    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True)
    session_id = Column(String(50), unique=True, index=True, nullable=False)

    # Basic info
    name = Column(String(100), nullable=True)

    # Investment accounts (JSON array: ["401k", "roth_ira", "taxable"])
    account_types = Column(Text, nullable=True)

    # Brokerages used (JSON array: ["fidelity", "vanguard"])
    brokerages = Column(Text, nullable=True)

    # Portfolio size range
    portfolio_size_range = Column(String(50), nullable=True)

    # Goals & Strategy
    primary_goal = Column(String(50), nullable=True)
    time_horizon = Column(String(50), nullable=True)
    risk_tolerance = Column(String(50), nullable=True)

    # Age / Retirement
    age = Column(Integer, nullable=True)
    target_retirement_year = Column(Integer, nullable=True)

    # Tax info (optional)
    filing_status = Column(String(50), nullable=True)
    state = Column(String(2), nullable=True)

    # Onboarding state
    onboarding_completed = Column(Boolean, default=False)
    current_step = Column(Integer, default=1)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for templates and API."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'name': self.name,
            'account_types': json.loads(self.account_types) if self.account_types else [],
            'brokerages': json.loads(self.brokerages) if self.brokerages else [],
            'portfolio_size_range': self.portfolio_size_range,
            'primary_goal': self.primary_goal,
            'time_horizon': self.time_horizon,
            'risk_tolerance': self.risk_tolerance,
            'age': self.age,
            'target_retirement_year': self.target_retirement_year,
            'filing_status': self.filing_status,
            'state': self.state,
            'onboarding_completed': self.onboarding_completed,
            'current_step': self.current_step,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_ai_context(self) -> str:
        """Format profile for AI advisor system prompt."""
        parts = []

        if self.name:
            parts.append(f"- Name: {self.name}")

        if self.risk_tolerance:
            risk_labels = {
                'conservative': 'Conservative (prefers stability)',
                'moderate': 'Moderate (balanced approach)',
                'aggressive': 'Aggressive (maximizes growth)'
            }
            parts.append(f"- Risk Tolerance: {risk_labels.get(self.risk_tolerance, self.risk_tolerance)}")

        if self.primary_goal:
            goal_labels = {
                'retirement': 'Retirement savings',
                'growth': 'Wealth growth',
                'income': 'Income generation',
                'preservation': 'Capital preservation',
                'purchase': 'Saving for a major purchase'
            }
            parts.append(f"- Primary Goal: {goal_labels.get(self.primary_goal, self.primary_goal)}")

        if self.time_horizon:
            horizon_labels = {
                'short': 'Short-term (1-3 years)',
                'medium': 'Medium-term (3-7 years)',
                'long': 'Long-term (7-15 years)',
                'very_long': 'Very long-term (15+ years)'
            }
            parts.append(f"- Time Horizon: {horizon_labels.get(self.time_horizon, self.time_horizon)}")

        if self.age:
            parts.append(f"- Age: {self.age}")

        if self.target_retirement_year:
            parts.append(f"- Target Retirement Year: {self.target_retirement_year}")

        if self.portfolio_size_range:
            parts.append(f"- Portfolio Size: {self.portfolio_size_range}")

        account_types = json.loads(self.account_types) if self.account_types else []
        if account_types:
            parts.append(f"- Account Types: {', '.join(account_types)}")

        if self.filing_status:
            parts.append(f"- Tax Filing Status: {self.filing_status}")

        if self.state:
            parts.append(f"- State: {self.state}")

        if not parts:
            return ""

        return "USER PROFILE:\n" + "\n".join(parts)

    def __repr__(self):
        return f"<UserProfile(id={self.id}, session_id='{self.session_id}', name='{self.name}')>"


def init_user_profile_db():
    """Create the user_profiles table if it doesn't exist."""
    UserProfile.__table__.create(engine, checkfirst=True)


def get_or_create_profile(session_id: str) -> UserProfile:
    """Get existing profile or create a new one for the session."""
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.session_id == session_id).first()
        if not profile:
            profile = UserProfile(session_id=session_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile
    finally:
        db.close()


def get_profile(session_id: str) -> Optional[UserProfile]:
    """Get profile for a session, returns None if not found."""
    db = SessionLocal()
    try:
        return db.query(UserProfile).filter(UserProfile.session_id == session_id).first()
    finally:
        db.close()


def update_profile(session_id: str, **kwargs) -> Optional[UserProfile]:
    """Update profile fields for a session."""
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.session_id == session_id).first()
        if not profile:
            return None

        # Handle JSON fields
        if 'account_types' in kwargs and isinstance(kwargs['account_types'], list):
            kwargs['account_types'] = json.dumps(kwargs['account_types'])
        if 'brokerages' in kwargs and isinstance(kwargs['brokerages'], list):
            kwargs['brokerages'] = json.dumps(kwargs['brokerages'])

        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)
        return profile
    finally:
        db.close()


def is_onboarding_complete(session_id: str) -> bool:
    """Check if user has completed onboarding."""
    profile = get_profile(session_id)
    return profile is not None and profile.onboarding_completed


def mark_onboarding_complete(session_id: str) -> Optional[UserProfile]:
    """Mark onboarding as complete for a session."""
    return update_profile(session_id, onboarding_completed=True, current_step=11)


def get_profile_for_ai(session_id: str) -> Dict[str, Any]:
    """Get profile data formatted for AI advisor context."""
    profile = get_profile(session_id)
    if not profile:
        return {}
    return profile.to_dict()


def get_profile_ai_context(session_id: str) -> str:
    """Get profile formatted as text for AI system prompt."""
    profile = get_profile(session_id)
    if not profile:
        return ""
    return profile.to_ai_context()
