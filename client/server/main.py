import asyncio
from typing import AsyncGenerator, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

import platform
import httpx
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


def _detect_os_id() -> str:
    try:
        with open("/etc/os-release", "r", encoding="utf-8") as f:
            content = f.read()
        for line in content.splitlines():
            if line.startswith("ID="):
                return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return platform.system().lower()


@app.get("/api/software")
def list_software() -> Dict[str, object]:
    base = settings.resource_server_base
    if not base:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="RESOURCE_SERVER_BASE 未配置")

    os_id = _detect_os_id() or "ubuntu"
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(f"{base}/api/v1/software", params={"os_id": os_id})
        resp.raise_for_status()
        data = resp.json()

    # 填充安装状态，使用服务端提供的检测命令
    enriched = []
    for item in data.get("items", []):
        key = item.get("key")
        check_command = item.get("checkCommand")
        item["installed"] = installer_manager.check_installed(key, check_command)
        enriched.append(item)
    return {"items": enriched}


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


