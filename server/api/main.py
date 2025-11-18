from __future__ import annotations

import os
from pathlib import Path

import uvicorn

from . import create_app


def run() -> None:
    # 默认指向 server/data，支持通过 DATA_ROOT 覆盖
    default_data = Path(__file__).resolve().parents[1] / "data"
    data_root = Path(os.environ.get("DATA_ROOT", str(default_data)))
    app = create_app(data_root=data_root)

    host = os.environ.get("SERVER_HOST", "0.0.0.0")
    port = int(os.environ.get("SERVER_PORT", "8081"))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run()


