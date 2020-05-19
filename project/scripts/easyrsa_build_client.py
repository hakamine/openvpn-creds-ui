import logging
import os
import shlex
import subprocess
import sys


logger = logging.getLogger(__name__)


def build_client(user, password):
    # Invoke easyrsa build-client-full
    # (to generate user key and cert in the PKI)

    env = os.environ.copy()
    # need to provide the password in the variable EASYRSA_PASSOUT
    # as "pass:PASSWORD"
    env['EASYRSA_PASSOUT'] = "pass:{}".format(password)

    spr_command = env['CRUI_EASYRSA_SCRIPT']
    spr_args = "build-client-full {}".format(user)
    commstr = '{} {}'.format(spr_command, spr_args)

    print("Running: {}".format(commstr))
    logger.info("Running: {}".format(commstr))
    try:
        cp = subprocess.run(shlex.split(commstr), env=env,
                            capture_output=True, text=True,
                            cwd=env['CRUI_EASYRSA_DIR'])
    except Exception as e:
        print("Exception: {}".format(e))
        logger.error("Exception: {}".format(e))
        raise

    print("return code: {}".format(cp.returncode))
    print("stdout:\n {}".format(cp.stdout))
    print("stderr:\n {}".format(cp.stderr))
    logger.info("return code: {}".format(cp.returncode))

    return cp


if __name__ == '__main__':
    sys.exit(build_client(sys.argv[1], sys.argv[2]).returncode)
