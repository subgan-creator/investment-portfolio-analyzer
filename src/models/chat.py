"""
Chat message model for storing conversation history.

Uses SQLAlchemy ORM for database persistence with the existing SQLite database.
"""
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy import Column, Integer, String, DateTime, Text

# Import Base from existing snapshot model to share the same database
from src.models.snapshot import Base, engine, SessionLocal


class ChatMessage(Base):
    """Represents a chat message in a conversation."""

    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'created_at_formatted': self.created_at.strftime('%I:%M %p'),
        }

    def __repr__(self) -> str:
        return f"ChatMessage(id={self.id}, role='{self.role}', content='{self.content[:50]}...')"


# Create table if it doesn't exist
def init_chat_db():
    """Create chat_messages table if it doesn't exist."""
    ChatMessage.__table__.create(engine, checkfirst=True)


# CRUD operations
def save_message(session_id: str, role: str, content: str) -> ChatMessage:
    """Save a new chat message to the database."""
    db = SessionLocal()
    try:
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    finally:
        db.close()


def get_messages(session_id: str, limit: int = 50) -> List[ChatMessage]:
    """Get chat messages for a session, ordered by creation time."""
    db = SessionLocal()
    try:
        return db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .order_by(ChatMessage.created_at.asc())\
            .limit(limit)\
            .all()
    finally:
        db.close()


def get_messages_for_api(session_id: str, limit: int = 20) -> List[Dict[str, str]]:
    """Get messages formatted for OpenAI API (role + content only)."""
    messages = get_messages(session_id, limit)
    return [{"role": m.role, "content": m.content} for m in messages]


def clear_messages(session_id: str) -> int:
    """Clear all messages for a session. Returns count of deleted messages."""
    db = SessionLocal()
    try:
        count = db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .delete()
        db.commit()
        return count
    finally:
        db.close()


def get_message_count(session_id: str) -> int:
    """Get the number of messages in a session."""
    db = SessionLocal()
    try:
        return db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .count()
    finally:
        db.close()
