from fastapi import FastAPI

from db.database import Base
from db.database import engine

from core.config import settings
from core.exceptions import register_exception_handlers

from routes.agreement_router import router as agreement_router
from routes.esign_routers import router as esign_router
from routes.disbursement_router import router as disbursement_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Loan Service Provider - Backend API",
        version="1.0.0"
    )
    Base.metadata.create_all(bind=engine)

    # Include routers
    app.include_router(agreement_router)
    app.include_router(esign_router)
    app.include_router(disbursement_router)

    # Register global exception handlers
    register_exception_handlers(app)

    # Health check
    @app.get("/")
    def home():
        return {"status": "running"}

    return app

app = create_app()

