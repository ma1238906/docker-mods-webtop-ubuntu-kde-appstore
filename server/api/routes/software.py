from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi import Request


router = APIRouter()


def _build_base_url(request: Request) -> str:
    scheme = request.url.scheme
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    if not host:
        # Fallback to netloc from request.url
        host = request.url.netloc
    return f"{scheme}://{host}"


def _load_software_metadata(os_dir: Path, key: str) -> Dict[str, object]:
    """加载软件元数据文件（JSON），如果存在的话"""
    metadata_file = os_dir / "metadata" / f"{key}.json"
    if metadata_file.exists():
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _list_software_items(data_root: Path, os_id: str) -> List[Dict[str, object]]:
    os_dir = data_root / "software" / os_id
    if not os_dir.exists():
        return []

    # 支持以每个软件一个目录或一个json的形式；此处实现简单目录扫描：
    # - 脚本目录: data/software/<os>/scripts/<key>.sh
    # - 图标目录: data/software/<os>/icons/<key>.(png|svg)
    # - 元数据目录: data/software/<os>/metadata/<key>.json (可选)
    scripts_dir = os_dir / "scripts"
    icons_dir = os_dir / "icons"

    items: List[Dict[str, object]] = []
    if scripts_dir.exists():
        for script_path in scripts_dir.glob("*.sh"):
            key = script_path.stem
            icon_file: Optional[Path] = None
            for ext in ("png", "svg"):
                candidate = icons_dir / f"{key}.{ext}"
                if candidate.exists():
                    icon_file = candidate
                    break

            # 加载元数据（如果存在）
            metadata = _load_software_metadata(os_dir, key)
            
            item = {
                "key": key,
                "name": metadata.get("name", key),  # 优先使用元数据中的名称
                "requires_root": metadata.get("requires_root", True),
                "checkCommand": metadata.get("checkCommand"),  # 安装检测命令
                # icon/script URL 在handler中补全
                "_script_rel": f"/static/software/{os_id}/scripts/{script_path.name}",
                "_icon_rel": f"/static/software/{os_id}/icons/{icon_file.name}" if icon_file else "",
            }
            items.append(item)

    return items


@router.get("")
def list_software(request: Request, os_id: str = Query("ubuntu")) -> Dict[str, object]:
    data_root = Path(request.app.state.data_root)
    base = _build_base_url(request)
    items = _list_software_items(data_root, os_id)

    # 将相对URL转为绝对URL，方便客户端直接引用
    result: List[Dict[str, object]] = []
    for it in items:
        icon_rel = it.pop("_icon_rel", "")
        script_rel = it.pop("_script_rel", "")
        it["iconUrl"] = f"{base}{icon_rel}" if icon_rel else ""
        it["scriptUrl"] = f"{base}{script_rel}" if script_rel else ""
        result.append(it)

    return {"items": result}


@router.get("/{key}")
def get_software(request: Request, key: str, os_id: str = Query("ubuntu")) -> Dict[str, object]:
    data_root = Path(request.app.state.data_root)
    base = _build_base_url(request)
    items = _list_software_items(data_root, os_id)
    for it in items:
        if it.get("key") == key:
            icon_rel = it.pop("_icon_rel", "")
            script_rel = it.pop("_script_rel", "")
            it["iconUrl"] = f"{base}{icon_rel}" if icon_rel else ""
            it["scriptUrl"] = f"{base}{script_rel}" if script_rel else ""
            return it
    raise HTTPException(status_code=404, detail="not found")


