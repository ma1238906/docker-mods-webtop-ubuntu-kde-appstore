from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .routes import api_router


def create_app(data_root: Path) -> FastAPI:
    app = FastAPI(title="Software Store Server", version="1.0.0")
    app.include_router(api_router, prefix="/api/v1")

    # 挂载静态资源，暴露 data 目录（只读）
    app.state.data_root = str(data_root)
    app.mount("/static", StaticFiles(directory=data_root, html=False), name="static")
    return app


