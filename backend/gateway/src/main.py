from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from src.auth.service import extract_bearer_token, get_user_by_token
from src.routers.proxy import router as proxy_router

app = FastAPI()

app.include_router(proxy_router)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    auth = request.headers.get("Authorization")
    token = extract_bearer_token(auth)

    if token:
        try:
            user = await get_user_by_token(token)
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )

        request.state.user_id = user.id
        request.state.user_is_manager = user.is_manager

    return await call_next(request)
