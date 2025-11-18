# 软件商店服务器

这是软件商店的服务器端，用于提供不同系统的软件安装资源（名称、图标、脚本等）。

## 已实现

- 基本软件列表API：`GET /api/v1/software?os_id=ubuntu`
- 软件详情API：`GET /api/v1/software/{key}?os_id=ubuntu`
- 静态资源暴露：`/static` 挂载 `server/data` 目录（图标与脚本）
- **软件元数据支持**：支持通过JSON文件配置软件名称、检测命令等

示例：

```bash
curl 'http://localhost:8081/api/v1/software?os_id=ubuntu'
```

## 目录结构

```
server/
├── api/              # API接口
│   ├── routes/      # 路由定义
│   ├── models/      # 数据模型
│   └── services/    # 业务逻辑
├── data/            # 软件资源数据
│   ├── software/    # 按系统分类的软件资源
│   │   ├── ubuntu/  # Ubuntu系统软件
│   │   │   ├── scripts/    # 安装脚本 (*.sh)
│   │   │   ├── icons/      # 图标文件 (*.png, *.svg)
│   │   │   └── metadata/   # 软件元数据 (*.json)
│   │   ├── debian/  # Debian系统软件
│   │   └── centos/  # CentOS系统软件
│   └── packages/    # 软件包元数据
└── static/          # 静态资源（当前由 /static 挂载 data 目录，不必手放）
```

## 运行

两种方式，注意工作目录不同：

1) 在项目根目录运行（推荐）

```bash
pip install -r server/requirements.txt
python3 -m server.api.main  # 监听默认 0.0.0.0:8081
```

2) 在 server/ 目录内运行

```bash
cd server
pip install -r requirements.txt
python3 -m api.main
```

环境变量：
- `SERVER_HOST`（默认 `0.0.0.0`）
- `SERVER_PORT`（默认 `8081`）
- `DATA_ROOT`（默认 `server/data`）

## 添加新软件

1. **准备安装脚本**：将安装脚本放入 `data/software/<os_id>/scripts/<key>.sh`
2. **准备图标**：将图标文件放入 `data/software/<os_id>/icons/<key>.png` 或 `<key>.svg`
3. **配置元数据**（可选但推荐）：创建 `data/software/<os_id>/metadata/<key>.json`

元数据文件示例：

```json
{
  "name": "软件显示名称",
  "requires_root": true,
  "checkCommand": "which command-name"
}
```

字段说明：
- `name`: 软件显示名称（默认使用key）
- `requires_root`: 是否需要root权限（默认true）
- `checkCommand`: 检测软件是否已安装的命令（返回0表示已安装）。例如：
  - `"which google-chrome"` - 检测命令行工具
  - `"dpkg -l | grep -q package-name"` - 检测deb包
  - `"test -f /path/to/binary"` - 检测文件是否存在

## 待开发

- 版本与发行版细分（`version_id`、`arch` 过滤）

