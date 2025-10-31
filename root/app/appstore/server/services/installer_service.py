from __future__ import annotations

import asyncio
import os
import platform
import uuid
from asyncio.subprocess import Process
from pathlib import Path
from typing import AsyncGenerator, Dict, Optional

import shutil
from ..settings import Settings


class InstallStartError(Exception):
    pass


class InstallerTask:
    def __init__(self, key: str, process: Process):
        self.key = key
        self.process = process
        self.buffer: asyncio.Queue[str] = asyncio.Queue()
        self.done_event = asyncio.Event()
        self.return_code: Optional[int] = None


class InstallerManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.key_to_task: Dict[str, InstallerTask] = {}

    @staticmethod
    def check_installed(key: str) -> bool:
        # 各软件检测逻辑，可根据需扩展
        if key == 'chrome':
            return shutil.which('google-chrome') is not None
        elif key == 'vscode':
            return shutil.which('code') is not None
        elif key == 'wps':
            return shutil.which('wps') is not None
        elif key == 'vlc':
            return shutil.which('vlc') is not None
        elif key == 'bruno':
            return shutil.which('bruno') is not None
        elif key == 'iptux':
            return shutil.which('iptux') is not None
        elif key == 'fix_sources':
            # 源修复只当做可用于操作，无已安装意义，返回False
            return False
        else:
            return False

    def get_software_list(self) -> list:
        res = []
        for item in self.settings.software_list:
            _dict = dict(item)
            key = _dict.get('key')
            _dict['installed'] = self.check_installed(key)
            res.append(_dict)
        return res

    def _find_software(self, key: str) -> Optional[dict]:
        for item in self.settings.software_list:
            if item.get("key") == key:
                return item
        return None

    async def start_install(self, key: str) -> str:
        if key in self.key_to_task:
            task = self.key_to_task[key]
            if task.return_code is None:
                # already running
                return key

        item = self._find_software(key)
        if not item:
            raise InstallStartError("unknown software key")

        script_name = item.get("script_name")
        requires_root = bool(item.get("requires_root", True))
        script_path = (self.settings.scripts_dir / script_name).resolve()
        if not script_path.exists():
            raise InstallStartError(f"script not found: {script_path}")

        try:
            mode = os.stat(script_path).st_mode
            os.chmod(script_path, mode | 0o111)
        except Exception:
            pass

        cmd = ["bash", script_path.as_posix()]

        use_pkexec = requires_root and platform.system() == "Linux"
        if use_pkexec:
            if _which("pkexec"):
                cmd = ["pkexec"] + cmd
            elif _which("sudo"):
                cmd = ["sudo", "-E", "-S"] + cmd
            else:
                raise InstallStartError("no pkexec or sudo available for privilege escalation")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(self.settings.scripts_dir),
            env=self._build_env(),
        )

        task = InstallerTask(key=key, process=process)
        self.key_to_task[key] = task

        asyncio.create_task(self._pump_output(task))
        asyncio.create_task(self._wait_return_code(task))

        return key

    def get_status(self, key: str) -> Optional[dict]:
        task = self.key_to_task.get(key)
        if not task:
            return None
        return {
            "key": key,
            "running": task.return_code is None,
            "returnCode": task.return_code,
        }

    async def stream_output(self, key: str) -> AsyncGenerator[str, None]:
        task = self.key_to_task.get(key)
        if not task:
            return
        # Drain existing buffered lines first
        while not task.buffer.empty():
            yield await task.buffer.get()
        # Then continue streaming
        while task.return_code is None or not task.buffer.empty():
            try:
                line = await asyncio.wait_for(task.buffer.get(), timeout=0.5)
                yield line
            except asyncio.TimeoutError:
                if task.return_code is not None and task.buffer.empty():
                    break

    async def _pump_output(self, task: InstallerTask) -> None:
        assert task.process.stdout is not None
        while True:
            line = await task.process.stdout.readline()
            if not line:
                break
            # asyncio subprocess 返回 bytes，需要解码为 str
            try:
                text = line.decode(errors="replace")
            except Exception:
                text = str(line)
            await task.buffer.put(text.rstrip("\n"))

    async def _wait_return_code(self, task: InstallerTask) -> None:
        rc = await task.process.wait()
        task.return_code = rc
        task.done_event.set()

    def _build_env(self) -> dict:
        env = os.environ.copy()
        env.setdefault("DEBIAN_FRONTEND", "noninteractive")
        return env


def _which(cmd: str) -> Optional[str]:
    paths = os.environ.get("PATH", "").split(":")
    for p in paths:
        candidate = Path(p) / cmd
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate.as_posix()
    return None


