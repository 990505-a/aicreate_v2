"""Workflow management API endpoints."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.plugin_loader import plugin_loader
from app.models.workflow import Workflow


class WorkflowStartRequest(BaseModel):
    """Request model for starting a workflow."""

    input_params: Dict[str, Any] = Field(default_factory=dict, description="Input parameters for the workflow")

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_workflows(db: AsyncSession = Depends(get_db)):
    """List all available workflows."""
    # Get plugins
    plugins = plugin_loader.list_plugins()

    # Get database workflows
    from sqlalchemy import select

    result = await db.execute(select(Workflow))
    db_workflows = result.scalars().all()

    # Combine and return
    workflows = []
    for db_workflow in db_workflows:
        plugin = plugin_loader.get_plugin(db_workflow.plugin_name)
        workflows.append(
            {
                "id": db_workflow.id,
                "name": db_workflow.name,
                "description": db_workflow.description,
                "version": db_workflow.version,
                "plugin_name": db_workflow.plugin_name,
                "is_active": db_workflow.is_active,
                "plugin_version": plugin.version if plugin else None,
                "created_at": db_workflow.created_at,
                "updated_at": db_workflow.updated_at,
            }
        )

    return workflows


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific workflow details."""
    from sqlalchemy import select

    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    plugin = plugin_loader.get_plugin(workflow.plugin_name)

    return {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "version": workflow.version,
        "plugin_name": workflow.plugin_name,
        "config_schema": plugin.get_config_schema() if plugin else {},
        "default_config": plugin.get_default_config() if plugin else {},
        "is_active": workflow.is_active,
        "created_at": workflow.created_at,
        "updated_at": workflow.updated_at,
    }


@router.post("/{workflow_id}/start")
async def start_workflow(
    workflow_id: str,
    request: WorkflowStartRequest = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """Start a workflow execution."""
    from app.services.workflow_service import WorkflowService
    from sqlalchemy import select
    from loguru import logger

    try:
        # Verify workflow exists
        result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

        if not workflow.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Workflow is not active"
            )

        # Get plugin and validate input params
        plugin = plugin_loader.get_plugin(workflow.plugin_name)
        if not plugin:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Plugin {workflow.plugin_name} not found",
            )

        # Validate input params against config schema
        schema = plugin.get_config_schema()
        input_params = request.input_params or {}

        # Merge with default config if input_params is empty or partial
        default_config = plugin.get_default_config()
        if not input_params:
            # Use all defaults if no input provided
            input_params = default_config
            logger.info(f"Using default config for workflow {workflow_id}")
        else:
            # Merge: defaults + user overrides
            merged_params = {**default_config, **input_params}
            input_params = merged_params

        # Basic validation: check required fields
        required_fields = schema.get("required", [])
        missing_fields = [field for field in required_fields if field not in input_params]
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields: {', '.join(missing_fields)}",
            )

        logger.info(f"Starting workflow {workflow_id} with params: {input_params}")

        # Start execution
        service = WorkflowService(db)
        execution_id = await service.start_execution(workflow_id, input_params)

        return {
            "message": "Workflow started",
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "running",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting workflow {workflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workflow: {str(e)}",
        )
