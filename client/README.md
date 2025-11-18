# 软件商店客户端

这是软件商店的客户端部分，运行在每个Ubuntu系统中，提供Web界面和软件安装功能。

## 功能

- **软件列表展示**：显示可安装的软件，包括名称、图标、安装状态
- **软件安装**：点击安装按钮，执行安装脚本
- **实时日志**：通过SSE（Server-Sent Events）实时显示安装日志
- **安装状态检测**：自动检测软件是否已安装

## 目录结构

```
client/
├── assets/            # 静态资源
│   └── icons/         # 图标（.png/.svg，已迁移到服务端）
├── scripts/           # 安装脚本目录（脚本会从服务端自动下载）
├── server/            # FastAPI 后端（托管静态与接口）
│   ├── main.py        # 后端入口（uvicorn）
│   ├── settings.py    # 配置加载
│   └── services/
│       └── installer_service.py
├── web/               # 前端页面
│   └── index.html     # Web界面（原生 JS + SSE）
├── etc/               # s6-overlay 服务配置
│   └── s6-overlay/s6-rc.d/svc-appstore/
│       ├── run        # 服务启动脚本
│       └── type       # 服务类型（longrun）
├── config/            # 持久化配置目录（Docker 挂载）
├── requirements.txt   # Python依赖
└── Dockerfile         # Docker镜像定义（基于 webtop:ubuntu-kde）
```

## 运行

### 直接运行（开发）

```bash
pip install -r requirements.txt
python3 -m server.main
```

### Docker运行

客户端基于 `lscr.io/linuxserver/webtop:ubuntu-kde` 镜像，使用 s6-overlay 管理服务。

#### 构建镜像

```bash
cd client
docker build -t software-installer-client .
```

#### 运行容器

```bash
docker run -d \
  --name software-installer-client \
  --privileged \
  -p 8080:8080 \
  -v $(pwd)/config:/config \
  -e RESOURCE_SERVER_BASE=http://your-server:8081 \
  software-installer-client
```

#### 使用 docker-compose（推荐）

在项目根目录运行：

```bash
docker-compose up -d software-installer-client
```

**重要环境变量：**
- `RESOURCE_SERVER_BASE`: 软件商店服务器地址（必需）
- `INSTALLER_HOST`: 监听地址（默认 0.0.0.0）
- `INSTALLER_PORT`: 监听端口（默认 8080）

**注意：**
- 服务通过 s6-overlay 自动启动，无需手动指定 CMD
- 虚拟环境会持久化到 `/config/.venv` 目录
- 需要 `--privileged` 权限以执行需要 root 权限的安装脚本

