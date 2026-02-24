from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey,Boolean, Enum as SqlEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
from enum import Enum

# ENUMS
class EsignStatus(str, Enum):
    OTP_SENT = "OTP_SENT"
    OTP_FAILED = "OTP_FAILED"
    SIGNED = "SIGNED"
    FAILED = "FAILED"
    CALLBACK_RECEIVED = "CALLBACK_RECEIVED"


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


class EsignSession(Base):
    __tablename__ = "esign_sessions"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)

    transaction_id = Column(String, unique=True, nullable=False, index=True)

    request_payload = Column(JSON, nullable=False)
    response_payload = Column(JSON, nullable=False)
    callback_payload = Column(JSON, nullable=True)

    status = Column(SqlEnum(EsignStatus), default=EsignStatus.OTP_SENT, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    signed_document = relationship("SignedDocument", back_populates="session", uselist=False)
    audit_logs = relationship("EsignAuditLog", back_populates="session")


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

class EsignAuditLog(Base):
    __tablename__ = "esign_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("esign_sessions.id"), nullable=False, index=True)

    event_type = Column(String, nullable=False)
    event_description = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("EsignSession", back_populates="audit_logs")

# DISBURSEMENT RECORD
class DisbursementRecord(Base):
    __tablename__ = "disbursement_records"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, index=True, nullable=False, unique=True)
    user_id = Column(Integer, index=True, nullable=False)

    utr_number = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)
    remarks = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    disbursed_at = Column(DateTime(timezone=True), nullable=True)

    