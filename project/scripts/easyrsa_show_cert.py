import os
import shlex
import subprocess
import sys


def show_cert(user):
    # Invoke easyrsa show-cert, returning its returncode
    # (0 if could return the cert info, 1 otherwise)

    env = os.environ.copy()

    spr_command = env['CRUI_EASYRSA_SCRIPT']
    spr_args = "show-cert {}".format(user)
    commstr = '{} {}'.format(spr_command, spr_args)

    print("Running: {}".format(commstr))
    try:
        cp = subprocess.run(shlex.split(commstr), env=env,
                            capture_output=True, text=True,
                            cwd=env['CRUI_EASYRSA_DIR'])
    except Exception as e:
        print("Exception: {}".format(e))
        raise

    print("retcode:\n {}".format(cp.returncode))
    print("stdout:\n {}".format(cp.stdout))
    print("stderr:\n {}".format(cp.stderr))

    return cp


if __name__ == '__main__':
    sys.exit(show_cert(sys.argv[1:]).returncode)
