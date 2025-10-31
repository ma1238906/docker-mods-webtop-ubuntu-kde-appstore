from __future__ import annotations

import importlib.util
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

    @staticmethod
    def load() -> "Settings":
        # 动态导入现有 app.config 以复用 SOFTWARE_LIST 与 SCRIPTS_DIR
        project_root = Path(__file__).resolve().parents[1]
        app_config_path = project_root / "app" / "config.py"

        spec = importlib.util.spec_from_file_location("app_config", app_config_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("无法加载 app/config.py 以获取软件清单和脚本目录")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[arg-type]

        scripts_dir = getattr(module, "SCRIPTS_DIR")
        software_list = getattr(module, "SOFTWARE_LIST")

        allow_origins_env = os.environ.get("INSTALLER_CORS_ORIGINS", "*")
        cors_allow_origins = (
            [o.strip() for o in allow_origins_env.split(",") if o.strip()] if allow_origins_env else ["*"]
        )

        host = os.environ.get("INSTALLER_HOST", "0.0.0.0")
        port = int(os.environ.get("INSTALLER_PORT", "8080"))

        return Settings(
            host=host,
            port=port,
            cors_allow_origins=cors_allow_origins,
            project_root=project_root,
            scripts_dir=Path(scripts_dir),
            software_list=software_list,
        )


