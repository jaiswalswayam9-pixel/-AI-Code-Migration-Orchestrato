"""
Final migration report retrieval endpoints (JSON and Markdown).
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services import migration_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{migration_id}")
def get_report(migration_id: str, db: Session = Depends(get_db)):
    job = migration_service.get_migration(db, migration_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Migration not found")
    if job.report is None:
        return {"report": None, "message": "Report not generated yet."}
    return {"report": job.report.content}


@router.get("/{migration_id}/markdown", response_class=PlainTextResponse)
def get_report_markdown(migration_id: str, db: Session = Depends(get_db)):
    job = migration_service.get_migration(db, migration_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Migration not found")
    if job.report is None or not job.report.content:
        return "# Migration Report\n\nNo report generated yet."
    return job.report.content.get("markdown", "# Migration Report\n\nNo markdown available.")
