
# sudo -E ./install_bruno.sh

#!/usr/bin/env bash
set -ex

wget -q http://192.168.2.239:8081/repository/apt-internal/pool/b/bruno/bruno_2.13.2_amd64.deb -O bruno.deb

apt-get install -y ./bruno.deb

sudo sed -i 's|Exec=/opt/Bruno/bruno|Exec=/opt/Bruno/bruno --no-sandbox|' /usr/share/applications/bruno.desktop

rm ./bruno.deb