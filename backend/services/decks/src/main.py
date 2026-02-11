import time

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.log_settings import LogLevels, configure_logging

from .api import register_routes
from .exception_handlers import register_exception_handlers
from .monitoring.api_metrics import (
    api_calls_total,
    http_errors_4xx_total,
    http_errors_5xx_total,
    http_request_duration_seconds,
    http_requests_total,
)
from .monitoring.common import registry

configure_logging(LogLevels.info)

app = FastAPI(docs_url="/api/docs")

register_exception_handlers(app)
register_routes(app)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    route = request.scope.get("route")
    if route and hasattr(route, "path"):
        endpoint = route.path
    else:
        endpoint = request.url.path

    method = request.method
    status_code = str(response.status_code)

    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status_code=status_code,
    ).inc()

    http_request_duration_seconds.labels(
        method=method,
        endpoint=endpoint,
    ).observe(duration)

    if endpoint.startswith("/api/"):
        parts = endpoint.split("/")
        api_type = parts[2] if len(parts) > 2 else "unknown"
        api_calls_total.labels(api_type=api_type).inc()

    status = response.status_code
    if 400 <= status < 500:
        http_errors_4xx_total.labels(
            endpoint=endpoint,
            status_code=status_code,
        ).inc()
    elif status >= 500:
        http_errors_5xx_total.labels(
            endpoint=endpoint,
            status_code=status_code,
        ).inc()

    return response


@app.get("/metrics")
async def metrics():
    return PlainTextResponse(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
