from typing import Annotated
from fastapi import APIRouter, Request, Response, Depends

from matrix_guard_api.services.matrix_auth_service import MatrixAuthService
from matrix_guard_api.services.session_service import SessionService
from matrix_guard_api.config_service import ConfigService

router = APIRouter()

@router.post("/api/session")
async def create_session(
    request: Request,
    response: Response,
    auth: Annotated[MatrixAuthService, Depends()],
    sessions: Annotated[SessionService, Depends()],
    config: Annotated[ConfigService, Depends()],
):
    body = await request.json() if await request.body() else {}

    # Token extrahieren
    if not (auth_header := request.headers.get("Authorization")):
        return Response("Missing Authorization header", status_code=401)
    token = auth_header.replace("Bearer ", "")

    # matrix_server_name aus Body holen (vom Widget mitgesendet)
    if not (matrix_server_name := body.get("matrix_server_name")):
        return Response("Missing matrix_server_name", status_code=400)

    # OpenID Token über Federation API validieren
    if not (user_id := auth.validate_openid_token(token, matrix_server_name)):
        return Response("Invalid token", status_code=401)
    if not auth.is_user_allowed(user_id):
        return Response("Forbidden", status_code=403)

    pad_name = body.get("padName")
    room_id = body.get("roomId")
    session_id = sessions.create_session(user_id, pad_name, room_id)

    response.set_cookie(
        key=config.session_cookie_name,
        value=session_id,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=int(config.session_lifetime.total_seconds()),
    )
    return {"success": True, "user_id": user_id}

@router.get("/auth")
async def auth_check(
    request: Request,
    sessions: Annotated[SessionService, Depends()],
    config: Annotated[ConfigService, Depends()],
):
    session_id = request.cookies.get(config.session_cookie_name)

    if not (session := sessions.get_session(session_id) if session_id else None):
        return Response("Unauthorized", status_code=401)

    return Response(
        "OK",
        status_code=200,
        headers={
            "X-Matrix-User-ID": session["user_id"],
            "X-Auth-User": session["user_id"],
        },
    )


@router.post("/api/logout")
async def logout(
    request: Request,
    sessions: Annotated[SessionService, Depends()],
    config: Annotated[ConfigService, Depends()],
):
    if (session_id := request.cookies.get(config.session_cookie_name)):
        sessions.destroy_session(session_id)

    return {"success": True}
