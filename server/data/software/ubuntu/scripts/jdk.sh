#!/bin/bash
set -e
echo "==== JDK installation started ===="

# 1. 安装 JDK
apt-get update
apt-get install -y openjdk-17-jdk

# 2. 写系统级 profile 片段
cat > /etc/profile.d/jdk17.sh <<'EOF'
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
EOF

# 3. ****** 一次性解决「以后所有新终端」 ******
# 对 bash 交互式（非登录）也生效
tee -a /etc/bash.bashrc >/dev/null <<'EOF'
[[ -f /etc/profile.d/jdk17.sh ]] && source /etc/profile.d/jdk17.sh
EOF

# 对 zsh 交互式也生效
mkdir -p /etc/zsh
tee -a /etc/zsh/zshrc >/dev/null <<'EOF'
[[ -f /etc/profile.d/jdk17.sh ]] && source /etc/profile.d/jdk17.sh
EOF

# 4. ****** 让「当前脚本」立即能用 ******
source /etc/profile.d/jdk17.sh

# 5. 检验
java -version

echo "==== JDK installation ended ===="