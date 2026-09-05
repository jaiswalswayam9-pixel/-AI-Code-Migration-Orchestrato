"""
Entry point for the AI Code Migration Orchestrator backend.

Phase 1 goal: prove the FastAPI app boots and exposes a health check.
Real routes (projects, migrations, agents, files, reports) get wired
in during later phases as their underlying services are implemented.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.database import init_db
from app.api.routes import projects, migrations, agents, files, reports

settings = get_settings()
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    init_db()
    yield


app = FastAPI(
    title="AI Code Migration Orchestrator",
    description="Autonomous multi-language code migration system (Java -> Python/TypeScript/Kotlin)",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(migrations.router)
app.include_router(agents.router)
app.include_router(files.router)
app.include_router(reports.router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ai-code-migration-orchestrator-backend",
        "environment": settings.environment,
    }
