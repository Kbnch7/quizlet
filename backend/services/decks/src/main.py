from fastapi import FastAPI

from src.log_settings import LogLevels, configure_logging

from .api import register_routes
from .exception_handlers import register_exception_handlers
from .middlewares import register_cors_middleware

configure_logging(LogLevels.info)

app = FastAPI()

register_cors_middleware(app)

register_exception_handlers(app)
register_routes(app)
