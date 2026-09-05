"""
Project upload/listing/sample endpoints.
"""
import shutil
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.schemas import ProjectResponse, ProjectUploadResponse
from app.services import project_service, file_service
from app.agents.analyzer_agent import analyze_project

router = APIRouter(prefix="/api/projects", tags=["projects"])

SAMPLE_PROJECTS_DIR = Path(__file__).parents[4] / "sample_projects"


def _to_response(project) -> ProjectResponse:
    return ProjectResponse(
        project_id=project.id,
        name=project.name,
        uploaded_at=project.uploaded_at,
        file_count=project.file_count,
        status=project.status,
        analysis=project.analysis,
    )


@router.get("/samples")
def list_sample_projects():
    """Return available bundled sample projects for instant testing."""
    samples = [
        {
            "id": "basic_calculator",
            "name": "Basic Calculator",
            "description": "Standard Java library with Calculator class, arithmetic methods, and history collections.",
            "framework": "Plain Java",
        },
        {
            "id": "employee_management",
            "name": "Employee Management Service",
            "description": "Spring Boot multi-tier app with Employee Entity, Repository, Service, and REST Controller.",
            "framework": "Spring Boot",
        },
        {
            "id": "spring_boot_rest",
            "name": "Product Catalog REST API",
            "description": "Spring Boot RESTful microservice with Product domain models, data persistence, and controller endpoints.",
            "framework": "Spring Boot + JPA",
        },
    ]
    return {"samples": samples}


@router.post("/sample/{sample_id}", response_model=ProjectUploadResponse)
def load_sample_project(sample_id: str, db: Session = Depends(get_db)):
    sample_path = SAMPLE_PROJECTS_DIR / sample_id
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample project '{sample_id}' not found.")

    display_name = sample_id.replace("_", " ").title()
    project = project_service.create_project(db, name=display_name)

    # Copy sample files into workspace/original/{project_id}
    workspace = Path("workspace") / "original" / project.id
    if workspace.exists():
        shutil.rmtree(workspace)
    shutil.copytree(sample_path, workspace)

    project.workspace_path = str(workspace)
    db.commit()

    analysis = analyze_project(workspace)
    project = project_service.save_analysis(db, project, analysis)

    return ProjectUploadResponse(
        project_id=project.id,
        name=project.name,
        message=f"Sample '{display_name}' loaded: {analysis['file_count']} Java file(s) analyzed.",
        analysis=analysis,
    )


@router.post("/upload", response_model=ProjectUploadResponse)
def upload_project(file: UploadFile = File(...), db: Session = Depends(get_db)):
    name = file.filename.rsplit(".", 1)[0] if file.filename else "unnamed-project"

    project = project_service.create_project(db, name=name)
    workspace = file_service.extract_project_zip(file, project.id)
    project.workspace_path = str(workspace)
    db.commit()

    analysis = analyze_project(workspace)
    project = project_service.save_analysis(db, project, analysis)

    return ProjectUploadResponse(
        project_id=project.id,
        name=project.name,
        message=f"Project extracted and analyzed: {analysis['file_count']} Java file(s) found.",
        analysis=analysis,
    )


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return [_to_response(p) for p in project_service.list_projects(db)]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return _to_response(project)


@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.workspace_path:
        shutil.rmtree(project.workspace_path, ignore_errors=True)
    db.delete(project)
    db.commit()
    return {"status": "deleted", "project_id": project_id}
