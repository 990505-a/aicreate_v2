"""Plugin system for extensible workflows."""

from typing import Dict, Type, Optional, List
from importlib import import_module
from pathlib import Path
from loguru import logger
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()


class WorkflowPlugin(BaseModel):
    """Base class for workflow plugins."""

    name: str
    version: str
    description: str
    author: str = "Unknown"

    def get_workflow(self):
        """Get the LangGraph workflow for this plugin."""
        raise NotImplementedError("Plugin must implement get_workflow()")

    def get_config_schema(self) -> dict:
        """Get the configuration schema for this workflow."""
        return {}

    def get_default_config(self) -> dict:
        """Get default configuration values."""
        return {}


class PluginLoader:
    """Plugin loader for discovering and loading workflow plugins."""

    def __init__(self, plugins_path: Optional[str] = None):
        self.plugins_path = Path(plugins_path or "app/plugins")
        self._plugins: Dict[str, WorkflowPlugin] = {}
        self._loaded = False

    def discover_plugins(self) -> Dict[str, Type[WorkflowPlugin]]:
        """Discover all workflow plugins in the plugins directory."""
        plugins = {}

        if not self.plugins_path.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_path}")
            return plugins

        for plugin_file in self.plugins_path.glob("*_plugin.py"):
            plugin_name = plugin_file.stem.replace("_plugin", "")
            try:
                module = import_module(f"app.plugins.{plugin_file.stem}")
                if hasattr(module, "Plugin"):
                    plugins[plugin_name] = module.Plugin
                    logger.info(f"Discovered plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_name}: {e}")

        return plugins

    def load_plugin(self, plugin_name: str) -> Optional[WorkflowPlugin]:
        """Load a specific plugin by name."""
        if not self._loaded:
            self._load_all_plugins()

        return self._plugins.get(plugin_name)

    def _load_all_plugins(self):
        """Load all discovered plugins."""
        plugin_classes = self.discover_plugins()

        for name, plugin_class in plugin_classes.items():
            try:
                plugin_instance = plugin_class()
                self._plugins[name] = plugin_instance
                logger.info(f"Loaded plugin: {name} v{plugin_instance.version}")
            except Exception as e:
                logger.error(f"Failed to instantiate plugin {name}: {e}")

        self._loaded = True

    def list_plugins(self) -> List[Dict[str, str]]:
        """List all loaded plugins with metadata."""
        if not self._loaded:
            self._load_all_plugins()

        return [
            {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "author": plugin.author,
            }
            for plugin in self._plugins.values()
        ]

    def get_plugin(self, plugin_name: str) -> Optional[WorkflowPlugin]:
        """Get a loaded plugin by name."""
        return self.load_plugin(plugin_name)

    def reload_plugins(self):
        """Reload all plugins."""
        self._plugins = {}
        self._loaded = False
        self._load_all_plugins()
        logger.info("All plugins reloaded")


# Global plugin loader instance
plugin_loader = PluginLoader()
