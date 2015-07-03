# kexec-remote-debian-install

Work in progress tools to remotely re-install Debian or Ubuntu using kexec and SSH.

## build.py

Before running `build.py` you will need a `linux` and `initrd.gz` file from the installer of the distro you prefer.

* Ubuntu Trusty AMD64 http://linux.citylink.co.nz/ubuntu/dists/trusty/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64/
* Debian Jessie AMD64 http://linux.citylink.co.nz/debian/dists/jessie/main/installer-amd64/current/images/netboot/debian-installer/amd64/

Currently `build.py` must be run as root, as it unpacks the cpio archive and re-packs it, and this allows the permissions of various device files to be preserved. 

    sudo ./build.py initrd.gz eth0 172.16.0.4 255.255.255.0 172.16.0.1 8.8.8.8

    d-i anna/choose_modules string network-console
    d-i preseed/early_command string anna-install network-console

    d-i network-console/password password c96f4ef5edef6a2daa7b63eb81db5f66
    d-i network-console/password-again password c96f4ef5edef6a2daa7b63eb81db5f66

    d-i netcfg/choose_interface select eth0
    d-i netcfg/disable_dhcp boolean true
    d-i netcfg/get_ipaddress string 172.16.0.4
    d-i netcfg/get_netmask string 255.255.255.0
    d-i netcfg/get_gateway string 172.16.0.1
    d-i netcfg/get_nameservers string 8.8.8.8
    d-i netcfg/confirm_static boolean true

    d-i debian-installer/locale string en_NZ.UTF-8
    d-i console-keymaps-at/keymap select us
        
    Unpacking initrd...
    105824 blocks

    Re-packing initrd...
    105825 blocks

Once `initrd.gz` has been re-packed the new kernel can be launched:

    kexec --command-line="auto=true priority=critical" --initrd=initrd.gz linux

Once the machine has booted the new kernel, the installer will be available over SSH on the IP address given on the command line, with the username `installer` and the password shown during the build output.
