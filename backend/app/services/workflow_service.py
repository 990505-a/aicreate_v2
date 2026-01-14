"""Workflow execution service."""

import uuid
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from loguru import logger

from app.models.workflow import Workflow, WorkflowExecution, WorkflowStatus
from app.core.plugin_loader import plugin_loader
from app.api.websockets.workflow_updates import manager
from app.monitoring import (
    workflow_executions_total,
    workflow_duration_seconds,
    workflow_retries_total,
)


class WorkflowService:
    """Service for managing workflow executions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_execution(self, workflow_id: str, input_params: Dict[str, Any]) -> str:
        """Start a workflow execution."""
        execution_id = str(uuid.uuid4())
        thread_id = str(uuid.uuid4())

        # Create execution record
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow_id,
            thread_id=thread_id,
            status=WorkflowStatus.running,
            input_params=input_params,
            started_at=datetime.utcnow(),
            current_step="Initializing",
            progress=0.0,
        )

        self.db.add(execution)
        await self.db.commit()

        # Start execution in background
        asyncio.create_task(
            self._execute_workflow(execution_id, workflow_id, thread_id, input_params)
        )

        return execution_id

    async def _execute_workflow(
        self, execution_id: str, workflow_id: str, thread_id: str, input_params: Dict[str, Any]
    ):
        """Execute workflow with error handling and retry logic."""
        settings = self._get_settings()

        for retry in range(settings.workflow_max_retries):
            try:
                await self._update_execution(
                    execution_id,
                    status=WorkflowStatus.running,
                    current_step="Loading workflow plugin",
                    progress=5.0,
                )

                # Load workflow plugin
                result = await self.db.execute(select(Workflow).where(Workflow.id == workflow_id))
                workflow = result.scalar_one_or_none()

                if not workflow:
                    raise ValueError(f"Workflow not found: {workflow_id}")

                plugin = plugin_loader.get_plugin(workflow.plugin_name)
                if not plugin:
                    raise ValueError(f"Plugin not found: {workflow.plugin_name}")

                # Get LangGraph workflow
                await self._update_execution(
                    execution_id, current_step="Building workflow graph", progress=10.0
                )

                langgraph_workflow = plugin.get_workflow()

                # Merge input params with default config
                default_config = plugin.get_default_config()
                merged_params = {**default_config, **input_params}

                # Execute workflow
                await self._update_execution(
                    execution_id, current_step="Executing workflow", progress=20.0
                )

                start_time = datetime.utcnow()

                result = await langgraph_workflow.ainvoke(
                    merged_params, config={"configurable": {"thread_id": thread_id}}
                )

                # Calculate duration
                duration = (datetime.utcnow() - start_time).total_seconds()

                # Convert result to JSON-serializable format
                serializable_result = self._serialize_result(result)

                # Update execution as completed
                await self._update_execution(
                    execution_id,
                    status=WorkflowStatus.completed,
                    output=serializable_result,
                    current_step="Completed",
                    progress=100.0,
                    completed_at=datetime.utcnow(),
                    duration=duration,
                )

                # Record metrics
                workflow_executions_total.labels(
                    workflow_name=workflow.name, status="completed"
                ).inc()
                workflow_duration_seconds.labels(workflow_name=workflow.name).observe(duration)

                return

            except Exception as e:
                logger.error(f"Workflow execution failed (attempt {retry + 1}): {e}")

                if retry < settings.workflow_max_retries - 1:
                    # Update retry count and wait
                    await self._update_execution(
                        execution_id, retry_count=retry + 1, error_message=str(e)
                    )

                    workflow_retries_total.labels(workflow_name=workflow_id).inc()

                    await asyncio.sleep(settings.workflow_retry_delay)
                else:
                    # Final failure
                    await self._update_execution(
                        execution_id,
                        status=WorkflowStatus.failed,
                        error_message=str(e),
                        current_step="Failed",
                        completed_at=datetime.utcnow(),
                    )

                    workflow_executions_total.labels(
                        workflow_name=workflow_id, status="failed"
                    ).inc()

    async def _update_execution(self, execution_id: str, **updates):
        """Update execution record and broadcast changes."""
        # Update in database
        stmt = (
            update(WorkflowExecution)
            .where(WorkflowExecution.id == execution_id)
            .values(**updates, updated_at=datetime.utcnow())
        )

        await self.db.execute(stmt)
        await self.db.commit()

        # Broadcast via WebSocket
        result = await self.db.execute(
            select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
        )
        execution = result.scalar_one_or_none()

        if execution:
            await manager.broadcast_to_execution(
                execution_id,
                {
                    "type": "execution_update",
                    "execution_id": execution_id,
                    "status": execution.status,
                    "current_step": execution.current_step,
                    "progress": execution.progress,
                    "error_message": execution.error_message,
                },
            )

    async def cancel_execution(self, execution_id: str):
        """Cancel a running execution."""
        await self._update_execution(
            execution_id,
            status=WorkflowStatus.cancelled,
            current_step="Cancelled",
            completed_at=datetime.utcnow(),
        )

    def _get_settings(self):
        """Get application settings."""
        from app.core.config import get_settings

        return get_settings()

    def _serialize_result(self, result: Any) -> Dict[str, Any]:
        """Convert workflow result to JSON-serializable format."""
        from langchain_core.messages import BaseMessage

        serialized = {}
        for key, value in result.items():
            if isinstance(value, list) and value:
                # Handle lists of messages
                if hasattr(value[0], "content"):
                    serialized[key] = [
                        {
                            "type": msg.__class__.__name__,
                            "content": msg.content,
                        }
                        for msg in value
                    ]
                else:
                    serialized[key] = value
            elif isinstance(value, BaseMessage):
                # Handle single message
                serialized[key] = {
                    "type": value.__class__.__name__,
                    "content": value.content,
                }
            else:
                # Handle other types
                serialized[key] = value
        return serialized
