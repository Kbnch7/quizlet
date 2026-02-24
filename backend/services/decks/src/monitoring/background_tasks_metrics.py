from prometheus_client import Histogram

from .common import registry

background_task_duration_seconds = Histogram(
    "background_task_duration_seconds",
    "Background task execution time",
    ["task_type"],
    registry=registry,
)
