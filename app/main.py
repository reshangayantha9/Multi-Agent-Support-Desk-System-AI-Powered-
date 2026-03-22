from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config.logging_config import setup_logging
from app.config.settings import get_settings
from app.db.database import init_db
from app.api import chat, triage, tickets

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

@asynccontextmanager
async def lifespan(_):
    logger.info("Initialising database…")
    await init_db()

    logger.info("Indexing KB…")
    try:
        from app.services.rag_service import index_kb
        count = await index_kb(settings.kb_docs_path)
        logger.info(f"KB indexed: {count} chunks ready")
    except Exception as e:
        logger.error(f"KB indexing failed (continuing anyway): {e}")

    yield
    logger.info("Shutting down…")

app = FastAPI(
    title="Multi-Agent Support Desk",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, tags=["Chat"])
app.include_router(triage.router, tags=["Triage"])
app.include_router(tickets.router, tags=["Tickets"])

@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)