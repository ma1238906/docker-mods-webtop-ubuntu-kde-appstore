#!/bin/bash
set -e
echo "==== Conda installation started ===="

# 1. 下载离线包（带重试/超时）
wget -t 3 -T 10 \
  http://192.168.2.239:8081/repository/tools/miniconda/Miniconda3-py312_25.9.1-3-Linux-x86_64.sh \
  -O /tmp/miniconda.sh

# 2. 统一安装路径
INSTALL_PREFIX=/opt/miniconda
bash /tmp/miniconda.sh -b -p "$INSTALL_PREFIX"
rm -f /tmp/miniconda.sh

# 3. 生成系统级 profile 片段（固定路径，无变量）
cat > /etc/profile.d/conda.sh <<EOF
export PATH=$INSTALL_PREFIX/bin:\$PATH
EOF

# 4. 对交互式 bash/zsh 也生效
tee -a /etc/bash.bashrc >/dev/null <<'EOF'
[[ -f /etc/profile.d/conda.sh ]] && source /etc/profile.d/conda.sh
EOF

mkdir -p /etc/zsh
tee -a /etc/zsh/zshrc >/dev/null <<'EOF'
[[ -f /etc/profile.d/conda.sh ]] && source /etc/profile.d/conda.sh
EOF

echo "==== Conda installation ended ===="