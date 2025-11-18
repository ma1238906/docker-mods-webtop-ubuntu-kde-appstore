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
import httpx


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

    def check_installed(self, key: str, check_command: Optional[str] = None) -> bool:
        """
        动态检测软件是否已安装
        :param key: 软件key
        :param check_command: 检测命令（从服务端获取），如果为None则使用默认检测
        """
        # 如果提供了检测命令，执行它
        if check_command:
            try:
                import subprocess
                result = subprocess.run(
                    check_command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5
                )
                return result.returncode == 0
            except Exception:
                return False
        
        # 兼容旧的硬编码检测逻辑（向后兼容）
        if key == 'fix_sources':
            # 源修复只当做可用于操作，无已安装意义，返回False
            return False
        
        # 默认尝试使用 which 命令检测
        try:
            return shutil.which(key) is not None
        except Exception:
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

        # 必须从服务端获取软件信息
        base = getattr(self.settings, "resource_server_base", "")
        if not base:
            raise InstallStartError("RESOURCE_SERVER_BASE 未配置")

        os_id = _detect_os_id() or "ubuntu"
        try:
            with httpx.Client(timeout=15.0) as client:
                # 获取软件详情
                resp = client.get(f"{base}/api/v1/software/{key}", params={"os_id": os_id})
                resp.raise_for_status()
                data = resp.json()
                
                script_url = data.get("scriptUrl")
                if not script_url:
                    raise InstallStartError("远程服务端未提供 scriptUrl")
                
                requires_root = bool(data.get("requires_root", True))
                
                # 从 scriptUrl 中提取脚本文件名，或使用 key 构造
                script_filename = script_url.split("/")[-1]
                if not script_filename.endswith(".sh"):
                    # 如果 URL 中没有文件名，使用 key 构造
                    script_filename = f"{key}.sh"
                
                script_path = (self.settings.scripts_dir / script_filename).resolve()

                content = client.get(script_url, timeout=30.0).content
                self.settings.scripts_dir.mkdir(parents=True, exist_ok=True)
                script_path.write_bytes(content)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise InstallStartError(f"软件 '{key}' 在服务端不存在")
            raise InstallStartError(f"从服务端获取软件信息失败: {e}")
        except Exception as e:
            raise InstallStartError(f"获取软件信息失败: {e}")

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


def _which(cmd: str) -> Optional[str]:
    paths = os.environ.get("PATH", "").split(":")
    for p in paths:
        candidate = Path(p) / cmd
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate.as_posix()
    return None


