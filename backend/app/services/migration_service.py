"""
Migration job persistence -- backed by Postgres via SQLAlchemy as of Phase 4.
Agent events, errors, and file changes are now real related tables
(AgentRun, MigrationErrorRow, FileChange) instead of JSON blobs in a dict,
so later phases (Agent Activity Log, Error Analyzer, Diff Viewer) can query
them directly instead of parsing an in-memory structure.
"""
from sqlalchemy.orm import Session
from app.db.models import MigrationJob

DEFAULT_PROGRESS = {
    "analyzer": False, "planner": False, "translator": False,
    "refactoring": False, "build": False, "repair": False,
    "testing": False, "validation": False,
}


def start_migration(db: Session, project_id: str, target_language: str, mode: str) -> MigrationJob:
    job = MigrationJob(
        project_id=project_id,
        target_language=target_language,
        mode=mode,
        status="pending",
        progress=dict(DEFAULT_PROGRESS),
        human_approval_required=(mode == "suggest"),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_migration(db: Session, migration_id: str) -> MigrationJob | None:
    return db.get(MigrationJob, migration_id)


def approve_migration(db: Session, job: MigrationJob) -> MigrationJob:
    job.human_approval_required = False
    db.commit()
    db.refresh(job)
    return job


def cancel_migration(db: Session, job: MigrationJob) -> MigrationJob:
    job.status = "failed"
    db.commit()
    db.refresh(job)
    return job
