from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logger import logger
from app.core.exceptions import register_exception_handlers

from app.db.database import Base, engine
from app.api.routes.agreement_router import router as agreement_router
from app.api.routes.esign_routers import router as esign_router
#from app.api.routes.disbursement_router import router as disbursement_router
import os


def create_app() -> FastAPI:
    app = FastAPI(
        title="Loan Service Provider - Backend API",
        version="1.0.0"
    )

    # DB INIT
    Base.metadata.create_all(bind=engine)

    # ---- ROUTERS ----
    app.include_router(agreement_router)
    app.include_router(esign_router)
    

    # STATIC FILES
    app.mount(
        "/files",
        StaticFiles(directory=settings.AGREEMENT_STORAGE_PATH),
        name="files"
    )

    # GLOBAL EXCEPTIONS
    register_exception_handlers(app)

    # HEALTH CHECK
    @app.get("/")
    def home():
        return {"status": "running", "service": "LSP Backend"}

    return app


os.makedirs(settings.AGREEMENT_STORAGE_PATH, exist_ok=True)
os.makedirs(settings.SIGNED_PDF_PATH, exist_ok=True)

app = create_app()

