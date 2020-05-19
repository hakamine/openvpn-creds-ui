#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This script creates an openvpn client config file for the
# specified username, with all the information included
# (CA, client cert/key, auth key)
# It has been tested to work on:
#   - linux: openvpn
#   - macOS: tunnelblick

from io import BytesIO
import logging
import os
import shlex
import subprocess
import sys


logger = logging.getLogger(__name__)


def cat_to_bytesio(cat_cmd, file_path):

    commstr = '{} {}'.format(cat_cmd, file_path)

    print("Running: {}".format(commstr))
    logger.info("Running: {}".format(commstr))
    try:
        cp = subprocess.run(shlex.split(commstr),
                            capture_output=True,
                            )
    except Exception as e:
        print("Exception: {}".format(e))
        logger.error("Error: {}".format(e))
        raise

    if cp.returncode != 0:
        print("Error: command return code is not 0")
        logger.error("Error: command return code is not 0")
        raise

    return BytesIO(cp.stdout)


def main(arguments):
    vpnconfig = BytesIO()
    rc = 0

    if len(arguments) != 5:
        sys.stderr.write("must specify the following arguments: <username> <easyrsa_pki_dir> <base_cfg_file> <ta_key> <cat command>")
        logger.error("Incorrect number of arguments")
        rc = -1
        return rc, vpnconfig
    username = arguments[0]
    EASYRSA_PKI_DIR = arguments[1]
    BASE_CONFIG_FILE = arguments[2]
    TA_KEY_FILE = arguments[3]
    cat_cmd = arguments[4]

    # check all the files required exist
    # note that the app user may not have permissions to see some of these files
    # such as the ones in PKI dir unless using sudo
    try:

        base_config_file = cat_to_bytesio(cat_cmd, BASE_CONFIG_FILE)
        ta_key_file = cat_to_bytesio(cat_cmd, TA_KEY_FILE)
        ca_file = cat_to_bytesio(cat_cmd, os.path.join(EASYRSA_PKI_DIR, "ca.crt"))
        cli_cert_file = cat_to_bytesio(cat_cmd, os.path.join(EASYRSA_PKI_DIR, "issued", "{}.crt".format(username)))
        cli_key_file = cat_to_bytesio(cat_cmd, os.path.join(EASYRSA_PKI_DIR, "private", "{}.key".format(username)))

    except Exception as e:
        sys.stderr.write("Error when trying to open input files: {}\n".format(e))
        logger.error("Error when trying to open input files: {}".format(e))
        rc = -2
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
        logger.error("Exception: {}".format(e))
        rc = -3
        return rc, vpnconfig.getvalue()


if __name__ == "__main__":
    # if called from command line, output config to stdout
    rc, vpncfg = main(sys.argv[1:])
    if rc == 0:
        sys.stdout.write(vpncfg.decode("utf-8"))
    sys.exit(rc)
