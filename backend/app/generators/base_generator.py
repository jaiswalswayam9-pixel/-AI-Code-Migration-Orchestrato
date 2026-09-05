"""
Generator interface (spec section 44 -- extensibility requirement).
Adding a new target language later means implementing this interface
and adding a rule file; nothing in the orchestrator or IR changes.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from app.ir.models import IRProject

FileStatus = Literal["success", "partial", "failed", "unsupported", "requires_human_review"]


@dataclass
class GeneratedFile:
    path: str            # relative path within the generated project
    content: str
    status: FileStatus
    notes: list[str] = field(default_factory=list)


class BaseLanguageGenerator(ABC):
    language: str
    file_extension: str

    @abstractmethod
    def generate_project(self, ir: IRProject, output_dir: Path) -> list[GeneratedFile]:
        """Writes the generated project to output_dir and returns the
        per-file results (spec section 35 status categories)."""
        raise NotImplementedError
