from fastapi import APIRouter, HTTPException, Request
from src.config import SERVICE_MAP
from src.core.proxy import forward_request

router = APIRouter()


@router.api_route(
    "/{service}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"]
)
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICE_MAP:
        raise HTTPException(404, "Service not found")
    return await forward_request(service, path, request)
