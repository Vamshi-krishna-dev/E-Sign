from fastapi import FastAPI

from app.core.config import settings
from app.core.exceptions import register_exception_handlers

from app.api.routes.agreement_router import router as agreement_router
from app.api.routes.esign_routers import router as esign_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Loan Service Provider - Backend API",
        version="1.0.0"
    )

    # Include routers
    app.include_router(agreement_router)
    app.include_router(esign_router)

    # Register global exception handlers
    register_exception_handlers(app)

    # Health check
    @app.get("/")
    def home():
        return {"status": "running"}

    return app

app = create_app()

