"""
Integration tests for the full Multi-Agent Orchestrator Pipeline.
"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, Project, MigrationJob
from app.services.migration_pipeline import run_migration
from app.agents.analyzer_agent import analyze_project

SAMPLE_CALCULATOR_DIR = Path(__file__).parents[3] / "sample_projects" / "basic_calculator"
SAMPLE_EMPLOYEE_DIR = Path(__file__).parents[3] / "sample_projects" / "employee_management"


def test_full_pipeline_calculator_to_python(tmp_path):
    # Setup in-memory sqlite session
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # Create project and job
    analysis = analyze_project(SAMPLE_CALCULATOR_DIR)
    project = Project(
        id="test-calc-proj",
        name="Basic Calculator",
        file_count=analysis["file_count"],
        workspace_path=str(SAMPLE_CALCULATOR_DIR),
        analysis=analysis,
    )
    db.add(project)
    db.commit()

    job = MigrationJob(
        id="test-calc-mig-py",
        project_id=project.id,
        target_language="python",
        mode="autonomous",
        status="pending",
    )
    db.add(job)
    db.commit()

    # Run full orchestrator pipeline
    result_job = run_migration(db, job, project)

    assert result_job.status in ("success", "partial")
    assert len(result_job.agent_runs) >= 5
    assert len(result_job.file_changes) >= 1
    assert result_job.plan is not None
    assert result_job.report is not None
    assert result_job.validation_results is not None
    assert len(result_job.validation_results) > 0


def test_full_pipeline_employee_to_typescript(tmp_path):
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    analysis = analyze_project(SAMPLE_EMPLOYEE_DIR)
    project = Project(
        id="test-emp-proj",
        name="Employee Management",
        file_count=analysis["file_count"],
        workspace_path=str(SAMPLE_EMPLOYEE_DIR),
        analysis=analysis,
    )
    db.add(project)
    db.commit()

    job = MigrationJob(
        id="test-emp-mig-ts",
        project_id=project.id,
        target_language="typescript",
        mode="autonomous",
        status="pending",
    )
    db.add(job)
    db.commit()

    result_job = run_migration(db, job, project)

    assert result_job.status in ("success", "partial")
    assert len(result_job.file_changes) >= 4
    assert result_job.report is not None
