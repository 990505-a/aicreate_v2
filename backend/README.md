# AICreate Workflow Platform - Backend

High-availability intelligent workflow platform built with LangGraph, LangChain, and DeepAgents.

## Quick Start

### Prerequisites

- Python 3.13
- PostgreSQL 15+
- Redis 7+

### Installation

```bash
# Install dependencies with uv
uv pip install --system -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
```

### Configuration

Edit `.env` file:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/aicreate

# LLM Providers
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### Running the Application

```bash
# Development mode with auto-reload
python -m app.main

# Or with uvicorn directly
uvicorn app.main:app --reload
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── v1/         # REST API v1
│   │   └── websockets/ # WebSocket endpoints
│   ├── core/           # Core functionality (config, database, plugins)
│   ├── models/         # Database models
│   ├── services/       # Business logic services
│   ├── tools/          # LangChain tools
│   ├── workflows/      # LangGraph workflows
│   ├── plugins/        # Workflow plugins
│   └── utils/         # Utility functions
├── tests/              # Test suites
├── migrations/         # Database migrations
└── pyproject.toml     # Project dependencies
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Plugin Development

Create a new workflow plugin:

```python
from app.core.plugin_loader import WorkflowPlugin
from langgraph.graph import StateGraph

class MyWorkflowPlugin(WorkflowPlugin):
    def __init__(self):
        super().__init__(
            name="my_workflow",
            version="1.0.0",
            description="My custom workflow"
        )

    def get_workflow(self):
        workflow = StateGraph(dict)
        # Add nodes and edges
        return workflow.compile()
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```
