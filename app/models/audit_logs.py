from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey,Boolean, Enum as SqlEnum
from app.db.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class EsignAuditLog(Base):
    __tablename__ = "esign_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("esign_sessions.id"), nullable=False, index=True)

    event_type = Column(String, nullable=False)
    event_description = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("EsignSession", back_populates="audit_logs")