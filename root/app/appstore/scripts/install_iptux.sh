
# sudo -E ./install_iptux.sh
#!/usr/bin/env bash
set -ex

# Install 飞秋
apt-get update
apt-get install -y iptux

# Desktop icon
cp /usr/share/applications/io.github.iptux_src.iptux.desktop $HOME/Desktop/
chmod +x $HOME/Desktop/io.github.iptux_src.iptux.desktop

# Cleanup for app layer
chown -R 1000:0 $HOME
find /usr/share/ -name "icon-theme.cache" -exec rm -f {} \;
if [ -z ${SKIP_CLEAN+x} ]; then
  apt-get autoclean
  rm -rf \
    /var/lib/apt/lists/* \
    /var/tmp/* \
    /tmp/*
fi