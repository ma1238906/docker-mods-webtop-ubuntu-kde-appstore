# sudo -E ./install_vscode.sh

#!/usr/bin/env bash
set -ex

# Install vsCode
wget -q http://192.168.2.239:8081/repository/apt-internal/pool/c/code/code_1.105.1-1760482543_amd64.deb -O vs_code.deb
# apt-get update
apt-get install -y ./vs_code.deb

rm ./vs_code.deb

sed -i 's#/usr/share/code/code#/usr/share/code/code --no-sandbox##' /usr/share/applications/code.desktop