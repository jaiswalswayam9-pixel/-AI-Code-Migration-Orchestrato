"""
Autonomous Migration Pipeline Orchestrator.

Coordinates the end-to-end multi-agent migration execution:
AST Parse -> IR Build -> Architecture -> Planner -> Dependency Mapping ->
Target Generation -> Test Generation -> Autonomous Build & Repair ->
Validation -> Final Report & Packaging.
"""
import shutil
import zipfile
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.db.models import (
    MigrationJob, Project, AgentRun, FileChange,
    MigrationPlan, MigrationErrorRow, RepairAttempt,
    TestResult, ValidationResult, Report
)
from app.orchestrator.workflow import execute_migration_workflow
from app.orchestrator.events import AgentEvent

GENERATED_ROOT = Path("workspace") / "generated"


def run_migration(db: Session, job: MigrationJob, project: Project) -> MigrationJob:
    if not project.workspace_path:
        job.status = "failed"
        db.commit()
        return job

    job.status = "running"
    db.commit()

    workspace = Path(project.workspace_path)
    output_dir = GENERATED_ROOT / job.id
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    progress = dict(job.progress or {})

    def handle_event(event: AgentEvent):
        run_record = AgentRun(
            migration_job_id=job.id,
            agent_name=event.agent_name,
            message=event.message,
        )
        db.add(run_record)
        progress[event.stage] = True
        job.progress = dict(progress)
        db.commit()

    try:
        results = execute_migration_workflow(
            workspace_path=workspace,
            output_dir=output_dir,
            project_name=project.name,
            target_language=job.target_language,
            mode=job.mode,
            event_callback=handle_event,
        )
    except Exception as e:
        job.status = "failed"
        db.add(AgentRun(
            migration_job_id=job.id,
            agent_name="orchestrator",
            message=f"Pipeline error: {str(e)}",
        ))
        db.commit()
        return job

    # 1. Save Plan
    plan_data = results.get("plan", {})
    plan_record = MigrationPlan(
        migration_job_id=job.id,
        steps=plan_data.get("steps", []),
        complexity_estimate=plan_data.get("complexity_estimate", "Low"),
    )
    db.add(plan_record)

    # 2. Save File Changes
    for fc in results.get("file_changes", []):
        change_record = FileChange(
            migration_job_id=job.id,
            file_path=fc["file_path"],
            status=fc.get("status", "success"),
            reason=fc.get("reason"),
            agent="translator",
        )
        db.add(change_record)

    # 3. Save Repair Attempts & Errors
    for rep in results.get("repair_attempts", []):
        err_record = MigrationErrorRow(
            migration_job_id=job.id,
            file_path=rep.get("file_path", "unknown"),
            message=rep.get("error", ""),
            category=rep.get("category", "syntax_error"),
        )
        db.add(err_record)
        db.flush()

        rep_record = RepairAttempt(
            migration_job_id=job.id,
            error_id=err_record.id,
            attempt_number=rep.get("attempt_number", 1),
            patch_summary=rep.get("patch_summary"),
            succeeded=rep.get("succeeded", True),
        )
        db.add(rep_record)

    # 4. Save Test Results
    test_data = results.get("test_results", {})
    test_record = TestResult(
        migration_job_id=job.id,
        passed=test_data.get("passed", 0),
        failed=test_data.get("failed", 0),
        log=test_data.get("output"),
    )
    db.add(test_record)

    # 5. Save Validation Result
    val_data = results.get("validation", {})
    val_record = ValidationResult(
        migration_job_id=job.id,
        status=val_data.get("status", "SUCCESS"),
        details=val_data,
    )
    db.add(val_record)

    # 6. Save Report
    report_data = results.get("report", {})
    rep_record = Report(
        migration_job_id=job.id,
        content=report_data,
    )
    db.add(rep_record)

    # Set final job status
    validation_status = val_data.get("status", "SUCCESS")
    if validation_status == "SUCCESS":
        job.status = "success"
    elif validation_status == "PARTIAL":
        job.status = "partial"
    else:
        job.status = "failed"

    # Zip target package for download
    zip_path = GENERATED_ROOT / f"{job.id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in output_dir.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(output_dir))

    db.commit()
    db.refresh(job)
    return job


def get_download_path(migration_id: str) -> Path | None:
    zip_path = GENERATED_ROOT / f"{migration_id}.zip"
    return zip_path if zip_path.exists() else None
