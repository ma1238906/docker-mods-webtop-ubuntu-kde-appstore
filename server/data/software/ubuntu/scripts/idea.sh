#!/bin/bash
set -e
echo "==== IDEA installation started ===="

# 0. 准备工作
IDEA_TAR=/tmp/idea.tar.gz
INSTALL_DIR=/opt/idea
BIN_LINK=/usr/local/bin/idea

# 1. 下载离线包（带重试/超时）
wget -t 3 -T 10 \
  http://192.168.2.239:8081/repository/tools/idea/ideaIC-2024.3.1.1.tar.gz \
  -O "$IDEA_TAR"

# 2. 解压到 /opt，并去掉版本号目录
tar -xzf "$IDEA_TAR" -C /opt
rm -f "$IDEA_TAR"

# 解压后目录名类似 /opt/idea-IC-243.22562.145，找出真实目录
REAL_DIR=$(find /opt -maxdepth 1 -type d -name 'idea-*' | head -n1)
mv "$REAL_DIR" "$INSTALL_DIR"

# 3. 全局可执行软链接
ln -sf "$INSTALL_DIR/bin/idea.sh" "$BIN_LINK"

# 4. 系统级 PATH 补全（可选，保险）
cat > /etc/profile.d/idea.sh <<EOF
export PATH=$INSTALL_DIR/bin:\$PATH
EOF

# 5. 立即验证
bash -lc 'type -p idea' || true

# 6. 创建桌面图标
cat >/usr/share/applications/idea.desktop <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=IntelliJ IDEA Community
Comment=IntelliJ IDEA Integrated Development Environment
Exec=/opt/idea/bin/idea.sh %f
Icon=/opt/idea/bin/idea.png
Terminal=false
StartupWMClass=jetbrains-idea
Categories=Development;IDE;
EOF

echo "==== IDEA installation ended ===="