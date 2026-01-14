"""Workflow execution API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.workflow import WorkflowExecution, WorkflowStatus

router = APIRouter()


@router.get("/")
async def list_executions(
    workflow_id: str = Query(None),
    status: WorkflowStatus = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List workflow executions with optional filters."""
    from sqlalchemy import select, and_

    # Build query
    conditions = []
    if workflow_id:
        conditions.append(WorkflowExecution.workflow_id == workflow_id)
    if status:
        conditions.append(WorkflowExecution.status == status)

    query = select(WorkflowExecution)
    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(WorkflowExecution.created_at.desc())
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    executions = result.scalars().all()

    return [
        {
            "id": exec.id,
            "workflow_id": exec.workflow_id,
            "status": exec.status,
            "current_step": exec.current_step,
            "progress": exec.progress,
            "started_at": exec.started_at,
            "completed_at": exec.completed_at,
            "duration": exec.duration,
            "error_message": exec.error_message,
            "created_at": exec.created_at,
        }
        for exec in executions
    ]


@router.get("/{execution_id}")
async def get_execution(execution_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific execution details."""
    from sqlalchemy import select

    result = await db.execute(select(WorkflowExecution).where(WorkflowExecution.id == execution_id))
    execution = result.scalar_one_or_none()

    if not execution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found")

    return {
        "id": execution.id,
        "workflow_id": execution.workflow_id,
        "thread_id": execution.thread_id,
        "status": execution.status,
        "input_params": execution.input_params,
        "config": execution.config,
        "output": execution.output,
        "error_message": execution.error_message,
        "current_step": execution.current_step,
        "progress": execution.progress,
        "total_steps": execution.total_steps,
        "started_at": execution.started_at,
        "completed_at": execution.completed_at,
        "duration": execution.duration,
        "retry_count": execution.retry_count,
        "created_at": execution.created_at,
        "updated_at": execution.updated_at,
    }


@router.post("/{execution_id}/cancel")
async def cancel_execution(execution_id: str, db: AsyncSession = Depends(get_db)):
    """Cancel a running execution."""
    from sqlalchemy import select
    from app.services.workflow_service import WorkflowService

    result = await db.execute(select(WorkflowExecution).where(WorkflowExecution.id == execution_id))
    execution = result.scalar_one_or_none()

    if not execution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found")

    if execution.status not in [WorkflowStatus.idle, WorkflowStatus.running]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel execution in current state",
        )

    # Cancel execution
    service = WorkflowService(db)
    await service.cancel_execution(execution_id)

    return {"message": "Execution cancelled"}
