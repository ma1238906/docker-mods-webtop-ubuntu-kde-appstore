#!/bin/bash
set -e
echo "==== MySQL installation started ===="

# 1. 更新索引并安装
apt-get update -qq
apt-get install -y mysql-server mysql-client

# 2. 启动 & 开机自启
# 确保数据目录存在
if [ -z "$(ls -A /var/lib/mysql)" ]; then
    mysqld --initialize-insecure --user=mysql --basedir=/usr --datadir=/var/lib/mysql
fi

# 启动 MySQL 服务
service mysql start

echo "==== MySQL installation ended ===="
echo "root 用户当前使用 auth_socket 插件，无密码；"
echo "后续请手动执行 mysql_secure_installation 或 ALTER USER 设置密码。"