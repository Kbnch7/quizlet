from fastapi import FastAPI
from .api import register_routes
from .exception_handlers import register_exception_handlers
from src.log_settings import configure_logging, LogLevels

configure_logging(LogLevels.info)

app = FastAPI()

register_exception_handlers(app)
register_routes(app)
