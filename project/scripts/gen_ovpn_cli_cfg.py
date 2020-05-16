#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This script creates an openvpn client config file for the
# specified username, with all the information included
# (CA, client cert/key, auth key)
# It has been tested to work on:
#   - linux: openvpn
#   - macOS: tunnelblick

from io import BytesIO
import os
import sys


def main(arguments):
    vpnconfig = BytesIO()
    rc = 0

    if len(arguments) != 4:
        sys.stderr.write("must specify the following arguments: <username> <easyrsa_pki_dir> <base_cfg_file> <ta_key>")
        return rc, vpnconfig
    username = arguments[0]
    EASYRSA_PKI_DIR = arguments[1]
    BASE_CONFIG_FILE = arguments[2]
    TA_KEY_FILE = arguments[3]

    # check all the files required exist
    try:
        base_config_file = open(BASE_CONFIG_FILE, "rb")
        ca_file = open(os.path.join(EASYRSA_PKI_DIR, "ca.crt"), "rb")
        cli_cert_file = open(
            os.path.join(EASYRSA_PKI_DIR, "issued", "{}.crt".format(username)), "rb"
        )
        cli_key_file = open(
            os.path.join(EASYRSA_PKI_DIR, "private", "{}.key".format(username)), "rb"
        )
        ta_key_file = open(TA_KEY_FILE, "rb")
    except IOError as e:
        sys.stderr.write("Error when trying to open input files: {}\n".format(e))
        return rc, vpnconfig.getvalue()

    # write configuration to stdout
    try:
        # add base config
        vpnconfig.write(base_config_file.read())
        # add CA
        vpnconfig.write(b"\n<ca>\n")
        vpnconfig.write(ca_file.read())
        vpnconfig.write(b"</ca>\n\n")
        # add client cert
        vpnconfig.write(b"<cert>\n")
        vpnconfig.write(cli_cert_file.read())
        vpnconfig.write(b"</cert>\n\n")
        # add client key
        vpnconfig.write(b"<key>\n")
        vpnconfig.write(cli_key_file.read())
        vpnconfig.write(b"</key>\n\n")
        # add ta key
        vpnconfig.write(b"<tls-auth>\n")
        vpnconfig.write(ta_key_file.read())
        vpnconfig.write(b"</tls-auth>\n")

        return rc, vpnconfig.getvalue()

    except Exception as e:
        sys.stderr.write("Error: {}\n".format(e))
        return rc, vpnconfig.getvalue()


if __name__ == "__main__":
    # if called from command line, output config to stdout
    rc, vpncfg = main(sys.argv[1:])
    if rc == 0:
        sys.stdout.write(vpncfg.decode("utf-8"))
    sys.exit(rc)
