#!/bin/bash
set -e
echo "==== PyCharm installation started ===="

# 0. 准备工作
PYCHARM_TAR=/tmp/pycharm.tar.gz
INSTALL_DIR=/opt/pycharm
BIN_LINK=/usr/local/bin/pycharm

# 1. 下载离线包（带重试/超时）
wget -t 3 -T 10 \
  http://192.168.2.239:8081/repository/tools/pycharm/pycharm-community-2024.3.5.tar.gz \
  -O "$PYCHARM_TAR"

# 2. 先清空旧目录（若存在）
rm -rf "$INSTALL_DIR"
# 解压到 /opt，去掉版本号目录
tar -xzf "$PYCHARM_TAR" -C /opt
rm -f "$PYCHARM_TAR"

# 找出真实目录（例如 pycharm-community-2024.3.5）
REAL_DIR=$(find /opt -maxdepth 1 -type d -name 'pycharm-*' | head -n1)
mv "$REAL_DIR" "$INSTALL_DIR"          # 固定路径 /opt/pycharm

# 3. 全局可执行软链接
ln -sf "$INSTALL_DIR/bin/pycharm.sh" "$BIN_LINK"

# 4. 系统级 PATH 补全（可选）
cat > /etc/profile.d/pycharm.sh <<EOF
export PATH=$INSTALL_DIR/bin:\$PATH
EOF

# 5. 立即验证
bash -lc 'type -p pycharm' || true

# 6. 创建桌面图标
cat >/usr/share/applications/pycharm.desktop <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=PyCharm Community
Comment=PyCharm Integrated Development Environment
Exec=/opt/pycharm/bin/pycharm.sh %f
Icon=/opt/pycharm/bin/pycharm.png
Terminal=false
StartupWMClass=jetbrains-pycharm
Categories=Development;IDE;
EOF

echo "==== PyCharm installation ended ===="