"""
Project persistence -- backed by Postgres via SQLAlchemy.
"""
from sqlalchemy.orm import Session
from app.db.models import Project


def create_project(db: Session, name: str, workspace_path: str | None = None) -> Project:
    project = Project(name=name, status="uploaded", workspace_path=workspace_path)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def save_analysis(db: Session, project: Project, analysis: dict) -> Project:
    project.analysis = analysis
    project.file_count = analysis.get("file_count", 0)
    project.status = "analyzed"
    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: str) -> Project | None:
    return db.get(Project, project_id)


def list_projects(db: Session) -> list[Project]:
    return db.query(Project).order_by(Project.uploaded_at.desc()).all()
