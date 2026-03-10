from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey,Boolean, Enum as SqlEnum
from app.db.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


# SIGNED DOCUMENT
class SignedDocument(Base):
    __tablename__ = "signed_documents"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(Integer, ForeignKey("esign_sessions.id"), unique=True, nullable=False)
    agreement_id = Column(Integer, ForeignKey("agreements.id"), nullable=True)

    signed_pdf_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)

    signed_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("EsignSession", back_populates="signed_document")