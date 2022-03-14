#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import shlex
import subprocess


logger = logging.getLogger(__name__)


def main(cat_cmd, file_path):

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

    return cp.stdout

