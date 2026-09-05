"""
Generated project files browsing and content viewing endpoints.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services import migration_service

router = APIRouter(prefix="/api/files", tags=["files"])
GENERATED_ROOT = Path("workspace") / "generated"


@router.get("/{migration_id}")
def list_generated_files(migration_id: str, db: Session = Depends(get_db)):
    job = migration_service.get_migration(db, migration_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Migration not found")

    output_dir = GENERATED_ROOT / migration_id
    if not output_dir.exists():
        return {"files": [], "total": 0}

    files = []
    for f in output_dir.rglob("*"):
        if f.is_file() and not f.name.endswith(".zip"):
            rel = str(f.relative_to(output_dir)).replace("\\", "/")
            files.append({
                "path": rel,
                "name": f.name,
                "size": f.stat().st_size,
                "extension": f.suffix,
            })

    return {"files": sorted(files, key=lambda x: x["path"]), "total": len(files)}


@router.get("/{migration_id}/content")
def get_file_content(migration_id: str, path: str = Query(...), db: Session = Depends(get_db)):
    job = migration_service.get_migration(db, migration_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Migration not found")

    output_dir = GENERATED_ROOT / migration_id
    file_path = (output_dir / path).resolve()

    if not file_path.exists() or not str(file_path).startswith(str(output_dir.resolve())):
        raise HTTPException(status_code=404, detail="File not found or unsafe path")

    try:
        content = file_path.read_text(encoding="utf-8")
        return {"path": path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
