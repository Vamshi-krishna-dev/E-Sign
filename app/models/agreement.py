from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey,Boolean, Enum as SqlEnum
from app.db.database import Base
from sqlalchemy.sql import func
from enum import Enum

class AgreementStatus(str, Enum):
    GENERATED = "GENERATED"
    SIGNED = "SIGNED"
    COMPLETED = "COMPLETED"

class Agreement(Base):
    __tablename__ = "agreements"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    version = Column(Integer, default=1)

    is_active = Column(Boolean, default=True, index=True)

    status = Column(SqlEnum(AgreementStatus), default=AgreementStatus.GENERATED)

    agreement_pdf_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)

    provider = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
