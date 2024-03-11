# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "bento/ubuntu-20.04-arm64"

  config.vm.provider "vmware_desktop" do |v|
    v.gui = true
  end

  config.vm.synced_folder '.', '/vagrant', disabled: true
  config.vm.hostname = "p4"
  config.vm.provision "file", source: "p4-logo.png",   destination: "/home/vagrant/p4-logo.png"
  config.vm.provision "file", source: "p4_16-mode.el", destination: "/home/vagrant/p4_16-mode.el"
  config.vm.provision "file", source: "p4.vim",        destination: "/home/vagrant/p4.vim"

  config.vm.define "dev-arm", primary: true do |dev|
    dev.vm.provider "vmware_desktop" do |v|
      v.vmx['displayname'] = "P4 Tutorial Development" + Time.now.strftime(" %Y-%m-%d")
    end
    dev.vm.provision "file", source: "py3localpath.py", destination: "/home/vagrant/py3localpath.py"
    dev.vm.provision "shell", inline: "chmod 755 /home/vagrant/py3localpath.py"
    dev.vm.provision "file", source: "patches/disable-Wno-error-and-other-small-changes.diff", destination: "/home/vagrant/patches/disable-Wno-error-and-other-small-changes.diff"
    dev.vm.provision "file", source: "patches/behavioral-model-use-correct-libssl-pkg.patch", destination: "/home/vagrant/patches/behavioral-model-use-correct-libssl-pkg.patch"
    dev.vm.provision "file", source: "patches/mininet-dont-install-python2-2022-apr.patch", destination: "/home/vagrant/patches/mininet-dont-install-python2-2022-apr.patch"
    dev.vm.provision "file", source: "clean.sh", destination: "/home/vagrant/clean.sh"
    dev.vm.provision "shell", inline: "chmod 755 /home/vagrant/clean.sh"
    dev.vm.provision "shell", path: "arm/root-dev-bootstrap_arm.sh"
    dev.vm.provision "shell", path: "arm/root-common-bootstrap_arm.sh"
    dev.vm.provision "shell", privileged: false, path: "user-dev-bootstrap.sh"
    dev.vm.provision "shell", privileged: false, path: "user-common-bootstrap.sh"
  end
end
