"""SymptomLog ORM model."""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class SymptomLog(Base):
    __tablename__ = "symptom_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    symptoms: Mapped[dict] = mapped_column(JSON)     # ["karın ağrısı", "ateş"]
    result: Mapped[dict] = mapped_column(JSON)        # analiz sonucu
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="symptom_logs")

    def __repr__(self):
        return f"<SymptomLog user={self.user_id} at {self.created_at}>"
