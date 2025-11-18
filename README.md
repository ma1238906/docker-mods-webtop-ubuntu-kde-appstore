# Ubuntu 软件安装助手

本项目为「前后端架构」的安装工具，包含两个主要组件：

- **客户端（client）**：运行在每个Ubuntu系统中的软件商店客户端，提供Web界面和软件安装功能
- **服务器（server）**：软件商店服务器，提供不同系统的软件安装资源（名称、图标、脚本等）

## 项目结构

```
.
├── client/                 # 软件商店客户端
│   ├── app/               # 应用配置
│   │   └── config.py      # 软件清单与脚本映射
│   ├── assets/            # 静态资源
│   │   └── icons/         # 图标（.png/.svg）
│   ├── scripts/           # 安装脚本（.sh）
│   ├── server/            # FastAPI 后端（托管静态与接口）
│   │   ├── main.py        # 后端入口（uvicorn）
│   │   ├── settings.py    # 配置加载
│   │   └── services/
│   │       └── installer_service.py
│   ├── web/               # 前端页面
│   │   └── index.html     # Web界面（原生 JS + SSE）
│   ├── requirements.txt   # Python依赖
│   └── Dockerfile         # 客户端Docker镜像
│
├── server/                 # 软件商店服务器（待开发）
│   ├── api/               # API接口
│   │   ├── routes/        # 路由定义
│   │   ├── models/        # 数据模型
│   │   └── services/      # 业务逻辑
│   ├── data/              # 软件资源数据
│   │   ├── software/      # 按系统分类的软件资源
│   │   └── packages/      # 软件包元数据
│   ├── static/            # 静态资源
│   ├── requirements.txt   # Python依赖
│   └── README.md          # 服务器说明文档
│
├── root/                   # 保留的旧目录结构（用于Docker构建）
│   └── app/
│       └── appstore/      # 旧的应用目录（将被client替代）
│
├── requirements.txt        # 根目录依赖（客户端使用）
├── Dockerfile              # 根目录Dockerfile（客户端使用）
├── docker-compose.yml      # Docker Compose配置
└── README.md              # 本文件
```

## 客户端功能

客户端提供以下功能：

- **软件列表展示**：显示可安装的软件，包括名称、图标、安装状态
- **软件安装**：点击安装按钮，执行安装脚本
- **实时日志**：通过SSE（Server-Sent Events）实时显示安装日志
- **安装状态检测**：自动检测软件是否已安装

### 已支持软件

- Google Chrome (`chrome`)
- VS Code (`vscode`)
- WPS (`wps`)
- VLC (`vlc`)
- Bruno (`bruno`)
- iptux (`iptux`)
- 修复软件源 (`fix_sources`)

> 你可以在 `client/app/config.py` 中调整显示名称、脚本映射与图标路径。

## 服务器功能（规划中）

服务器端将提供以下功能：

- **软件列表API**：提供可用软件列表
- **软件详情API**：提供软件详细信息（名称、图标、脚本等）
- **多系统支持**：支持Ubuntu、Debian、CentOS等不同系统
- **资源下载**：提供软件图标、安装脚本等资源的下载接口
- **版本管理**：支持软件资源的版本管理

## 环境要求

- Ubuntu 22.04+（其他发行版也可尝试，但需要 `pkexec`/`polkit`）
- Python 3.10+
- 依赖安装：

```bash
pip install -r client/requirements.txt
```

## 运行客户端

### 方式一：直接运行（推荐用于开发）

1) 安装依赖：

```bash
pip install -r client/requirements.txt
```

2) 启动后端（默认 0.0.0.0:8080）：

```bash
cd client
python3 -m server.main
```

3) 访问前端页面：

在浏览器打开 `http://<服务器>:8080/`（FastAPI 已托管 `/` 为 `web/` 目录，`/static` 为 `assets/`）。

### 方式二：使用 Docker（推荐用于生产环境）

1) 构建镜像：

```bash
docker build -t software-installer-client -f client/Dockerfile client/
```

2) 使用 docker-compose 启动（推荐）：

```bash
docker-compose up -d
```

或使用 docker 命令直接运行：

```bash
docker run -d \
  --name software-installer-client \
  --privileged \
  -p 8080:8080 \
  -v $(pwd)/client/scripts:/app/scripts:ro \
  -v $(pwd)/client/assets:/app/assets:ro \
  -v $(pwd)/client/web:/app/web:ro \
  -v $(pwd)/client/app:/app/app:ro \
  software-installer-client
```

3) 访问前端页面：

在浏览器打开 `http://localhost:8080/`。

**注意：**
- Docker 运行需要 `--privileged` 权限，以便容器内可以执行需要 root 权限的安装脚本。
- 容器内安装的软件只会影响容器自身。如需影响宿主机，请额外挂载并授权（需谨慎）。

## 放置脚本与图标

- 将安装脚本放入 `client/scripts/` 目录，建议命名：
  - `install_chrome.sh`
  - `install_vscode.sh`
  - `install_wps.sh`
  - `install_vlc.sh`
  - `install_bruno.sh`
  - `install_iptux.sh`
- 将图标放入 `client/assets/icons/` 目录，建议命名与软件 key 对应：
  - `chrome.png`, `vscode.png`, `wps.png`, `vlc.png`, `bruno.png`, `iptux.png`

你也可以修改 `client/app/config.py` 中的 `script_name` 与 `icon` 来适配自定义命名。

## 脚本规范建议

- 开头加上：`#!/usr/bin/env bash`
- 需要 root 的命令可以不写 `sudo`，程序会使用 `pkexec` 以 root 执行
- 脚本内打印关键步骤（echo），便于日志面板显示
- 正确返回退出码（0 成功，非 0 失败）

## 常见问题

- 若系统缺少 `pkexec` 或 polkit，请安装 `policykit-1`；无图形会话可能无法弹出授权框。
- 若脚本执行权限不足：

```bash
chmod +x client/scripts/*.sh
```

## 许可证

MIT
