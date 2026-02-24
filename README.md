**Module Overview**

This service handles the Loan Agreement PDF generation, E-Sign initiation, OTP verification, provider callback, and disbursement tracking.
The module is fully functional in DEV mode using a Mock eSign Provider.

**Completed Features (DEV Mode)**
<Agreement Module>

Generate loan agreement PDF

Versioning support

SHA-256 hashing

Store agreement entry in DB

Verify agreement integrity

<E-Sign Flow (Mock)>

Initiate e-sign (OTP sent)

Verify OTP (Signed – mock mode)

Store eSign session

Audit logs for each transition

Callback endpoint (DEV mode auto-accepts)

Correlation-ID middleware

<Disbursement Module>

Check disbursement status (mock)

Confirm disbursement

Create disbursement record

Idempotency built-in

**Project Folder Structure**
app/
 ├── api/
 │    └── routes/
 │         ├── agreement_router.py
 │         ├── esign_routers.py
 │         └── disbursement_router.py
 │
 ├── core/
 │    ├── config.py
 │    ├── exceptions.py
 │    └── logger.py
 │
 ├── db/
 │    ├── database.py
 │    └── db_helper.py
 │
 ├── middleware/
 │    ├── request_logger.py
 │    └── correlation_id.py
 │
 ├── models/
 │    └── models.py
 │
 ├── pdf/
 │    ├── pdf_generator.py
 │    └── signature.py
 │
 ├── schemas/
 │    ├── agreement_schema.py
 │    ├── callback_schema.py
 │    ├── disbursement_schema.py
 │    ├── esign_schema.py
 │    └── loan_schema.py
 │
 ├── services/
 │    ├── agreement_service.py
 │    ├── esign_service.py
 │    ├── disbursement_service.py
 │    └── loan_client.py
 │
 ├── services/provider/
 │    ├── base_provider.py
 │    ├── mock_esign_provider.py
 │    ├── real_esign_provider.py   (Shell only)
 │    ├── provider_client.py
 │    └── factory.py
 │
 └── utils/
      ├── response.py
      ├── file_handler.py
      └── logger.py

 **Environment Variables (.env)**
# ENVIRONMENT
ENV=DEV
APP_BASE_URL=http://localhost:8000

# DATABASE
DATABASE_URL=postgresql://postgres:password@localhost:5432/esign

# STORAGE PATHS
AGREEMENT_STORAGE_PATH=storage/generated_pdfs
SIGNED_PDF_PATH=storage/signed_pdfs

# ESIGN PROVIDER (Mock or Real)
ESIGN_PROVIDER=eMudhra
ESIGN_BASE_URL=https://api.your-esign-provider.com/v1
ESIGN_API_KEY=your_provider_key
ESIGN_CLIENT_SECRET=your_provider_secret

# LOAN SERVICE (External)
LOAN_SERVICE_BASE_URL=http://loan-service/api/v1/loans

# CALLBACK
ESIGN_CALLBACK_SECRET=REPLACE_WITH_32_CHAR_RANDOM_KEY
CALLBACK_URL=${APP_BASE_URL}/api/v1/loan/esign/callback

**API Overview**
1. Generate Agreement
--> POST /api/v1/loan/agreement/{loan_id}

2. Initiate e-Sign (Send OTP)
--> POST /api/v1/loan/esign/initiate

3. Verify e-Sign (Submit OTP)
--> POST /api/v1/loan/esign/verify

4. Provider Callback (POST-only, secure)
--> POST /api/v1/loan/esign/callback
Headers:
   X-Signature: <HMAC signature>
Body:
{
  "transaction_id": "string",
  "loan_id": 0,
  "status": "string",
  "signed_pdf_url": "string",
  "provider_signature_id": "string",
  "timestamp": "2026-02-24T03:38:02.373Z"
}

5. Disbursement – Status
--> GET /api/v1/loan/disbursement/{loan_id}/status

6. Disbursement – Confirm
--> POST /api/v1/loan/disbursement/confirm


**Pending Work (Real Provider)**

These items cannot be completed until the real provider API is known.

<Download Signed PDF (Real Mode)>

Currently mock returns "LOCAL"
Real provider might return a URL like:

signed_pdf_url: "https://...../signed-document.pdf"

Pending:

Auth headers

Token mechanism

Download logic

Save to storage/signed_pdfs/

Hash real PDF

<Save Signed Document Record>

Table exists:

signed_documents

Pending real implementation:

session_id

agreement_id mapping

PDF path

file hash

<Update Agreement Status = SIGNED>

To be done only when:

Signed PDF downloaded

Hash is validated

Callback status = SIGNED

<Callback Signature Validation (Real Mode)>

Mock provider bypasses signature.
Pending:

Real signature algorithm

Real secret key

Validation mechanism

<Loan Application Module Integration>

LoanClient currently uses mock data.
Pending:

Real loan-service API

Auth validation

User ownership check


📌 Notes

When loan module integrates, remove dummy user_id=1.

Module is fully functional in DEV/mock mode

Real provider integration deliberately left incomplete (requires API specs)

All tables, schema, endpoints, middleware, logging, and base architecture are ready

Code uses dependency injection & is production-safe

**Final Developer Statement**

“E-Sign Module is fully completed in DEV mode and ready for real provider integration.
All pending items require actual e-Sign provider documentation and loan-service integration.


