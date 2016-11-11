import sys
import os
import tempfile
import shutil
import subprocess
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

MY_DIR = os.path.dirname(__file__)
ROOT = os.path.dirname(MY_DIR)
PIP_REQUIRES = os.path.join(MY_DIR, 'pip-requires')
PIP_REQUIRES_TEST = os.path.join(MY_DIR, 'pip-requires-test')


def die(message, *args):
    print >> sys.stderr, message % args
    sys.exit(1)


def download(url, to_path):
    print 'Downloading %s into %s' % (url, to_path)
    req = urlopen(url)
    with open(to_path, 'wb') as fp:
        for line in req:
            fp.write(line)
    return to_path


def run_command(cmd, redirect_output=True, check_exit_code=True, shell=False, prefix=None):
    """
    Runs a command in an out-of-process shell, returning the
    output of that command.  Working directory is ROOT.
    """
    if prefix:
        cmd.append("--prefix=" + prefix)
    if shell:
        cmd = ['sh', '-c', cmd]
    proc = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE if redirect_output else None)
    output = proc.communicate()[0]
    if check_exit_code and proc.returncode != 0:
        # print("ec = %d " % proc.returncode)
        die('Command "%s" failed.\n%s', ' '.join(cmd), output)
    return output


def install_deps(has_setup=False, has_pip=False, prefix=None):
    tempdir = tempfile.mkdtemp()
    try:
        if not has_setup:
            run_command([sys.executable, download("https://bootstrap.pypa.io/ez_setup.py",
                                                  os.path.join(tempdir, "ez_setup.py"))])
        if not has_pip:
            run_command([sys.executable, download("https://bootstrap.pypa.io/get-pip.py",
                                                  os.path.join(tempdir, "get-pip.py"))])

        print 'Installing dependencies with pip (this can take a while)...'

        cmd = [sys.executable, '-m', 'pip', 'install', '-r', PIP_REQUIRES]
        if prefix:
            cmd.append("--prefix="+prefix)
        run_command(cmd, redirect_output=False)

        cmd = [sys.executable, '-m', 'pip', 'install', '-r', PIP_REQUIRES_TEST]
        if prefix:
            cmd.append("--prefix="+prefix)
        run_command(cmd, redirect_output=False)
    finally:
        shutil.rmtree(tempdir)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--has_setup",  action='store_true')
    parser.add_argument("--has_pip",  action='store_true')
    parser.add_argument("--prefix", default=None, type=lambda x: x if os.path.isdir(x) else None)
    arg = parser.parse_args(sys.argv[1:])

    install_deps(arg.has_setup, arg.has_pip, arg.prefix)
