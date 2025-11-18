#!/bin/bash
set -e
echo "==== Maven installation started ===="

# 1. 安装 Maven
wget -q --show-progress -O /tmp/maven.tar.gz \
    http://192.168.2.239:8081/repository/tools/maven/apache-maven-3.9.6-bin.tar.gz
tar -xzf /tmp/maven.tar.gz -C /opt
rm /tmp/maven.tar.gz
ln -sfn /opt/apache-maven-3.9.6 /opt/maven

# 2. 系统级 profile（bash/zsh 登录 Shell 会读）
cat > /etc/profile.d/maven.sh <<'EOF'
export MAVEN_HOME=/opt/maven
export PATH=$MAVEN_HOME/bin:$PATH
EOF

# 3. ****** 一次性解决「以后所有新终端」 ******
# 对 bash 交互式（非登录）也生效
tee -a /etc/bash.bashrc >/dev/null <<'EOF'
[[ -f /etc/profile.d/maven.sh ]] && source /etc/profile.d/maven.sh
EOF

# 对 zsh 交互式也生效
mkdir -p /etc/zsh
tee -a /etc/zsh/zshrc >/dev/null <<'EOF'
[[ -f /etc/profile.d/maven.sh ]] && source /etc/profile.d/maven.sh
EOF

# 4. ****** 让「当前脚本」立即能用 ******
source /etc/profile.d/maven.sh

# 5. 检验
mvn -v
echo "==== Maven installation ended ===="