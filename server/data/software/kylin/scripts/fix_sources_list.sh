#!/usr/bin/env bash
# ------------------------------------------------------------
# 直接替换 sources.list 并禁用外部 list/source
# 用法: sudo bash replace_sources.sh
# ------------------------------------------------------------
set -euo pipefail

SOURCES="/etc/apt/sources.list"
LISTD_DIR="/etc/apt/sources.list.d"

NEW_CONTENT='deb [arch=amd64 trusted=yes] http://192.168.2.239:8081/repository/apt-internal/ weikun main
deb [arch=amd64 trusted=yes] http://192.168.2.239:8081/repository/apt-noble/ noble main restricted universe multiverse
deb [arch=amd64 trusted=yes] http://192.168.2.239:8081/repository/apt-noble-updates/ noble-updates main restricted universe multiverse
deb [arch=amd64 trusted=yes] http://192.168.2.239:8081/repository/apt-noble-security/ noble-security main restricted universe multiverse'

# 1. 直接写入新 sources.list
echo "===== 写入新 sources.list ====="
cat > "$SOURCES" <<< "$NEW_CONTENT"

# 2. 重命名 sources.list.d 下的 *.list 与 *.sources
if [[ -d "$LISTD_DIR" ]]; then
    for ext in list sources; do
        while IFS= read -r -d '' f; do
            [[ -e "${f}.bak" ]] && continue
            echo "  重命名: $(basename "$f") -> $(basename "$f").bak"
            mv "$f" "${f}.bak"
        done < <(find "$LISTD_DIR" -type f -name "*.${ext}" -print0)
    done
else
    echo "===== $LISTD_DIR 不存在，跳过 ====="
fi

# 3. 更新索引
echo "===== 执行 apt update ====="
apt update || echo "===== apt update 失败，请检查仓库配置 ====="
apt install -y wget

echo "===== 完成 ====="