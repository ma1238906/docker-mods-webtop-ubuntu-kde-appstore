# Ubuntu 软件安装助手（Web 前后端）

本项目为「前后端架构」的安装工具，当前项目结构已调整为以 `root/app/appstore` 为应用根：

- 后端：FastAPI 提供软件清单、启动安装、日志流（SSE）等接口。
- 前端：浏览器页面展示软件卡片，点击安装并实时显示日志。

## 已支持软件
- Google Chrome (`chrome`)
- VS Code (`vscode`)
- WPS (`wps`)
- VLC (`vlc`)
- Bruno (`bruno`)
- iptux (`iptux`)

> 你可以在 `app/config.py` 中调整显示名称、脚本映射与图标路径。

## 环境要求
- Ubuntu 22.04+（其他发行版也可尝试，但需要 `pkexec`/`polkit`）
- Python 3.10+
- 依赖安装：

```bash
pip install -r requirements.txt
```

## 目录结构（重要位置）
```
.
├─ root/
│  ├─ app/
│  │  └─ appstore/                 # 应用根目录
│  │     ├─ app/
│  │     │  └─ config.py           # 软件清单与脚本映射
│  │     ├─ assets/
│  │     │  └─ icons/              # 图标（.png/.svg）
│  │     ├─ scripts/               # 安装脚本（.sh）
│  │     ├─ server/                # FastAPI 后端（托管静态与接口）
│  │     │  ├─ main.py             # 后端入口（uvicorn）
│  │     │  ├─ settings.py         # 复用 app/config.py 的清单与路径
│  │     │  └─ services/
│  │     │     └─ installer_service.py
│  │     └─ web/
│  │        └─ index.html          # 最简网页前端（原生 JS + SSE）
│  └─ ...
│
│  └─ etc/
│     └─ s6-overlay/
│        └─ s6-rc.d/
│           └─ svc-appstore/
│              ├─ run               # s6 服务启动脚本
│              └─ type              # longrun
│
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
└─ README.md
```

## 放置脚本与图标
- 将安装脚本放入 `scripts/` 目录，建议命名：
  - `install_chrome.sh`
  - `install_vscode.sh`
  - `install_wps.sh`
  - `install_vlc.sh`
  - `install_bruno.sh`
  - `install_iptux.sh`
- 将图标放入 `assets/icons/` 目录，建议命名与软件 key 对应：
  - `chrome.png`, `vscode.png`, `wps.png`, `vlc.png`, `bruno.png`, `iptux.png`

你也可以修改 `root/app/appstore/app/config.py` 中的 `script_name` 与 `icon` 来适配自定义命名。

## 运行（Web 前后端）

### 方式一：直接运行（推荐用于开发）

1) 安装依赖：

```bash
pip install -r requirements.txt
```

2) 启动后端（默认 0.0.0.0:8080）：

```bash
cd root/app/appstore
python3 -m server.main
```

3) 访问前端页面：

在浏览器打开 `http://<服务器>:8080/`（FastAPI 已托管 `/` 为 `web/` 目录，`/static` 为 `assets/`）。

### 方式二：使用 Docker（推荐用于生产环境）

1) 构建镜像：

```bash
docker build -t software-installer .
```

2) 使用 docker-compose 启动（推荐）：

```bash
docker-compose up -d
```

或使用 docker 命令直接运行：

```bash
docker run -d \
  --name software-installer \
  --privileged \
  -p 8080:8080 \
  -v $(pwd)/root/app/appstore/scripts:/app/root/app/appstore/scripts:ro \
  -v $(pwd)/root/app/appstore/assets:/app/root/app/appstore/assets:ro \
  -v $(pwd)/root/app/appstore/web:/app/root/app/appstore/web:ro \
  -v $(pwd)/root/app/appstore/app:/app/root/app/appstore/app:ro \
  software-installer
```

3) 访问前端页面：

在浏览器打开 `http://localhost:8080/`。

**注意：**
- Docker 运行需要 `--privileged` 权限，以便容器内可以执行需要 root 权限的安装脚本。
- 容器内安装的软件只会影响容器自身。如需影响宿主机，请额外挂载并授权（需谨慎）。

## 脚本规范建议
- 开头加上：`#!/usr/bin/env bash`
- 需要 root 的命令可以不写 `sudo`，程序会使用 `pkexec` 以 root 执行
- 脚本内打印关键步骤（echo），便于日志面板显示
- 正确返回退出码（0 成功，非 0 失败）

## 常见问题
- 若系统缺少 `pkexec` 或 polkit，请安装 `policykit-1`；无图形会话可能无法弹出授权框。
- 若脚本执行权限不足：

```bash
chmod +x scripts/*.sh
```

## 许可证
MIT
