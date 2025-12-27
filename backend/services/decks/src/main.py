from fastapi import FastAPI

from src.log_settings import LogLevels, configure_logging

from .api import register_routes
from .exception_handlers import register_exception_handlers

configure_logging(LogLevels.info)

app = FastAPI(docs_url="/api/docs")

register_exception_handlers(app)
register_routes(app)
