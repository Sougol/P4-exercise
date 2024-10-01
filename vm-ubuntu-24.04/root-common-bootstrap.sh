#!/bin/bash

# Print commands and exit on errors
set -xe

useradd -m -d /home/p4 -s /bin/bash p4
echo "p4:p4" | chpasswd
echo "p4 ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/99_p4
chmod 440 /etc/sudoers.d/99_p4
usermod -aG vboxsf p4

# Install p4 logo as wallpaper
mv /home/vagrant/p4-logo.png /usr/share/lxqt/wallpapers/lxqt-default-wallpaper.png
