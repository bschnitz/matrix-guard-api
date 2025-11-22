from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from matrix_guard_api.endpoints.auth import router as auth_router
from matrix_guard_api.config_service import ConfigService

app = FastAPI()

# Config via DI, also nicht global benutzen — nur hier für CORS sinnvoll
config = ConfigService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


def start():
    """Entry point for `python -m matrix_guard_api.main`"""
    import uvicorn
    uvicorn.run("matrix_guard_api.main:app", host="0.0.0.0", port=8080, reload=False)


if __name__ == "__main__":
    start()
