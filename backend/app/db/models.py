"""
SQLAlchemy ORM models -- one class per table from spec section 24.

Design notes:
- UUID primary keys (as strings) so IDs generated in-memory during Phase 2/3
  (project_id, migration_id) stay valid once persisted here.
- JSON columns hold structures that don't need their own relational table yet
  (e.g. MigrationJob.progress) -- promoted to real tables if a later phase
  needs to query into them individually.
- Timestamps default to UTC now via func.now().
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    String, Integer, Boolean, ForeignKey, DateTime, JSON, Text, func
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    projects: Mapped[list["Project"]] = relationship(back_populates="owner")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    owner_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String)
    file_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="uploaded")
    workspace_path: Mapped[str | None] = mapped_column(String, nullable=True)
    analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User | None"] = relationship(back_populates="projects")
    migration_jobs: Mapped[list["MigrationJob"]] = relationship(back_populates="project")
    files: Mapped[list["ProjectFile"]] = relationship(back_populates="project")
    dependencies: Mapped[list["Dependency"]] = relationship(back_populates="project")


class MigrationJob(Base):
    __tablename__ = "migration_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    target_language: Mapped[str] = mapped_column(String)
    mode: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending")
    progress: Mapped[dict] = mapped_column(JSON, default=dict)
    repair_attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_repair_attempts: Mapped[int] = mapped_column(Integer, default=3)
    human_approval_required: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship(back_populates="migration_jobs")
    plan: Mapped["MigrationPlan | None"] = relationship(back_populates="migration_job", uselist=False)
    file_changes: Mapped[list["FileChange"]] = relationship(back_populates="migration_job")
    agent_runs: Mapped[list["AgentRun"]] = relationship(back_populates="migration_job")
    errors: Mapped[list["MigrationErrorRow"]] = relationship(back_populates="migration_job")
    repair_attempt_rows: Mapped[list["RepairAttempt"]] = relationship(back_populates="migration_job")
    test_results: Mapped[list["TestResult"]] = relationship(back_populates="migration_job")
    validation_results: Mapped[list["ValidationResult"]] = relationship(back_populates="migration_job")
    report: Mapped["Report | None"] = relationship(back_populates="migration_job", uselist=False)


class MigrationPlan(Base):
    __tablename__ = "migration_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    migration_job_id: Mapped[str] = mapped_column(ForeignKey("migration_jobs.id"), unique=True)
    steps: Mapped[dict] = mapped_column(JSON, default=dict)  # ordered list, produced by Planner Agent (Phase 13)
    complexity_estimate: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    migration_job: Mapped["MigrationJob"] = relationship(back_populates="plan")


class ProjectFile(Base):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    path: Mapped[str] = mapped_column(String)
    file_type: Mapped[str | None] = mapped_column(String, nullable=True)  # source/test/config/build

    project: Mapped["Project"] = relationship(back_populates="files")
    changes: Mapped[list["FileChange"]] = relationship(back_populates="file")


class FileChange(Base):
    __tablename__ = "file_changes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    migration_job_id: Mapped[str] = mapped_column(ForeignKey("migration_jobs.id"))
    file_id: Mapped[str | None] = mapped_column(ForeignKey("files.id"), nullable=True)
    file_path: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)  # success/partial/failed/unsupported/requires_human_review
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    agent: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence: Mapped[str | None] = mapped_column(String, nullable=True)  # low/medium/high risk

    migration_job: Mapped["MigrationJob"] = relationship(back_populates="file_changes")
    file: Mapped["ProjectFile | None"] = relationship(back_populates="changes")


class Dependency(Base):
    __tablename__ = "dependencies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String)
    version: Mapped[str | None] = mapped_column(String, nullable=True)
    target_equivalent: Mapped[str | None] = mapped_column(String, nullable=True)
    mapping_status: Mapped[str | None] = mapped_column(String, nullable=True)  # automatic/ai_assisted/unsupported/human_review

    project: Mapped["Project"] = relationship(back_populates="dependencies")


class MigrationRule(Base):
    __tablename__ = "migration_rules"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    source_pattern: Mapped[str] = mapped_column(String)   # e.g. "ArrayList<T>"
    target_language: Mapped[str] = mapped_column(String)  # python/typescript/kotlin
    target_pattern: Mapped[str] = mapped_column(String)   # e.g. "list[T]"
    category: Mapped[str | None] = mapped_column(String, nullable=True)  # type/collection/exception/...


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    migration_job_id: Mapped[str] = mapped_column(ForeignKey("migration_jobs.id"))
    agent_name: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    migration_job: Mapped["MigrationJob"] = relationship(back_populates="agent_runs")


class MigrationErrorRow(Base):
    __tablename__ = "errors"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    migration_job_id: Mapped[str] = mapped_column(ForeignKey("migration_jobs.id"))
    file_path: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    migration_job: Mapped["MigrationJob"] = relationship(back_populates="errors")


class RepairAttempt(Base):
    __tablename__ = "repair_attempts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    migration_job_id: Mapped[str] = mapped_column(ForeignKey("migration_jobs.id"))
    error_id: Mapped[str | None] = mapped_column(ForeignKey("errors.id"), nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer)
    patch_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    succeeded: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    migration_job: Mapped["MigrationJob"] = relationship(back_populates="repair_attempt_rows")


class TestResult(Base):
    __tablename__ = "test_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    migration_job_id: Mapped[str] = mapped_column(ForeignKey("migration_jobs.id"))
    passed: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    log: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    migration_job: Mapped["MigrationJob"] = relationship(back_populates="test_results")


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    migration_job_id: Mapped[str] = mapped_column(ForeignKey("migration_jobs.id"))
    status: Mapped[str] = mapped_column(String)  # SUCCESS/PARTIAL/FAILED
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    migration_job: Mapped["MigrationJob"] = relationship(back_populates="validation_results")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    migration_job_id: Mapped[str] = mapped_column(ForeignKey("migration_jobs.id"), unique=True)
    content: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    migration_job: Mapped["MigrationJob"] = relationship(back_populates="report")
