"""Monitoring and metrics setup."""

from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client import start_http_server

# Workflow execution metrics
workflow_executions_total = Counter(
    "workflow_executions_total", "Total number of workflow executions", ["workflow_name", "status"]
)

workflow_duration_seconds = Histogram(
    "workflow_duration_seconds",
    "Workflow execution duration in seconds",
    ["workflow_name"],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600],
)

workflow_retries_total = Counter(
    "workflow_retries_total", "Total number of workflow retries", ["workflow_name"]
)

# RSS feed metrics
rsshub_requests_total = Counter(
    "rsshub_requests_total", "Total number of RSSHub requests", ["route", "status"]
)

rsshub_request_duration_seconds = Histogram(
    "rsshub_request_duration_seconds", "RSSHub request duration in seconds", ["route"]
)

# Content filter metrics
content_filter_total = Counter(
    "content_filter_total", "Total number of content filter operations", ["filter_type", "result"]
)


def setup_monitoring(port: int = 9090):
    """Setup Prometheus monitoring."""
    start_http_server(port)
