#!/bin/bash

# Print script commands and exit on errors.
set -xe

PYTHON_VENV="${HOME}/p4dev-python-venv"
source "${PYTHON_VENV}/bin/activate"

# --- Mininet --- #
# Mininet install needs either distutils or packaging Python packages
# to be installed.  distutils is deprecated, and removed in Python
# 3.12, which is the default Python version on Ubuntu 24.04, so
# install packaging instead.
pip3 install packaging
MININET_COMMIT="5b1b376336e1c6330308e64ba41baac6976b6874"  # 2023-May-28
git clone https://github.com/mininet/mininet mininet
cd mininet
git checkout ${MININET_COMMIT}
PATCH_DIR="${HOME}/patches"
patch -p1 < "${PATCH_DIR}/mininet-patch-for-2023-jun-enable-venv.patch"
cd ..
RESTORE_SUDOERS_FILE=0
if [ -e /etc/sudoers.d/sudoers-dotfiles ]
then
    # Some Ubuntu 24.04 systems have a sudo configuration file that
    # disallows passing environment variables such as DEBIAN_FRONTEND
    # on a sudo command line for apt-get commands.  On such systems,
    # temporarily rename this configuration file while installing
    # Mininet, since Mininet's install script uses this feature of
    # sudo.
    sudo mv /etc/sudoers.d/sudoers-dotfiles /etc/sudoers.d/sudoers-dotfiles.orig
    RESTORE_SUDOERS_FILE=1
fi
PYTHON=python3 ./mininet/util/install.sh -nw
if [ ${RESTORE_SUDOERS_FILE} -eq 1 ]
then
    sudo mv /etc/sudoers.d/sudoers-dotfiles.orig /etc/sudoers.d/sudoers-dotfiles
fi

find /usr/lib /usr/local $HOME/.local | sort > $HOME/usr-local-7-after-mininet-install.txt

# --- Copy Python3 venv --- #
# Remove any compiled .pyc files, since they might contain references
# to soon-to-be-obsolete paths.
find ${PYTHON_VENV} -name '*.pyc' | xargs rm
# Replace all occurrences of /home/vagrant with /home/p4 in files soon
# to be moved.
/bin/cp -pr ${PYTHON_VENV} tmp-venv-to-move
find tmp-venv-to-move ! -type d | xargs grep --files-with-matches /home/vagrant | xargs sed -i 's-/home/vagrant-/home/p4-'
sudo mv tmp-venv-to-move /home/p4/p4dev-python-venv
sudo chown -R p4:p4 /home/p4/p4dev-python-venv

# --- Copy mininet source --- #
# This is useful because the mininet Python package installation that
# we just copied above contains references to directory
# /home/vagrant/mininet, which we have just changed above to
# /home/p4/mininet
/bin/cp -pr mininet mininet-to-move
sudo mv mininet-to-move /home/p4/mininet
sudo chown -R p4:p4 /home/p4/mininet

# --- environment variable setup for user p4 --- #
cd $HOME
cp /dev/null p4setup.bash
echo "source /home/p4/p4dev-python-venv/bin/activate" >> p4setup.bash
echo "export P4GUIDE_SUDO_OPTS=\"PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python\"" >> p4setup.bash
sudo mv p4setup.bash /home/p4/p4setup.bash
sudo chown p4:p4 /home/p4/p4setup.bash
echo "source /home/p4/p4setup.bash" | sudo tee -a /home/p4/.bashrc

# --- environment variable setup for user vagrant --- #
cd $HOME
cp /dev/null p4setup.bash
echo "source /home/vagrant/p4dev-python-venv/bin/activate" >> p4setup.bash
echo "export P4GUIDE_SUDO_OPTS=\"PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python\"" >> p4setup.bash
echo "source /home/vagrant/p4setup.bash" | tee -a /home/vagrant/.bashrc

# --- Tutorials --- #
git clone https://github.com/p4lang/tutorials
cd tutorials
PATCH_DIR="${HOME}/patches"
patch -p1 < "${PATCH_DIR}/tutorials-support-venv.patch"
cd ..
sudo mv tutorials /home/p4
sudo chown -R p4:p4 /home/p4/tutorials

# --- Emacs --- #
sudo cp p4_16-mode.el /usr/share/emacs/site-lisp/
sudo mkdir /home/p4/.emacs.d/
echo "(autoload 'p4_16-mode' \"p4_16-mode.el\" \"P4 Syntax.\" t)" > init.el
echo "(add-to-list 'auto-mode-alist '(\"\\.p4\\'\" . p4_16-mode))" | tee -a init.el
sudo mv init.el /home/p4/.emacs.d/
sudo ln -s /usr/share/emacs/site-lisp/p4_16-mode.el /home/p4/.emacs.d/p4_16-mode.el
sudo chown -R p4:p4 /home/p4/.emacs.d/

# --- Vim --- #
cd ~
mkdir .vim
cd .vim
mkdir ftdetect
mkdir syntax
echo "au BufRead,BufNewFile *.p4      set filetype=p4" >> ftdetect/p4.vim
echo "set bg=dark" >> ~/.vimrc
sudo mv ~/.vimrc /home/p4/.vimrc
cp ~/p4.vim syntax/p4.vim
cd ~
sudo mv .vim /home/p4/.vim
sudo chown -R p4:p4 /home/p4/.vim
sudo chown p4:p4 /home/p4/.vimrc

# --- Adding Desktop icons --- #
DESKTOP=/home/${USER}/Desktop
mkdir -p ${DESKTOP}

cat > ${DESKTOP}/Terminal.desktop << EOF
[Desktop Entry]
Encoding=UTF-8
Type=Application
Name=Terminal
Name[en_US]=Terminal
Icon=konsole
Exec=/usr/bin/x-terminal-emulator
Comment[en_US]=
EOF

cat > ${DESKTOP}/Wireshark.desktop << EOF
[Desktop Entry]
Encoding=UTF-8
Type=Application
Name=Wireshark
Name[en_US]=Wireshark
Icon=wireshark
Exec=/usr/bin/wireshark
Comment[en_US]=
EOF

sudo mkdir -p /home/p4/Desktop
sudo mv /home/${USER}/Desktop/* /home/p4/Desktop
sudo chown -R p4:p4 /home/p4/Desktop/

# Do this last!
sudo reboot
