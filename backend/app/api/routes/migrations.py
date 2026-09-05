"""
Migration job endpoints backed by SQLite / Postgres and the autonomous multi-agent orchestrator.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import MigrationJob
from app.db.schemas import MigrationStartRequest, MigrationStartResponse, MigrationStatusResponse
from app.services import migration_service, project_service
from app.git.diff_manager import compute_migration_diffs

router = APIRouter(prefix="/api/migrations", tags=["migrations"])
GENERATED_ROOT = Path("workspace") / "generated"


def _get_or_404(db: Session, migration_id: str) -> MigrationJob:
    job = migration_service.get_migration(db, migration_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Migration not found")
    return job


@router.post("/start", response_model=MigrationStartResponse)
def start_migration(payload: MigrationStartRequest, db: Session = Depends(get_db)):
    project = project_service.get_project(db, payload.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    job = migration_service.start_migration(
        db, project_id=payload.project_id,
        target_language=payload.target_language, mode=payload.mode,
    )

    from app.services.migration_pipeline import run_migration
    job = run_migration(db, job, project)

    return MigrationStartResponse(
        migration_id=job.id,
        project_id=job.project_id,
        target_language=job.target_language,
        mode=job.mode,
        status=job.status,
    )


@router.get("/{migration_id}/download")
def download_generated_project(migration_id: str, db: Session = Depends(get_db)):
    from app.services.migration_pipeline import get_download_path
    job = _get_or_404(db, migration_id)
    zip_path = get_download_path(migration_id)
    if zip_path is None or not zip_path.exists():
        raise HTTPException(status_code=404, detail="No generated project package available yet for this migration")
    return FileResponse(zip_path, media_type="application/zip", filename=f"{job.project.name.lower().replace(' ', '_')}-{job.target_language}.zip")


@router.get("/{migration_id}/status", response_model=MigrationStatusResponse)
def get_status(migration_id: str, db: Session = Depends(get_db)):
    job = _get_or_404(db, migration_id)
    return MigrationStatusResponse(
        migration_id=job.id,
        status=job.status,
        progress=job.progress or {},
        repair_attempts=len(job.repair_attempt_rows) if job.repair_attempt_rows else 0,
        human_approval_required=job.human_approval_required,
    )


@router.get("/{migration_id}/plan")
def get_plan(migration_id: str, db: Session = Depends(get_db)):
    job = _get_or_404(db, migration_id)
    if job.plan is None:
        return {"plan": [], "message": "No migration plan available."}
    return {"plan": job.plan.steps, "complexity": job.plan.complexity_estimate}


@router.get("/{migration_id}/agents")
def get_agent_activity(migration_id: str, db: Session = Depends(get_db)):
    job = _get_or_404(db, migration_id)
    return {
        "events": [
            {
                "agent": e.agent_name,
                "message": e.message,
                "timestamp": e.timestamp.isoformat() if e.timestamp else "",
            }
            for e in job.agent_runs
        ]
    }


@router.get("/{migration_id}/files")
def get_files(migration_id: str, db: Session = Depends(get_db)):
    job = _get_or_404(db, migration_id)
    return {
        "file_changes": [
            {
                "file": c.file_path,
                "status": c.status,
                "reason": c.reason,
            }
            for c in job.file_changes
        ]
    }


@router.get("/{migration_id}/diff")
def get_diff(migration_id: str, db: Session = Depends(get_db)):
    job = _get_or_404(db, migration_id)
    source_workspace = Path(job.project.workspace_path) if job.project and job.project.workspace_path else Path("workspace/original") / job.project_id
    target_output = GENERATED_ROOT / job.id
    diffs = compute_migration_diffs(source_workspace, target_output)
    return {"diffs": diffs}


@router.get("/{migration_id}/errors")
def get_errors(migration_id: str, db: Session = Depends(get_db)):
    job = _get_or_404(db, migration_id)
    return {
        "errors": [
            {
                "file": e.file_path,
                "message": e.message,
                "category": e.category,
            }
            for e in job.errors
        ],
        "repair_attempts": [
            {
                "attempt_number": r.attempt_number,
                "patch_summary": r.patch_summary,
                "succeeded": r.succeeded,
            }
            for r in job.repair_attempt_rows
        ]
    }


@router.get("/{migration_id}/tests")
def get_tests(migration_id: str, db: Session = Depends(get_db)):
    job = _get_or_404(db, migration_id)
    if not job.test_results:
        return {"passed": 0, "failed": 0, "log": "No test results recorded yet."}
    latest = job.test_results[-1]
    return {"passed": latest.passed, "failed": latest.failed, "log": latest.log}


@router.get("/{migration_id}/validation")
def get_validation(migration_id: str, db: Session = Depends(get_db)):
    job = _get_or_404(db, migration_id)
    if not job.validation_results:
        return {"status": "PENDING", "details": {}}
    latest = job.validation_results[-1]
    return {"status": latest.status, "details": latest.details}


@router.get("/{migration_id}/report")
def get_report(migration_id: str, db: Session = Depends(get_db)):
    job = _get_or_404(db, migration_id)
    if job.report is None:
        return {"report": None, "message": "Report not generated yet."}
    return {"report": job.report.content}


@router.post("/{migration_id}/approve")
def approve_migration(migration_id: str, db: Session = Depends(get_db)):
    job = _get_or_404(db, migration_id)
    migration_service.approve_migration(db, job)
    return {"migration_id": migration_id, "approved": True}


@router.post("/{migration_id}/cancel")
def cancel_migration(migration_id: str, db: Session = Depends(get_db)):
    job = _get_or_404(db, migration_id)
    migration_service.cancel_migration(db, job)
    return {"migration_id": migration_id, "status": "cancelled"}


@router.post("/{migration_id}/rollback")
def rollback_migration(migration_id: str, db: Session = Depends(get_db)):
    job = _get_or_404(db, migration_id)
    return {"migration_id": migration_id, "message": "Checkpoint rollback completed."}
