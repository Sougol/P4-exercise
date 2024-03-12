# P4 Assignment

This assignment will help you get familiar with some of the 
main concepts and constructs of the P4 programming language.

## Obtaining required software

To complete the exercises, you will need to either build a
virtual machine using 'vagrant' or use the GCP VM.

To build the virtual machine using 'vagrant':
- Install [VirtualBox](https://virtualbox.org)
  > **Apple Silicon Users**: Follow this [guide](./Readme-arm.md)
- Install [Vagrant](https://vagrantup.com)
- Clone the repository
- Before proceeding, ensure that your system has at least 12 Gbytes of free disk space, otherwise, the installation can fail in unpredictable ways.
- `cd vm-ubuntu-20.04`
- `vagrant up` - The time for this step to complete depends upon your computer and Internet access speeds, but for example with a 2015 MacBook Pro and 50 Mbps download speed, it took a little less than 20 minutes.  It requires a reliable Internet connection throughout the entire process.
- When the machine reboots, you should have a graphical desktop machine with the required software pre-installed.  There are two user accounts on the VM, `vagrant` (password `vagrant`) and `p4` (password `p4`).  The account `p4` is the one you are expected to use.
- Clone this repository in `$HOME`.

*Note*: Before running the `vagrant up` command, make sure you have enabled virtualization in your environment; otherwise you may get a "VT-x is disabled in the BIOS for both all CPU modes" error. Check [this](https://stackoverflow.com/questions/33304393/vt-x-is-disabled-in-the-bios-for-both-all-cpu-modes-verr-vmx-msr-all-vmx-disabl) for enabling it in VirtualBox and/or BIOS for different system configurations.

You will need the script to execute to completion before you can see the `p4` login on your virtual machine's GUI. In some cases, the `vagrant up` command brings up only the default `vagrant` login with the password `vagrant`. Dependencies may or may not have been installed for you to proceed with running P4 programs. Please refer to the [existing issues](https://github.com/p4lang/tutorials/issues) to help fix your problem or create a new one if your specific problem isn't addressed there.

To use the GCP image:
- You can get the students' credit through email. (You need to email me your Gmail account (e.g. sougol@gmail.com) with the title "[SDNCourse]-GCP".)
- There is an intro to GCP in the Canvas that walks you through building a VM with a prebuilt image. (Modules -> Tools)

## P4 Documentation and Extra Resources

The documentation for P4_16 and P4Runtime is available [here](https://p4.org/specs/)

All exercises in this repository use the v1model architecture, the documentation for which is available at:
1. The BMv2 Simple Switch target document accessible [here](https://github.com/p4lang/behavioral-model/blob/master/docs/simple_switch.md) talks mainly about the v1model architecture.
2. The include file `v1model.p4` has extensive comments and can be accessed [here](https://github.com/p4lang/p4c/blob/master/p4include/v1model.p4).

There are also some slides from a P4 tutorial event and a P4 Cheat Sheet in the repository that you can feel free to refer to as you are completing the assignment.
