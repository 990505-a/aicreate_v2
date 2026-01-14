"""Update database schema to use JSON type for dict fields."""

import asyncio
from sqlalchemy import text
from loguru import logger

from app.core.database import engine, AsyncSessionLocal, Base
from app.models.workflow import Workflow, WorkflowExecution


async def drop_and_recreate_tables():
    """Drop existing tables and recreate with new schema."""
    logger.info("Dropping existing tables...")

    async with engine.begin() as conn:
        # Drop tables
        await conn.execute(text("DROP TABLE IF EXISTS workflow_executions CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS workflows CASCADE"))

    logger.info("Tables dropped successfully")

    # Recreate tables with new schema
    logger.info("Recreating tables with new schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Tables recreated successfully")


async def init_workflows():
    """Re-initialize workflows from plugins."""
    from app.core.plugin_loader import plugin_loader
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        # Discover all plugins
        plugins = plugin_loader.list_plugins()
        logger.info(f"Discovered {len(plugins)} plugins")

        for plugin_info in plugins:
            plugin_name = plugin_info["name"]

            logger.info(f"Creating workflow '{plugin_name}'...")
            workflow = Workflow(
                id=plugin_name,
                name=plugin_info["name"],
                description=plugin_info["description"],
                version=plugin_info["version"],
                plugin_name=plugin_name,
                is_active=True,
            )
            db.add(workflow)

        # Commit changes
        await db.commit()
        logger.info("Workflows initialized successfully")


async def main():
    """Main entry point."""
    logger.info("Starting database schema update...")
    await drop_and_recreate_tables()
    await init_workflows()
    logger.info("Database schema update completed")


if __name__ == "__main__":
    asyncio.run(main())
