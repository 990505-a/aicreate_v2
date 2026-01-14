"""Initialize database with workflow plugins."""

import asyncio
from sqlalchemy import select
from loguru import logger

from app.core.database import AsyncSessionLocal
from app.core.plugin_loader import plugin_loader
from app.models.workflow import Workflow


async def init_workflows():
    """Initialize workflows from plugins."""
    async with AsyncSessionLocal() as db:
        # Discover all plugins
        plugins = plugin_loader.list_plugins()
        logger.info(f"Discovered {len(plugins)} plugins")

        for plugin_info in plugins:
            plugin_name = plugin_info["name"]

            # Check if workflow already exists
            result = await db.execute(
                select(Workflow).where(Workflow.id == plugin_name)
            )
            existing = result.scalar_one_or_none()

            if existing:
                logger.info(f"Workflow '{plugin_name}' already exists, updating...")
                existing.name = plugin_info["name"]
                existing.description = plugin_info["description"]
                existing.version = plugin_info["version"]
                existing.plugin_name = plugin_name
                existing.is_active = True
            else:
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
    logger.info("Starting workflow initialization...")
    await init_workflows()
    logger.info("Workflow initialization completed")


if __name__ == "__main__":
    asyncio.run(main())
