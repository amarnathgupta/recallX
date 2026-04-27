from app.db.base import Base
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
import enum


class MemoryTypeEnum(str, enum.Enum):
    FACT = "fact"
    PREFERENCE  = "preference"
    EPISODE = "episode"

class Memory(Base):
    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(String, nullable=False)
    memory_type = Column(Enum(MemoryTypeEnum), nullable=False, index=True)
    importance_score = Column(Float, default=0.5, nullable=False)
    vector_id = Column(String, unique=True)

    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("User", back_populates="memories")