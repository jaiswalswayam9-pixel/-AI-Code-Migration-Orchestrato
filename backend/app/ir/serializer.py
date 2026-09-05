"""
IR <-> JSON convenience wrappers. Thin on purpose -- Pydantic already
does the real work; this just gives callers (routes, storage) one
place to import from rather than reaching into pydantic directly.
"""
import json
from app.ir.models import IRProject


def ir_to_dict(project: IRProject) -> dict:
    return project.model_dump()


def ir_to_json(project: IRProject, indent: int | None = None) -> str:
    return project.model_dump_json(indent=indent)


def ir_from_dict(data: dict) -> IRProject:
    return IRProject.model_validate(data)


def ir_from_json(text: str) -> IRProject:
    return IRProject.model_validate(json.loads(text))
