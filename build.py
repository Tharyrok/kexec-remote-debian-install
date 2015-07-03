#!/usr/bin/env python
#
# Copyright (c) 2015 Catalyst.net Ltd
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import argparse
import os
import random
import shutil
import StringIO
import subprocess
import tempfile

"""
Produce an initrd image which can be used to remotely re-install Debian or Ubuntu.

Michael Fincham <michael.fincham@catalyst.net.nz>
"""

def find(root):
    for root, dirs, files in os.walk(root):
        print dirs
        print files

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('initrd', help='path to initrd.gz file to repack')
    parser.add_argument('interface', help='which interface to configure')
    parser.add_argument('address', help='IP address to configure on INTERFACE')
    parser.add_argument('netmask', help='netmask to configure on interface')
    parser.add_argument('gateway', help='default gateway to use')
    parser.add_argument('nameservers', help='space separated list of name servers to use')
    parser.add_argument('--locale', default='en_NZ.UTF-8', help='locale to use, defaults to en_NZ.UTF-8')
    parser.add_argument('--keymap', default='us', help='keyboard keymap to use, defaults to us')

    args = parser.parse_args()

    password = "".join("{:02x}".format(ord(c)) for c in open("/dev/urandom","rb").read(16))

    preseed_template = """
d-i anna/choose_modules string network-console
d-i preseed/early_command string anna-install network-console

d-i network-console/password password {password}
d-i network-console/password-again password {password}

d-i netcfg/choose_interface select {interface}
d-i netcfg/disable_dhcp boolean true
d-i netcfg/get_ipaddress string {address}
d-i netcfg/get_netmask string {netmask}
d-i netcfg/get_gateway string {gateway}
d-i netcfg/get_nameservers string {nameservers}
d-i netcfg/confirm_static boolean true

d-i debian-installer/locale string {locale}
d-i console-keymaps-at/keymap select {keymap}
    """

    preseed = preseed_template.format(
        password=password,
        interface=args.interface,
        nameservers=args.nameservers,
        address=args.address,
        netmask=args.netmask,
        gateway=args.gateway,
        locale=args.locale,
        keymap=args.keymap,
    )

    print preseed

    initrd_path = os.path.abspath(args.initrd)
    original_cwd = os.getcwd()

    working_directory = tempfile.mkdtemp()
    os.chdir(working_directory)

    with open('initrd.cpio','wb') as initrd_cpio:
        print "Unpacking initrd..."
        subprocess.check_call(("gzip -cd %s" % initrd_path).split(), stdout=initrd_cpio)

    with open('initrd.cpio','rb') as initrd_cpio:
        subprocess.check_call(("cpio -id").split(), stdin=initrd_cpio)

    print ""
    print "Re-packing initrd..."

    os.unlink('initrd.cpio')
    with open('preseed.cfg', 'w') as preseed_file:
        preseed_file.write(preseed)

    file_list = subprocess.check_output("find .".split())

    with open('initrd.cpio', 'w') as initrd_cpio:
        cpio_process = subprocess.Popen('cpio -H newc -o'.split(), stdin=subprocess.PIPE, stdout=initrd_cpio)
        cpio_process.communicate(file_list)

    with open(initrd_path,'wb') as initrd_cpio:
        subprocess.check_call("gzip -c initrd.cpio".split(), stdout=initrd_cpio)

    os.chdir(original_cwd)
    shutil.rmtree(working_directory)
