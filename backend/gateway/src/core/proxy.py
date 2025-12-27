import httpx
from fastapi import Request, Response
from src.config import SERVICE_MAP, Settings

settings = Settings()


def prepare_headers(request: Request) -> dict:
    headers = dict(request.headers)

    headers.pop("host", None)
    headers.pop("Authorization", None)
    headers.pop("X-User-Id", None)
    headers.pop("X-User-Ismanager", None)
    headers.pop("X-Gateway-Auth", None)

    if hasattr(request.state, "user_id"):
        headers["X-User-Id"] = str(request.state.user_id)
        headers["X-User-Ismanager"] = str(request.state.user_is_manager)

    headers["X-Gateway-Auth"] = settings.GATEWAY_SECRET

    return headers


async def forward_request(service: str, path: str, request: Request):
    url = f"{SERVICE_MAP[service]}/api/{path}"
    headers = prepare_headers(request)
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.query_params,
            content=await request.body(),
        )

    return Response(
        content=resp.content, status_code=resp.status_code, headers=resp.headers
    )
