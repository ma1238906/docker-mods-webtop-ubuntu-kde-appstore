import asyncio
from typing import AsyncGenerator, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from .settings import Settings
from .services.installer_service import InstallerManager, InstallStartError


settings = Settings.load()
app = FastAPI(title="Software Installer API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

installer_manager = InstallerManager(settings=settings)


@app.get("/api/software")
def list_software() -> Dict[str, object]:
    items = []
    for it in installer_manager.get_software_list():
        icon_path = str(it.get("icon", ""))
        icon_name = icon_path.split("/")[-1] if icon_path else ""
        icon_url = f"/static/icons/{icon_name}" if icon_name else ""
        items.append({
            "key": it.get("key"),
            "name": it.get("name", it.get("key")),
            "requires_root": bool(it.get("requires_root", True)),
            "iconUrl": icon_url,
            "installed": it.get("installed", False),
        })
    return {"items": items}


@app.post("/api/install/{key}")
async def start_install(key: str) -> Dict[str, object]:
    try:
        task_id = await installer_manager.start_install(key)
    except InstallStartError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"taskId": task_id}


@app.get("/api/install/{key}/status")
def get_status(key: str) -> Dict[str, object]:
    status = installer_manager.get_status(key)
    if status is None:
        raise HTTPException(status_code=404, detail="task not found")
    return status


@app.get("/api/install/{key}/stream")
async def stream_logs(key: str) -> StreamingResponse:
    async def generator() -> AsyncGenerator[bytes, None]:
        async for line in installer_manager.stream_output(key):
            yield f"data: {line}\n\n".encode()
        # signal end of stream (include data for better browser compatibility)
        yield b"event: end\ndata: done\n\n"

    resp = StreamingResponse(generator(), media_type="text/event-stream")
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["X-Accel-Buffering"] = "no"
    return resp


# 静态资源与前端托管
app.mount("/static", StaticFiles(directory=settings.project_root / "assets"), name="static")
app.mount("/", StaticFiles(directory=settings.project_root / "web", html=True), name="web")


def run():
    import uvicorn

    uvicorn.run(
        "server.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    run()


