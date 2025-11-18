
# sudo -E ./install_wps.sh

#!/usr/bin/env bash
set -ex

wget -q http://192.168.2.239:8081/repository/apt-internal/pool/w/wps-office/wps-office_12.1.2.22571.AK.preread.sw_amd64.deb -O wps-office.deb

apt-get install -y ./wps-office.deb

rm ./wps-office.deb