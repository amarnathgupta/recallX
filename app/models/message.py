from app.db.base import Base
from sqlalchemy import Column, String, ForeignKey, DateTime, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

import uuid
from datetime import datetime, timezone
import enum

class RoleEnum(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role = Column(Enum(RoleEnum), nullable=False)
    content = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=True
    )

    # 🔗 relationship
    user = relationship("User", back_populates="messages")