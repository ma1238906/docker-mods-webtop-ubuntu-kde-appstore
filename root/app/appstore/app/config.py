from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 资源与脚本目录
ASSETS_DIR = PROJECT_ROOT / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 已支持软件清单（可扩展）
SOFTWARE_LIST = [
    {
        "key": "chrome",
        "name": "Google Chrome",
        "script_name": "install_chrome.sh",
        "icon": (ICONS_DIR / "chrome.png").as_posix(),
        "requires_root": True,
    },
    {
        "key": "vscode",
        "name": "VS Code",
        "script_name": "install_vscode.sh",
        "icon": (ICONS_DIR / "vscode.png").as_posix(),
        "requires_root": True,
    },
    {
        "key": "wps",
        "name": "WPS",
        "script_name": "install_wps.sh",
        "icon": (ICONS_DIR / "wps.png").as_posix(),
        "requires_root": True,
    },
    {
        "key": "vlc",
        "name": "VLC",
        "script_name": "install_vlc.sh",
        "icon": (ICONS_DIR / "vlc.png").as_posix(),
        "requires_root": True,
    },
    {
        "key": "bruno",
        "name": "Bruno",
        "script_name": "install_bruno.sh",
        "icon": (ICONS_DIR / "bruno.png").as_posix(),
        "requires_root": True,
    },
    {
        "key": "iptux",
        "name": "iptux",
        "script_name": "install_iptux.sh",
        "icon": (ICONS_DIR / "iptux.png").as_posix(),
        "requires_root": True,
    },
    {
        "key": "fix_sources",
        "name": "修复软件源",
        "script_name": "fix_sources_list.sh",
        "icon": (ICONS_DIR / "nexus.png").as_posix(),
        "requires_root": True,
    },
]
