<<<<<<< HEAD
# -AI-Code-Migration-Orchestrato
=======
# Autonomous AI Workflow Orchestrator for Multi-Language Software Code Migration

Migrates Java projects to Python, TypeScript, or Kotlin via a deterministic
Intermediate-Representation pipeline, AI-assisted translation, autonomous
build/test/repair loop, and human-in-the-loop validation.

**Status:** Phase 1 (repository setup) complete. See `docs/architecture.md`.

## Quick start (Phase 1 — backend health check only)

    cd backend
    python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload

    curl http://localhost:8000/health

## Structure

- `backend/` — FastAPI + LangGraph orchestrator, agents, parsers, IR, generators
- `frontend/` — React + TypeScript dashboard
- `migration_rules/` — deterministic Java -> {Python,TypeScript,Kotlin} rule tables
- `sample_projects/` — Java test fixtures for evaluation
- `docs/` — architecture, agent design, API, migration rules, evaluation

## Supported migration paths (Phase 1 scope)

Java -> Python (primary vertical slice, built first)
Java -> Kotlin
Java -> TypeScript

Framework migration (e.g. Spring Boot -> FastAPI) is scoped to a small,
explicit compatibility matrix — see `docs/migration_rules.md`. This is an
academic prototype: it does not claim 100% automatic conversion of all
Java applications.
>>>>>>> 61c32ba (Initial commit: AI Code Migration Orchestrator (Frontend, Backend, AST/IR Agents, Sample Projects))
