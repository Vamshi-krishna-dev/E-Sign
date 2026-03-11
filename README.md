*Loan Agreement & E-Sign Module*
# Overview

This module manages the loan agreement signing workflow.

Main responsibilities:

Generate loan agreement PDFs

Initiate eSign with provider

Verify OTP

Handle provider callback

Store signed documents

Maintain audit logs for traceability

The module currently runs in DEV mode using a Mock eSign Provider.
Real provider integration will be completed once provider API documentation is available.

# Implemented Features
Agreement

Generate loan agreement PDF

Maintain agreement versioning

Generate SHA-256 hash for document integrity

Store agreement metadata in DB

Verify document integrity

# E-Sign Flow

Implemented using Mock Provider for development testing.

Flow:

Generate Agreement
       ↓
Initiate eSign
       ↓
OTP Sent
       ↓
OTP Verified
       ↓
Signed (Mock)
       ↓
Callback Received
       ↓
Signed Document Stored

# Features included:

eSign session tracking

OTP verification

Provider callback handling

Signed document storage

Audit logging

# Project Structure
app
│
├── api/routes
│   ├── agreement_router.py
│   └── esign_routers.py
│
├── core
│   ├── config.py
│   ├── exceptions.py
│   └── logger.py
│
├── db
│   ├── database.py
│   └── db_helper.py
│
├── models
│   ├── agreement.py
│   ├── esign_session.py
│   ├── signed_documents.py
│   └── audit_logs.py
│
├── pdf
│   ├── pdf_generator.py
│   
│
├── schemas
│   ├── agreement_schema.py
│   ├── callback_schema.py
│   └── esign_schema.py
│
├── services
│   ├── agreement_service.py
│   ├── esign_service.py
│   └── loan_client.py
│
├── provider
│   ├── base_provider.py
│   ├── mock_provider.py
│   ├── real_provider.py
│   ├── provider_client.py
│   └── factory.py
│
└── utils
    ├── response.py
    └── file_handler.py
    └── signature.py

# Important Components
AgreementService
Handles:
loan agreement generation
PDF creation
agreement versioning
hash verification

# EsignService
Manages the full eSign lifecycle:

initiate eSign
verify OTP
process callback
store signed document
record audit logs

# LoanClient
Responsible for communicating with the Loan Service API.

Purpose:
validate loan
fetch borrower details
ensure loan status is APPROVED before agreement generation

# Provider Layer
The provider layer allows the system to support multiple eSign providers.

# base_provider.py
Defines the interface that all providers must implement.
Purpose:
standardize provider communication
allow provider switching without changing service code

# mock_provider.py
Used for development testing.
Purpose:
simulate OTP sending
simulate signing
allow development without real provider

This file is allows local testing.Not for real Implement

# real_provider.py

Contains the integration layer for the actual eSign provider.

This file currently acts as a placeholder until provider API documentation is available.

# provider_client.py

Low-level HTTP client responsible for:

making API requests

handling timeouts

retry logic

provider authentication headers

Separates network logic from business logic.

# factory.py

Loads the correct provider dynamically.

Example:

DEV → mock_provider
PROD → real_provider

This allows switching providers without modifying service code.

# Database Tables
--> agreements

Stores agreement metadata and file hash.

--> esign_sessions

Tracks the lifecycle of each eSign transaction.

Purpose:
track OTP state
store provider responses
maintain signing status

--> signed_documents

Stores the final signed agreement file.

--> esign_audit_logs

Stores all events during the signing process.

Purpose:
debugging
traceability
compliance logging

# API Endpoints

Generate Agreement

POST /api/v1/loan/agreement/{loan_id}

Initiate eSign

POST /api/v1/loan/esign/initiate

Verify OTP

POST /api/v1/loan/esign/verify

Provider Callback

POST /api/v1/loan/esign/callback

# Pending Work (Provider Integration)

These items require actual provider API documentation.

# Signed PDF Download

Provider will return a URL:
signed_pdf_url

Required work:
download signed PDF
store in storage/signed_pdfs
generate SHA-256 hash

# Agreement Status Update

After storing signed PDF:

Agreement.status → SIGNED

# Callback Signature Validation
Real provider callback must verify signature using:
X-Signature header

# Loan Service Integration
LoanClient will be updated once Loan Service API authentication and response structure are finalized.

Notes

user_id is currently hardcoded for development.

Mock provider is intentionally retained for testing.

Static file serving is used only for local development.

Production environments typically store documents in external storage.

PDF generation currently implemented for DEV testing.
In production, agreement PDFs will be fetched from the external document service.

# Final Status

The Loan Agreement & E-Sign module is functionally complete in development mode.

All infrastructure required for production integration is already implemented, including:

database schema

provider abstraction

audit logging

callback handling

document storage logic


