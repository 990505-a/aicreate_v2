"""Workflow and execution models."""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, Text, DateTime, Integer, Float, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WorkflowStatus(str, Enum):
    """Workflow execution status."""

    idle = "idle"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class Workflow(Base):
    """Workflow definition model."""

    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    plugin_name: Mapped[str] = mapped_column(String(100))
    config_schema: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class WorkflowExecution(Base):
    """Workflow execution model."""

    __tablename__ = "workflow_executions"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    workflow_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    thread_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[WorkflowStatus] = mapped_column(String(50), default=WorkflowStatus.idle)

    # Execution configuration
    input_params: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Execution results
    output: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Progress tracking
    current_step: Mapped[Optional[str]] = mapped_column(String(200))
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    total_steps: Mapped[int] = mapped_column(Integer, default=0)

    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration: Mapped[Optional[float]] = mapped_column(Float)  # in seconds

    # Metadata
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
