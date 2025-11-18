from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Settings:
    host: str
    port: int
    cors_allow_origins: List[str]
    project_root: Path
    scripts_dir: Path
    software_list: list
    resource_server_base: str

    @staticmethod
    def load() -> "Settings":
        # 直接计算项目根目录和脚本目录，不再依赖 app.config
        project_root = Path(__file__).resolve().parents[1]
        scripts_dir = project_root / "scripts"

        allow_origins_env = os.environ.get("INSTALLER_CORS_ORIGINS", "*")
        cors_allow_origins = (
            [o.strip() for o in allow_origins_env.split(",") if o.strip()] if allow_origins_env else ["*"]
        )

        host = os.environ.get("INSTALLER_HOST", "0.0.0.0")
        port = int(os.environ.get("INSTALLER_PORT", "8080"))

        resource_server_base = os.environ.get("RESOURCE_SERVER_BASE", "").rstrip("/")

        return Settings(
            host=host,
            port=port,
            cors_allow_origins=cors_allow_origins,
            project_root=project_root,
            scripts_dir=scripts_dir,
            software_list=[],  # 不再使用本地软件列表，所有软件信息从服务端获取
            resource_server_base=resource_server_base,
        )


