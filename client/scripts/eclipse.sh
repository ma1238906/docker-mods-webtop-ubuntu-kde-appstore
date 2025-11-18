#!/bin/bash
set -e
echo "==== Eclipse-Platform 安装开始 ===="

# 0. 安装目录和下载链接（可改）
INSTALL_DIR=/opt/eclipse
DESKTOP_FILE=/usr/share/applications/eclipse.desktop
ECLIPSE_URL="https://download.eclipse.org/eclipse/downloads/drops4/R-4.32-202409030240/eclipse-platform-4.32-linux-gtk-x86_64.tar.gz"

# 1. 清理旧残留 ➜ 防止“cannot overwrite”报错
rm -rf "$INSTALL_DIR"

# 2. 下载并解压到临时目录
TMP=$(mktemp -d)
wget -q -t 3 -T 10 -O "$TMP/eclipse.tar.gz" "$ECLIPSE_URL"
tar -xzf "$TMP/eclipse.tar.gz" -C "$TMP"        # 得到 $TMP/eclipse/

# 3. 移动到最终位置
mv "$TMP/eclipse" "$INSTALL_DIR"
rm -rf "$TMP"

# 4. 全局命令 & 桌面入口
ln -sf "$INSTALL_DIR/eclipse" /usr/local/bin/eclipse

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Eclipse Platform
Comment=Eclipse Platform Runtime
Exec=$INSTALL_DIR/eclipse %f
Icon=$INSTALL_DIR/icon.xpm
Terminal=false
StartupWMClass=Eclipse
Categories=Development;IDE;
EOF

update-desktop-database /usr/share/applications || true

# 5. 验证
bash -lc 'type -p eclipse' || true
echo "==== Eclipse-Platform 安装完成 ===="