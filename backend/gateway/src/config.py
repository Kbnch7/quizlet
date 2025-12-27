# SERVICE MAP, PUBLIC PATHS

import os


class Settings:
    ALGORITHM = os.getenv("ALGORITHM")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")
    GATEWAY_SECRET = os.getenv("GATEWAY_SECRET")


SERVICE_MAP = {
    "auth": os.getenv("AUTH_SERVICE_URL"),
    "decks": os.getenv("DECKS_SERVICE_URL"),
    "teaching": os.getenv("TEACHING_SERVICE_URL"),
}
