from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.models import HealthResponse
from app.routers import translate, dictionary
from app.services.llm_client import llm_client


# Create FastAPI app
app = FastAPI(
    title="Tabasaran-Russian Translator",
    description="API для перевода между табасаранским и русским языками",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(translate.router, prefix=settings.API_PREFIX)
app.include_router(dictionary.router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()
    print(f"Database initialized at {settings.DATABASE_PATH}")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "name": "Tabasaran-Russian Translator API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check health of all services"""
    # Check database
    db_ok = settings.DATABASE_PATH.exists()

    # Check vector store (ChromaDB)
    vector_ok = settings.CHROMA_PATH.exists()

    # Check LLM server
    llm_ok = await llm_client.is_available()

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        database=db_ok,
        vector_store=vector_ok,
        llm_server=llm_ok
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
